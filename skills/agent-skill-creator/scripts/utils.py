"""Shared utilities for the trigger-eval scripts.

Adapted from Anthropic's skill-creator (Apache-2.0,
https://github.com/anthropics/skills/tree/main/skills/skill-creator).
Stdlib only; PyYAML is used when installed.
"""

from __future__ import annotations

from pathlib import Path

try:
    import yaml
except ModuleNotFoundError:  # optional
    yaml = None


def _split_frontmatter(content: str) -> list[str]:
    lines = content.split("\n")
    if lines[0].strip() != "---":
        raise ValueError("SKILL.md missing frontmatter (no opening ---)")
    for i, line in enumerate(lines[1:], start=1):
        if line.strip() == "---":
            return lines[1:i]
    raise ValueError("SKILL.md missing frontmatter (no closing ---)")


def parse_skill_md(skill_path: Path) -> tuple[str, str, str]:
    """Parse a SKILL.md file, returning (name, description, full_content)."""
    content = (Path(skill_path) / "SKILL.md").read_text(encoding="utf-8")
    fm_lines = _split_frontmatter(content)

    if yaml is not None:
        try:
            data = yaml.safe_load("\n".join(fm_lines)) or {}
            if isinstance(data, dict):
                return (
                    str(data.get("name", "")).strip(),
                    " ".join(str(data.get("description", "")).split()),
                    content,
                )
        except yaml.YAMLError:
            pass  # fall through to the line parser

    name = ""
    description = ""
    i = 0
    while i < len(fm_lines):
        line = fm_lines[i]
        if line.startswith("name:"):
            name = line[len("name:"):].strip().strip('"').strip("'")
        elif line.startswith("description:"):
            value = line[len("description:"):].strip()
            if value in (">", "|", ">-", "|-"):
                parts: list[str] = []
                i += 1
                while i < len(fm_lines) and fm_lines[i][:1] in (" ", "\t"):
                    parts.append(fm_lines[i].strip())
                    i += 1
                description = " ".join(parts)
                continue
            description = value.strip('"').strip("'")
        i += 1
    return name, description, content
