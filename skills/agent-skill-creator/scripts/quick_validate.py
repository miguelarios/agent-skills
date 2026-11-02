#!/usr/bin/env python3
"""
Validate a skill against the Agent Skills spec (https://agentskills.io/specification).

Usage:
    quick_validate.py <skill-dir> [--target default|claude-ai|spec]

Targets:
    default    Spec violations are errors. Non-spec top-level frontmatter keys
               are WARNINGS that name the runtime that reads them.
    claude-ai  Same as spec: claude.ai uploads, the Skills API and Anthropic's
               package_skill.py hard-reject unknown top-level keys, so they are
               errors. (package_skill.py --target claude-ai strips them.)
    spec       Strict spec: non-spec top-level keys are errors.

Exit codes:
    0  valid (warnings may be printed)
    1  one or more errors
    2  usage error
"""

import argparse
import re
import sys
from pathlib import Path
from typing import Optional

try:
    import yaml
except ModuleNotFoundError:
    yaml = None

MAX_SKILL_NAME_LENGTH = 64


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
        if value in {"|", "|-", "|+", ">", ">-", ">+"}:
            value = ""
        elif (value.startswith('"') and value.endswith('"')) or (
            value.startswith("'") and value.endswith("'")
        ):
            value = value[1:-1]
        parsed[key] = value
        current_key = key
    return parsed


def _validate_description_scalar(frontmatter_text: str) -> Optional[str]:
    """Reject YAML-unsafe plain descriptions before selecting a parser."""
    for raw_line in frontmatter_text.splitlines():
        if raw_line[:1].isspace() or ":" not in raw_line:
            continue

        key, raw_value = raw_line.split(":", 1)
        if key.strip() != "description":
            continue

        value = raw_value.strip()
        if not value or value[0] in {"|", ">"}:
            return None

        # A leading quote means a quoted scalar, which may continue onto later
        # lines (multi-line quoted descriptions are valid YAML).
        is_quoted = value[0] in {'"', "'"}
        if not is_quoted and ": " in value:
            return (
                "Description contains an unquoted ': ' sequence, which breaks YAML "
                "frontmatter. Quote the entire description, use a block scalar, or "
                "rewrite the sentence without ': '."
            )
        return None

    return None



SPEC_KEYS = {"name", "description", "license", "compatibility", "metadata", "allowed-tools"}
TARGETS = ("default", "claude-ai", "spec")

# Non-spec top-level keys we recognise -> who reads them.
CLAUDE_CODE_KEYS = {
    "when_to_use", "argument-hint", "arguments", "disable-model-invocation",
    "user-invocable", "disallowed-tools", "model", "effort", "context",
    "agent", "background", "hooks",
}
HERMES_KEYS = {"required_environment_variables", "platforms", "required_credential_files", "prerequisites"}
# Keys people often put at top level that belong under metadata.
METADATA_HINT_KEYS = {"version", "author", "tags", "related_skills", "category", "homepage"}


def key_owner(key: str) -> str:
    if key in CLAUDE_CODE_KEYS:
        return "read by Claude Code"
    if key in HERMES_KEYS:
        return "read by Hermes"
    return "not read by any known runtime"


