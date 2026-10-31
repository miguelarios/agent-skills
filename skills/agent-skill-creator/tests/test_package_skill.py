#!/usr/bin/env python3
import importlib.util
import sys
import tempfile
import unittest
import zipfile
from pathlib import Path

SCRIPTS = Path(__file__).parents[1] / "scripts"
sys.path.insert(0, str(SCRIPTS))
spec = importlib.util.spec_from_file_location("package_skill", SCRIPTS / "package_skill.py")
package_skill = importlib.util.module_from_spec(spec)
spec.loader.exec_module(package_skill)

FM = """---
name: demo-skill
description: Demo thing. Use when testing packaging.
license: MIT
compatibility: Needs MY_API_KEY and curl
required_environment_variables:
  - name: MY_API_KEY
    prompt: Enter key
    help: https://example.com
platforms: [linux, macos]
when_to_use: extra trigger text
metadata:
  author: me
  hermes:
    tags: [a]
allowed-tools: Bash(curl:*)
---

# Demo
Body stays.
"""


class StripTests(unittest.TestCase):
    def test_strip_removes_only_nonspec_blocks(self):
        out, removed = package_skill.strip_frontmatter_keys(FM)
        self.assertEqual(removed, ["required_environment_variables", "platforms", "when_to_use"])
        self.assertNotIn("MY_API_KEY\n    prompt", out)
        self.assertNotIn("platforms", out)
        for keep in ("name: demo-skill", "license: MIT", "compatibility:", "metadata:", "  hermes:",
                     "allowed-tools:", "Body stays."):
            self.assertIn(keep, out)

    def test_nothing_to_strip(self):
        out, removed = package_skill.strip_frontmatter_keys("---\nname: a\ndescription: b\n---\nbody")
        self.assertEqual(removed, [])
        self.assertEqual(out, "---\nname: a\ndescription: b\n---\nbody")


class PackageTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.src = Path(self.tmp.name) / "demo-skill"
        (self.src / "scripts").mkdir(parents=True)
        (self.src / "SKILL.md").write_text(FM)
        (self.src / "scripts" / "x.py").write_text("print(1)\n")
        self.out = Path(self.tmp.name) / "dist"

    def read_zip_skill_md(self, path):
        with zipfile.ZipFile(path) as z:
            return z.read("demo-skill/SKILL.md").decode(), z.namelist()

    def test_default_keeps_everything(self):
        result = package_skill.package_skill(self.src, self.out, "default")
        text, names = self.read_zip_skill_md(result)
        self.assertEqual(text, FM)
        self.assertIn("demo-skill/scripts/x.py", names)

    def test_claude_ai_strips_copy_not_source(self):
        result = package_skill.package_skill(self.src, self.out, "claude-ai")
        text, _ = self.read_zip_skill_md(result)
        self.assertNotIn("required_environment_variables", text)
        self.assertNotIn("platforms", text)
        self.assertIn("compatibility: Needs MY_API_KEY", text)
        self.assertEqual((self.src / "SKILL.md").read_text(), FM)

    def test_invalid_skill_blocks_packaging(self):
        (self.src / "SKILL.md").write_text("---\nname: Wrong\ndescription: d\n---\n")
        self.assertIsNone(package_skill.package_skill(self.src, self.out, "claude-ai"))


if __name__ == "__main__":
    unittest.main()
