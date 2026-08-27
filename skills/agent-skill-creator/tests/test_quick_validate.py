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
            skill_dir = Path(temp_dir)
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


if __name__ == "__main__":
    unittest.main()
