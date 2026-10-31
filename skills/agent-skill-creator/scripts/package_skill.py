#!/usr/bin/env python3
"""
Skill Packager - Creates a distributable .skill file of a skill folder

Usage:
    python scripts/package_skill.py <path/to/skill-folder> [output-directory] [--target default|claude-ai|spec]

Targets:
    default    Package the folder as is (spec errors block; extra keys only warn).
    claude-ai  claude.ai uploads and the Skills API reject non-spec top-level
    spec       frontmatter keys, so they are stripped from the PACKAGED COPY of
               SKILL.md (never from the source) and the removed keys are printed.
               'spec' behaves the same; use it for any strict consumer.

Example:
    python scripts/package_skill.py skills/public/my-skill
    python scripts/package_skill.py skills/public/my-skill ./dist
"""

import argparse
import re
import sys
import tempfile
import zipfile
from pathlib import Path

try:
    from scripts.quick_validate import SPEC_KEYS, _extract_frontmatter, validate_skill
except ModuleNotFoundError:
    from quick_validate import SPEC_KEYS, _extract_frontmatter, validate_skill

_TOP_KEY = re.compile(r"^([^\s#:-][^:]*?)\s*:(\s|$)")


def strip_frontmatter_keys(content: str, keep=SPEC_KEYS):
    """Remove non-spec top-level keys (and their nested blocks) from SKILL.md text.

    Text-level so comments, quoting and the body survive untouched and no YAML
    library is needed. Returns (new_content, removed_keys).
    """
    lines = content.split("\n")
    if not lines or lines[0].strip() != "---":
        return content, []
    end = next((i for i in range(1, len(lines)) if lines[i].strip() == "---"), None)
    if end is None:
        return content, []
    out, removed, dropping = [lines[0]], [], False
    for line in lines[1:end]:
        m = _TOP_KEY.match(line) if line[:1] not in (" ", "\t", "-", "#") and line.strip() else None
        if m:
            key = m.group(1).strip().strip("\"'")
            dropping = key not in keep
            if dropping:
                removed.append(key)
        elif line.strip() and line[:1] not in (" ", "\t", "-", "#"):
            dropping = False  # unrecognised construct: keep
        if not dropping:
            out.append(line)
    out.extend(lines[end:])
    return "\n".join(out), removed


def _is_within(path: Path, root: Path) -> bool:
    try:
        path.relative_to(root)
        return True
    except ValueError:
        return False


def package_skill(skill_path, output_dir=None, target="default"):
    """
    Package a skill folder into a .skill file.

    Args:
        skill_path: Path to the skill folder
        output_dir: Optional output directory for the .skill file (defaults to current directory)
        target: default | claude-ai | spec (the last two strip non-spec top-level keys from the packaged copy)

    Returns:
        Path to the created .skill file, or None if error
    """
    skill_path = Path(skill_path).resolve()

    if not skill_path.exists():
        print(f"[ERROR] Skill folder not found: {skill_path}")
        return None

    if not skill_path.is_dir():
        print(f"[ERROR] Path is not a directory: {skill_path}")
        return None

    skill_md = skill_path / "SKILL.md"
    if not skill_md.exists():
        print(f"[ERROR] SKILL.md not found in {skill_path}")
        return None

    # Run validation before packaging
    print("Validating skill...")
    valid, message = validate_skill(skill_path, "default")
    if not valid:
        print(f"[ERROR] Validation failed: {message}")
        print("   Please fix the validation errors before packaging.")
        return None
    print(f"[OK] {message}\n")

    skill_md_override = None  # stripped SKILL.md text for strict targets
    if target in ("claude-ai", "spec"):
        original = skill_md.read_text(encoding="utf-8")
        stripped, removed = strip_frontmatter_keys(original)
        if removed:
            print(f"[STRIP] --target {target}: removed top-level keys from the packaged SKILL.md "
                  f"(source untouched): {', '.join(removed)}")
            print("        Their behavior is lost in this build. Express requirements in "
                  "'compatibility' and a Prerequisites section so they survive.\n")
        else:
            print(f"[OK] --target {target}: no non-spec keys to strip\n")
        with tempfile.TemporaryDirectory() as tmp:
            check_dir = Path(tmp) / skill_path.name
            check_dir.mkdir()
            (check_dir / "SKILL.md").write_text(stripped, encoding="utf-8")
            ok, msg = validate_skill(check_dir, "spec")
        if not ok:
            print(f"[ERROR] Stripped SKILL.md still fails the spec: {msg}")
            return None
        skill_md_override = stripped

    # Determine output location
    skill_name = skill_path.name
    if output_dir:
        output_path = Path(output_dir).resolve()
        output_path.mkdir(parents=True, exist_ok=True)
    else:
        output_path = Path.cwd()

    skill_filename = output_path / f"{skill_name}.skill"

    EXCLUDED_DIRS = {".git", ".svn", ".hg", "__pycache__", "node_modules"}

    try:
        with zipfile.ZipFile(skill_filename, "w", zipfile.ZIP_DEFLATED) as zipf:
            for file_path in skill_path.rglob("*"):
                # Security: never follow or package symlinks
                if file_path.is_symlink():
                    print(f"[WARN] Skipping symlink: {file_path}")
                    continue

                rel_parts = file_path.relative_to(skill_path).parts
                if any(part in EXCLUDED_DIRS for part in rel_parts):
                    continue

                if file_path.is_file():
                    resolved_file = file_path.resolve()
                    if not _is_within(resolved_file, skill_path):
                        print(f"[ERROR] File escapes skill root: {file_path}")
                        return None
                    if resolved_file == skill_filename.resolve():
                        print(f"[WARN] Skipping output archive: {file_path}")
                        continue

                    arcname = Path(skill_name) / file_path.relative_to(skill_path)
                    if skill_md_override is not None and file_path == skill_path / "SKILL.md":
                        zipf.writestr(str(arcname), skill_md_override)
                    else:
                        zipf.write(file_path, arcname)
                    print(f"  Added: {arcname}")

        print(f"\n[OK] Successfully packaged skill to: {skill_filename}")
        return skill_filename

    except Exception as e:
        print(f"[ERROR] Error creating .skill file: {e}")
        return None


def main(argv=None):
    parser = argparse.ArgumentParser(description="Package a skill folder into a .skill file")
    parser.add_argument("skill_folder")
    parser.add_argument("output_dir", nargs="?", default=None)
    parser.add_argument("--target", choices=["default", "claude-ai", "spec"], default="default")
    try:
        args = parser.parse_args(argv)
    except SystemExit as e:
        sys.exit(2 if e.code else 0)

    print(f"Packaging skill: {args.skill_folder} (target: {args.target})")
    if args.output_dir:
        print(f"   Output directory: {args.output_dir}")
    print()
    sys.exit(0 if package_skill(args.skill_folder, args.output_dir, args.target) else 1)


if __name__ == "__main__":
    main()
