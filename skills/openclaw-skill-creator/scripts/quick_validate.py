#!/usr/bin/env python3
"""
Quick validation script for OpenClaw skills - validates against the AgentSkills spec
plus OpenClaw-specific requirements (single-line metadata JSON, gating fields, etc.)
"""

import json
import re
import sys
from pathlib import Path
from typing import Optional

try:
    import yaml
except ModuleNotFoundError:
    yaml = None

MAX_SKILL_NAME_LENGTH = 64

# Standard AgentSkills fields plus OpenClaw extensions
ALLOWED_PROPERTIES = {
    "name", "description", "license", "allowed-tools", "compatibility", "metadata",
    # OpenClaw-specific
    "user-invocable", "disable-model-invocation",
    "command-dispatch", "command-tool", "command-arg-mode",
    "homepage",
}

VALID_OPENCLAW_KEYS = {
    "requires", "primaryEnv", "always", "emoji", "homepage", "os", "install", "skillKey",
}

VALID_REQUIRES_KEYS = {"bins", "anyBins", "env", "config"}

VALID_OS_VALUES = {"darwin", "linux", "win32"}


def _extract_frontmatter(content: str) -> Optional[str]:
    lines = content.splitlines()
    if not lines or lines[0].strip() != "---":
        return None
    for i in range(1, len(lines)):
        if lines[i].strip() == "---":
            return "\n".join(lines[1:i])
    return None


def _parse_simple_frontmatter(frontmatter_text: str) -> Optional[dict[str, str]]:
    """
    Minimal fallback parser used when PyYAML is unavailable.
    Supports simple `key: value` mappings used by SKILL.md frontmatter.
    """
    parsed: dict[str, str] = {}
    current_key: Optional[str] = None
    for raw_line in frontmatter_text.splitlines():
        stripped = raw_line.strip()
        if not stripped or stripped.startswith("#"):
            continue

        is_indented = raw_line[:1].isspace()
        if is_indented:
            if current_key is None:
                return None
            current_value = parsed[current_key]
            parsed[current_key] = (
                f"{current_value}\n{stripped}" if current_value else stripped
            )
            continue

        if ":" not in stripped:
            return None
        key, value = stripped.split(":", 1)
        key = key.strip()
        value = value.strip()
        if not key:
            return None
        if (value.startswith('"') and value.endswith('"')) or (
            value.startswith("'") and value.endswith("'")
        ):
            value = value[1:-1]
        parsed[key] = value
        current_key = key
    return parsed


def _validate_metadata_openclaw(metadata_value) -> list[str]:
    """Validate OpenClaw-specific metadata fields. Returns list of warnings/errors."""
    issues = []

    # metadata must be parseable as JSON (single-line requirement)
    if isinstance(metadata_value, str):
        try:
            metadata_obj = json.loads(metadata_value)
        except json.JSONDecodeError as e:
            issues.append(f"metadata is not valid JSON: {e}")
            return issues
    elif isinstance(metadata_value, dict):
        metadata_obj = metadata_value
    else:
        issues.append(f"metadata must be a JSON object or string, got {type(metadata_value).__name__}")
        return issues

    if "openclaw" not in metadata_obj:
        return issues  # No openclaw block, nothing to validate

    oc = metadata_obj["openclaw"]
    if not isinstance(oc, dict):
        issues.append("metadata.openclaw must be an object")
        return issues

    # Check for unknown keys
    unknown_keys = set(oc.keys()) - VALID_OPENCLAW_KEYS
    if unknown_keys:
        issues.append(f"Unknown keys in metadata.openclaw: {', '.join(sorted(unknown_keys))}")

    # Validate requires
    if "requires" in oc:
        req = oc["requires"]
        if not isinstance(req, dict):
            issues.append("metadata.openclaw.requires must be an object")
        else:
            unknown_req = set(req.keys()) - VALID_REQUIRES_KEYS
            if unknown_req:
                issues.append(f"Unknown keys in requires: {', '.join(sorted(unknown_req))}")
            for key in ("bins", "anyBins", "env", "config"):
                if key in req:
                    if not isinstance(req[key], list):
                        issues.append(f"requires.{key} must be an array")
                    elif not all(isinstance(v, str) for v in req[key]):
                        issues.append(f"requires.{key} must contain only strings")

    # Validate primaryEnv
    if "primaryEnv" in oc:
        primary = oc["primaryEnv"]
        if not isinstance(primary, str):
            issues.append("primaryEnv must be a string")
        elif "requires" in oc and "env" in oc["requires"]:
            if primary not in oc["requires"]["env"]:
                issues.append(
                    f"primaryEnv '{primary}' is not listed in requires.env "
                    f"({oc['requires']['env']}). Users won't be able to set it via apiKey config."
                )

    # Validate os
    if "os" in oc:
        os_list = oc["os"]
        if not isinstance(os_list, list):
            issues.append("os must be an array")
        else:
            invalid_os = [v for v in os_list if v not in VALID_OS_VALUES]
            if invalid_os:
                issues.append(f"Invalid os values: {invalid_os}. Valid: {sorted(VALID_OS_VALUES)}")

    # Validate always
    if "always" in oc and oc["always"] is not True:
        issues.append("metadata.openclaw.always should be true (or omit it)")

    # Validate install
    if "install" in oc:
        installs = oc["install"]
        if not isinstance(installs, list):
            issues.append("install must be an array")
        else:
            for i, inst in enumerate(installs):
                if not isinstance(inst, dict):
                    issues.append(f"install[{i}] must be an object")
                elif "kind" not in inst:
                    issues.append(f"install[{i}] missing 'kind' field")

    return issues