def check_skill(skill_path, target: str = "default"):
    """Return (errors, warnings) as lists of strings."""
    errors: list[str] = []
    warnings: list[str] = []
    skill_path = Path(skill_path)
    skill_md = skill_path / "SKILL.md"
    if not skill_md.exists():
        return ["SKILL.md not found"], warnings
    try:
        content = skill_md.read_text(encoding="utf-8")
    except OSError as e:
        return [f"Could not read SKILL.md: {e}"], warnings

    frontmatter_text = _extract_frontmatter(content)
    if frontmatter_text is None:
        return ["Invalid frontmatter format"], warnings

    description_error = _validate_description_scalar(frontmatter_text)
    if description_error:
        return [description_error], warnings

    if yaml is not None:
        try:
            frontmatter = yaml.safe_load(frontmatter_text)
        except yaml.YAMLError as e:
            return [f"Invalid YAML in frontmatter: {e}"], warnings
        if not isinstance(frontmatter, dict):
            return ["Frontmatter must be a YAML dictionary"], warnings
    else:
        frontmatter = _parse_simple_frontmatter(frontmatter_text)
        if frontmatter is None:
            return ["Invalid YAML in frontmatter: unsupported syntax without PyYAML installed"], warnings

    strict = target in ("claude-ai", "spec")
    for key in sorted(set(frontmatter) - SPEC_KEYS, key=str):
        key = str(key)
        if "." in key:
            root_key, _, rest = key.partition(".")
            msg = (f"Top-level key '{key}' looks like a nested path. YAML does not nest dotted keys. "
                   f"Fix: write '{root_key}:' on its own line with '{rest}:' indented beneath it.")
            (errors if strict else warnings).append(msg)
            continue
        hint = ""
        if key in METADATA_HINT_KEYS:
            hint = f" Consider moving it under metadata ({key}: ...)."
        if strict:
            errors.append(
                f"Unexpected top-level key '{key}' ({key_owner(key)}). "
                f"Allowed: {', '.join(sorted(SPEC_KEYS))}.{hint}"
            )
        else:
            warnings.append(
                f"Non-spec top-level key '{key}' ({key_owner(key)}). Stripped by "
                f"'package_skill.py --target claude-ai'; claude.ai uploads reject it.{hint}"
            )

    for required in ("name", "description"):
        if required not in frontmatter:
            errors.append(f"Missing '{required}' in frontmatter")

    name = frontmatter.get("name")
    if name is not None:
        if not isinstance(name, str):
            errors.append(f"Name must be a string, got {type(name).__name__}")
        else:
            name = name.strip()
            if not name:
                errors.append("Name is empty")
            else:
                if not re.match(r"^[a-z0-9-]+$", name):
                    errors.append(f"Name '{name}' should be hyphen-case (lowercase letters, digits, and hyphens only)")
                if name.startswith("-") or name.endswith("-") or "--" in name:
                    errors.append(f"Name '{name}' cannot start/end with hyphen or contain consecutive hyphens")
                if len(name) > MAX_SKILL_NAME_LENGTH:
                    errors.append(f"Name is too long ({len(name)} characters). Maximum is {MAX_SKILL_NAME_LENGTH} characters.")
                dir_name = skill_path.resolve().name
                if name != dir_name:
                    errors.append(f"Name '{name}' must match the skill directory name '{dir_name}'")

    description = frontmatter.get("description")
    if description is not None:
        if not isinstance(description, str):
            errors.append(f"Description must be a string, got {type(description).__name__}")
        else:
            description = description.strip()
            if not description:
                errors.append("Description is empty")
            else:
                if "<" in description or ">" in description:
                    errors.append("Description cannot contain angle brackets (< or >)")
                if len(description) > 1024:
                    errors.append(f"Description is too long ({len(description)} characters). Maximum is 1024 characters.")

    if "compatibility" in frontmatter:
        comp = frontmatter["compatibility"]
        if not isinstance(comp, str):
            errors.append(f"Compatibility must be a string, got {type(comp).__name__}")
        elif not comp.strip():
            errors.append("Compatibility is empty (omit the field instead)")
        elif len(comp.strip()) > 500:
            errors.append(f"Compatibility is too long ({len(comp.strip())} characters). Maximum is 500 characters.")

    if "metadata" in frontmatter and yaml is not None and not isinstance(frontmatter["metadata"], dict):
        errors.append("Metadata must be a mapping")

    return errors, warnings


def validate_skill(skill_path, target: str = "default"):
    """Return (ok, message). Message lists errors (if any) or 'Skill is valid!' plus warnings."""
    errors, warnings = check_skill(skill_path, target)
    if errors:
        return False, "\n".join(errors + [f"warning: {w}" for w in warnings])
    msg = "Skill is valid!"
    if warnings:
        msg += "\n" + "\n".join(f"warning: {w}" for w in warnings)
    return True, msg


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description="Validate a skill directory", add_help=True)
    parser.add_argument("skill_dir")
    parser.add_argument("--target", choices=TARGETS, default="default")
    try:
        args = parser.parse_args(argv)
    except SystemExit as e:
        return 2 if e.code else 0
    ok, message = validate_skill(args.skill_dir, args.target)
    print(message)
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())
