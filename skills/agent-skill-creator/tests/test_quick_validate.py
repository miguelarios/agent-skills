#!/usr/bin/env python3

import importlib.util
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch


VALIDATOR_PATH = Path(__file__).parents[1] / "scripts" / "quick_validate.py"
SPEC = importlib.util.spec_from_file_location("quick_validate", VALIDATOR_PATH)
quick_validate = importlib.util.module_from_spec(SPEC)
assert SPEC.loader is not None
SPEC.loader.exec_module(quick_validate)


class DescriptionYamlValidationTests(unittest.TestCase):
    def validate(self, description_lines: str):
        with tempfile.TemporaryDirectory() as temp_dir:
            skill_dir = Path(temp_dir) / "example-skill"
            skill_dir.mkdir()
            (skill_dir / "SKILL.md").write_text(
                "---\n"
                "name: example-skill\n"
                f"{description_lines}\n"
                "---\n\n"
                "# Example\n",
                encoding="utf-8",
            )
            with patch.object(quick_validate, "yaml", None):
                return quick_validate.validate_skill(skill_dir)

    def test_rejects_unquoted_colon_space_without_pyyaml(self):
        valid, message = self.validate(
            "description: Advises on categorization schema: what belongs where."
        )

        self.assertFalse(valid)
        self.assertIn("unquoted ': '", message)

    def test_accepts_quoted_colon_space_without_pyyaml(self):
        valid, message = self.validate(
            'description: "Advises on categorization schema: what belongs where."'
        )

        self.assertTrue(valid, message)

    def test_accepts_block_scalar_with_colon_space_without_pyyaml(self):
        valid, message = self.validate(
            "description: >\n  Advises on categorization schema: what belongs where."
        )

        self.assertTrue(valid, message)


class SpecAndTargetTests(unittest.TestCase):
    def make(self, frontmatter: str, dirname: str = "example-skill"):
        self._tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self._tmp.cleanup)
        d = Path(self._tmp.name) / dirname
        d.mkdir()
        (d / "SKILL.md").write_text(f"---\n{frontmatter}\n---\n\n# X\n", encoding="utf-8")
        return d

    BASE = "name: example-skill\ndescription: Does a thing. Use when asked."

    def test_minimal_valid(self):
        ok, msg = quick_validate.validate_skill(self.make(self.BASE))
        self.assertTrue(ok, msg)

    def test_name_must_match_dir(self):
        ok, msg = quick_validate.validate_skill(self.make(self.BASE, "other-dir"))
        self.assertFalse(ok)
        self.assertIn("must match", msg)

    def test_bad_name_rules(self):
        for bad in ("Bad_Name", "-lead", "a--b"):
            ok, _ = quick_validate.validate_skill(
                self.make(f"name: {bad}\ndescription: x y", bad))
            self.assertFalse(ok, bad)

    def test_description_angle_brackets_and_length(self):
        ok, msg = quick_validate.validate_skill(self.make("name: example-skill\ndescription: use <b> tags"))
        self.assertFalse(ok); self.assertIn("angle", msg)
        ok, msg = quick_validate.validate_skill(self.make("name: example-skill\ndescription: " + "a" * 1025))
        self.assertFalse(ok); self.assertIn("too long", msg)

    def test_compatibility_rules(self):
        ok, _ = quick_validate.validate_skill(self.make(self.BASE + "\ncompatibility: " + "a" * 501))
        self.assertFalse(ok)
        ok, _ = quick_validate.validate_skill(self.make(self.BASE + "\ncompatibility: Needs python 3.12"))
        self.assertTrue(ok)

    def test_extra_key_is_warning_by_default_and_names_runtime(self):
        d = self.make(self.BASE + "\nplatforms: [linux]\nwhen_to_use: whenever")
        errors, warnings = quick_validate.check_skill(d)
        self.assertEqual(errors, [])
        joined = "\n".join(warnings)
        self.assertIn("Hermes", joined)
        self.assertIn("Claude Code", joined)
        self.assertIn("claude-ai", joined)
        ok, msg = quick_validate.validate_skill(d)
        self.assertTrue(ok); self.assertIn("warning:", msg)

    def test_extra_key_is_error_for_claude_ai_and_spec(self):
        d = self.make(self.BASE + "\nplatforms: [linux]")
        for target in ("claude-ai", "spec"):
            ok, msg = quick_validate.validate_skill(d, target)
            self.assertFalse(ok, target)
            self.assertIn("platforms", msg)

    def test_nested_metadata_is_fine_even_strict(self):
        d = self.make(self.BASE + "\nmetadata:\n  openclaw:\n    requires:\n      bins: [jq]")
        ok, msg = quick_validate.validate_skill(d, "claude-ai")
        self.assertTrue(ok, msg)

    def test_dotted_top_level_key_flagged_with_fix(self):
        d = self.make(self.BASE + "\nmetadata.openclaw: {requires: {bins: [jq]}}")
        errors, warnings = quick_validate.check_skill(d)
        self.assertEqual(errors, [])
        self.assertIn("nested path", warnings[0])
        self.assertIn("metadata", warnings[0])
        errors, _ = quick_validate.check_skill(d, "spec")
        self.assertTrue(errors)

    def test_main_exit_codes(self):
        good = self.make(self.BASE)
        self.assertEqual(quick_validate.main([str(good)]), 0)
        self.assertEqual(quick_validate.main([str(self.make("name: x"))]), 1)
        self.assertEqual(quick_validate.main([]), 2)


if __name__ == "__main__":
    unittest.main()


def test_multiline_quoted_description_with_colon_is_valid(tmp_path):
    import scripts.quick_validate as qv
    d = tmp_path / "ml-skill"; d.mkdir()
    (d / "SKILL.md").write_text("---\nname: ml-skill\ndescription: 'Covers all write ops: create,\n  edit, and more. Use when editing.'\n---\n# x\n")
    ok, msg = qv.validate_skill(d)[:2]
    assert ok, msg
