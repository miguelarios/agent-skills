#!/usr/bin/env python3
"""Offline smoke tests for run_eval / improve_description / run_loop. No LLM, no network."""
import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).parents[1]
sys.path.insert(0, str(ROOT))

from scripts import improve_description, run_eval, run_loop, runners  # noqa: E402

SKILL_MD = """---
name: sample-skill
description: Convert spreadsheet files into charts. Use when the user has an xlsx or csv and wants a chart.
---

# Sample
"""

EVALS = [
    {"query": "turn my quarterly spreadsheet csv into a chart please", "should_trigger": True},
    {"query": "make a chart from this xlsx spreadsheet with revenue", "should_trigger": True},
    {"query": "chart these spreadsheet csv numbers for the board", "should_trigger": True},
    {"query": "write a haiku about autumn leaves falling", "should_trigger": False},
    {"query": "explain kubernetes pod scheduling basics", "should_trigger": False},
    {"query": "summarize the plot of hamlet quickly", "should_trigger": False},
]


class FakeRunner(runners.Runner):
    name = "fake"
    calls = 0

    def trigger(self, query, skill_name, description, timeout, project_root, model=None):
        FakeRunner.calls += 1
        return "chart" in query

    def complete(self, prompt, model, timeout=300):
        return "<new_description>Chart spreadsheets. Use for charts.</new_description>"


class TriggerTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.skill = Path(self.tmp.name) / "sample-skill"
        self.skill.mkdir()
        (self.skill / "SKILL.md").write_text(SKILL_MD)

    def test_run_eval_with_fake_runner(self):
        out = run_eval.run_eval(EVALS, "sample-skill", "d", 2, 5, Path(self.tmp.name),
                                runs_per_query=2, runner=FakeRunner())
        self.assertEqual(out["summary"], {"total": 6, "passed": 6, "failed": 0})
        self.assertTrue(all(r["runs"] == 2 for r in out["results"]))

    def test_improve_description_uses_runner(self):
        res = {"description": "old", "results": [], "summary": {"passed": 0, "total": 0}}
        new = improve_description.improve_description(
            "sample-skill", SKILL_MD, "old", res, [], None, runner=FakeRunner())
        self.assertEqual(new, "Chart spreadsheets. Use for charts.")

    def test_run_loop_dry_runner(self):
        out = run_loop.run_loop(EVALS, self.skill, None, 2, 5, 2, 1, 0.5, 0.4, None, False,
                                runner=runners.DryRunner())
        self.assertIn("best_description", out)
        self.assertEqual(out["train_size"] + out["test_size"], len(EVALS))
        self.assertGreaterEqual(out["iterations_run"], 1)

    def test_cli_dry_run_end_to_end(self):
        evals = Path(self.tmp.name) / "e.json"
        evals.write_text(json.dumps(EVALS))
        r = subprocess.run([sys.executable, str(ROOT / "scripts" / "run_eval.py"), "--eval-set", str(evals),
                            "--skill-path", str(self.skill), "--dry-run", "--runs-per-query", "1"],
                           capture_output=True, text=True)
        self.assertEqual(r.returncode, 0, r.stderr)
        data = json.loads(r.stdout)
        self.assertEqual(data["runner"], "dry")
        self.assertEqual(data["summary"]["total"], 6)
        r = subprocess.run([sys.executable, "-m", "scripts.run_loop", "--eval-set", str(evals),
                            "--skill-path", str(self.skill), "--dry-run", "--runs-per-query", "1",
                            "--max-iterations", "2", "--report", "none"],
                           capture_output=True, text=True, cwd=ROOT)
        self.assertEqual(r.returncode, 0, r.stderr)
        self.assertIn("best_description", json.loads(r.stdout))


class HermesRunnerTests(unittest.TestCase):
    def test_parse_answer(self):
        self.assertEqual(runners.parse_skill_answer('blah {"skill": "foo-bar"}'), "foo-bar")
        self.assertIsNone(runners.parse_skill_answer('{"skill": "none"}'))
        self.assertIsNone(runners.parse_skill_answer("no json here"))
        self.assertEqual(runners.parse_skill_answer('{"skill":"a"} then {"skill": "b"}'), "b")

    def test_prompt_contains_listing_and_query(self):
        with tempfile.TemporaryDirectory() as d:
            other = Path(d) / "other"
            other.mkdir()
            (other / "SKILL.md").write_text("---\nname: other\ndescription: Other thing.\n---\n")
            r = runners.HermesRunner(distractor_dir=Path(d))
            p = r.build_trigger_prompt("do the thing", "mine", "My desc.")
            for s in ("- mine: My desc.", "- other: Other thing.", "do the thing", '{"skill"'):
                self.assertIn(s, p)

    def test_trigger_compares_name(self):
        r = runners.HermesRunner()
        r._chat = lambda prompt, model, timeout: '{"skill": "Mine"}'
        self.assertTrue(r.trigger("q", "mine", "d", 5, "."))
        r._chat = lambda prompt, model, timeout: '{"skill": "none"}'
        self.assertFalse(r.trigger("q", "mine", "d", 5, "."))


if __name__ == "__main__":
    unittest.main()