def _check_metadata_single_line(frontmatter_text: str) -> Optional[str]:
    """Check that metadata is on a single line (OpenClaw parser requirement)."""
    in_metadata = False
    metadata_lines = 0
    for line in frontmatter_text.splitlines():
        stripped = line.strip()
        if stripped.startswith("metadata:"):
            in_metadata = True
            metadata_lines = 1
            # Check if value is on the same line
            value_part = stripped[len("metadata:"):].strip()
            if value_part:
                # Value is inline — check if it's complete (valid JSON)
                try:
                    json.loads(value_part)
                    return None  # Valid single-line metadata
                except json.JSONDecodeError:
                    pass  # Might be multi-line or invalid
        elif in_metadata and line[:1].isspace():
            metadata_lines += 1
        elif in_metadata:
            break

    if in_metadata and metadata_lines > 1:
        return (
            "metadata spans multiple lines. OpenClaw's parser requires metadata "
            "to be a single-line JSON object. Collapse it to one line."
        )
    return None


def validate_skill(skill_path):
    """Validate an OpenClaw skill."""
    skill_path = Path(skill_path)

    skill_md = skill_path / "SKILL.md"
    if not skill_md.exists():
        return False, "SKILL.md not found"

    try:
        content = skill_md.read_text(encoding="utf-8")
    except OSError as e:
        return False, f"Could not read SKILL.md: {e}"

    frontmatter_text = _extract_frontmatter(content)
    if frontmatter_text is None:
        return False, "Invalid frontmatter format"

    # Check single-line metadata requirement (OpenClaw-specific)
    metadata_line_issue = _check_metadata_single_line(frontmatter_text)
    if metadata_line_issue:
        return False, metadata_line_issue

    if yaml is not None:
        try:
            frontmatter = yaml.safe_load(frontmatter_text)
            if not isinstance(frontmatter, dict):
                return False, "Frontmatter must be a YAML dictionary"
        except yaml.YAMLError as e:
            return False, f"Invalid YAML in frontmatter: {e}"
    else:
        frontmatter = _parse_simple_frontmatter(frontmatter_text)
        if frontmatter is None:
            return (
                False,
                "Invalid YAML in frontmatter: unsupported syntax without PyYAML installed",
            )

    unexpected_keys = set(frontmatter.keys()) - ALLOWED_PROPERTIES
    if unexpected_keys:
        allowed = ", ".join(sorted(ALLOWED_PROPERTIES))
        unexpected = ", ".join(sorted(unexpected_keys))
        return (
            False,
            f"Unexpected key(s) in SKILL.md frontmatter: {unexpected}. Allowed properties are: {allowed}",
        )

    if "name" not in frontmatter:
        return False, "Missing 'name' in frontmatter"
    if "description" not in frontmatter:
        return False, "Missing 'description' in frontmatter"

    name = frontmatter.get("name", "")
    if not isinstance(name, str):
        return False, f"Name must be a string, got {type(name).__name__}"
    name = name.strip()
    if name:
        if not re.match(r"^[a-z0-9-]+$", name):
            return (
                False,
                f"Name '{name}' should be hyphen-case (lowercase letters, digits, and hyphens only)",
            )
        if name.startswith("-") or name.endswith("-") or "--" in name:
            return (
                False,
                f"Name '{name}' cannot start/end with hyphen or contain consecutive hyphens",
            )
        if len(name) > MAX_SKILL_NAME_LENGTH:
            return (
                False,
                f"Name is too long ({len(name)} characters). "
                f"Maximum is {MAX_SKILL_NAME_LENGTH} characters.",
            )

    description = frontmatter.get("description", "")
    if not isinstance(description, str):
        return False, f"Description must be a string, got {type(description).__name__}"
    description = description.strip()
    if description:
        if "<" in description or ">" in description:
            return False, "Description cannot contain angle brackets (< or >)"
        if len(description) > 1024:
            return (
                False,
                f"Description is too long ({len(description)} characters). Maximum is 1024 characters.",
            )

    compatibility = frontmatter.get("compatibility", "")
    if compatibility and isinstance(compatibility, str):
        if len(compatibility.strip()) > 500:
            return (
                False,
                f"Compatibility is too long ({len(compatibility.strip())} characters). Maximum is 500 characters.",
            )

    # Validate OpenClaw metadata if present
    warnings = []
    if "metadata" in frontmatter:
        metadata_issues = _validate_metadata_openclaw(frontmatter["metadata"])
        for issue in metadata_issues:
            if "Unknown keys" in issue or "not listed in requires.env" in issue:
                warnings.append(f"[WARN] {issue}")
            else:
                return False, issue

    # Validate command-dispatch consistency
    if frontmatter.get("command-dispatch") == "tool":
        if "command-tool" not in frontmatter:
            return False, "command-dispatch: tool requires command-tool to be set"

    # Validate user-invocable and disable-model-invocation are booleans
    for bool_field in ("user-invocable", "disable-model-invocation"):
        if bool_field in frontmatter:
            val = frontmatter[bool_field]
            if not isinstance(val, bool) and val not in ("true", "false"):
                return False, f"{bool_field} must be true or false, got '{val}'"

    result_msg = "Skill is valid!"
    if warnings:
        result_msg += "\n" + "\n".join(warnings)

    return True, result_msg


if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python quick_validate.py <skill_directory>")
        sys.exit(1)

    valid, message = validate_skill(sys.argv[1])
    print(message)
    sys.exit(0 if valid else 1)
