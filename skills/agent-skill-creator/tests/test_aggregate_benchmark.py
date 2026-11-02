import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

SCRIPT = Path(__file__).parents[1] / "scripts" / "aggregate_benchmark.py"


class FlatLayoutTests(unittest.TestCase):
    def test_flat_layout_with_descriptive_eval_name(self):
        with tempfile.TemporaryDirectory() as d:
            it = Path(d) / "iteration-1"
            for cfg, rate in (("with_skill", 1.0), ("without_skill", 0.5)):
                run = it / "eval-chart-from-csv" / cfg
                (run / "outputs").mkdir(parents=True)
                (run / "grading.json").write_text(json.dumps(
                    {"summary": {"pass_rate": rate, "passed": 1, "failed": 1, "total": 2}, "expectations": []}))
                (run / "timing.json").write_text(json.dumps(
                    {"total_tokens": 10, "duration_ms": 1000, "total_duration_seconds": 1.0}))
            r = subprocess.run([sys.executable, str(SCRIPT), str(it), "--skill-name", "x"],
                               capture_output=True, text=True)
            self.assertEqual(r.returncode, 0, r.stderr)
            bench = json.loads((it / "benchmark.json").read_text())
            self.assertEqual(len(bench["runs"]), 2)
            self.assertEqual({x["configuration"] for x in bench["runs"]}, {"with_skill", "without_skill"})


if __name__ == "__main__":
    unittest.main()
