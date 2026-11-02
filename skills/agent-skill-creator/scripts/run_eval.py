#!/usr/bin/env python3
"""Run trigger evaluation for a skill description.

Tests whether a skill's description makes the agent consult the skill for a
set of queries, using a pluggable runner (claude | hermes | dry).
Adapted from Anthropic's skill-creator run_eval.py (Apache-2.0).

Eval set format: [{"query": "...", "should_trigger": true}, ...]
Exit code: 0 on completion (results are in the JSON), 1 on bad input.
"""

import argparse
import json
import sys
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path

try:  # run as `python -m scripts.X` from the skill root...
    from scripts.utils import parse_skill_md
    from scripts.runners import make_runner, find_claude_project_root
except ModuleNotFoundError:  # ...or directly as `python scripts/X.py`
    from utils import parse_skill_md
    from runners import make_runner, find_claude_project_root


def run_eval(
    eval_set: list[dict],
    skill_name: str,
    description: str,
    num_workers: int,
    timeout: int,
    project_root: Path,
    runs_per_query: int = 1,
    trigger_threshold: float = 0.5,
    model: str | None = None,
    runner=None,
) -> dict:
    """Run the full eval set and return results. `runner` is a Runner instance."""
    if runner is None:
        runner = make_runner("claude")
    query_triggers: dict[str, list[bool]] = {}
    query_items: dict[str, dict] = {}

    # Threads, not processes: the work is subprocess/IO-bound and runner objects
    # (including test fakes) stay shareable.
    with ThreadPoolExecutor(max_workers=max(1, num_workers)) as executor:
        future_to_info = {}
        for item in eval_set:
            for run_idx in range(runs_per_query):
                fut = executor.submit(runner.trigger, item["query"], skill_name, description,
                                      timeout, str(project_root), model)
                future_to_info[fut] = (item, run_idx)
        for fut in as_completed(future_to_info):
            item, _ = future_to_info[fut]
            q = item["query"]
            query_items[q] = item
            query_triggers.setdefault(q, [])
            try:
                query_triggers[q].append(bool(fut.result()))
            except Exception as e:  # a failed run counts as "did not trigger"
                print(f"Warning: query failed: {e}", file=sys.stderr)
                query_triggers[q].append(False)

    results = []
    for q, triggers in query_triggers.items():
        item = query_items[q]
        rate = sum(triggers) / len(triggers)
        should = item["should_trigger"]
        ok = rate >= trigger_threshold if should else rate < trigger_threshold
        results.append({
            "query": q,
            "should_trigger": should,
            "trigger_rate": rate,
            "triggers": sum(triggers),
            "runs": len(triggers),
            "pass": ok,
        })
    passed = sum(1 for r in results if r["pass"])
    return {
        "skill_name": skill_name,
        "description": description,
        "runner": getattr(runner, "name", "custom"),
        "results": results,
        "summary": {"total": len(results), "passed": passed, "failed": len(results) - passed},
    }


def add_runner_args(parser):
    parser.add_argument("--runner", choices=["claude", "hermes", "dry"], default="claude",
                        help="How to decide whether the skill triggers (default: claude)")
    parser.add_argument("--dry-run", action="store_true",
                        help="Alias for --runner dry: offline stub, no LLM calls, scores are meaningless")
    parser.add_argument("--distractor-dir", default=None,
                        help="hermes runner: directory of sibling skills to include in the listing "
                             "so the skill competes realistically (e.g. ~/agent-skills/skills)")


def runner_from_args(args):
    name = "dry" if args.dry_run else args.runner
    return make_runner(name, distractor_dir=args.distractor_dir)


def main():
    parser = argparse.ArgumentParser(description="Run trigger evaluation for a skill description")
    parser.add_argument("--eval-set", required=True, help="Path to eval set JSON file")
    parser.add_argument("--skill-path", required=True, help="Path to skill directory")
    parser.add_argument("--description", default=None, help="Override description to test")
    parser.add_argument("--num-workers", type=int, default=10)
    parser.add_argument("--timeout", type=int, default=30, help="Timeout per query in seconds")
    parser.add_argument("--runs-per-query", type=int, default=3)
    parser.add_argument("--trigger-threshold", type=float, default=0.5)
    parser.add_argument("--model", default=None, help="Model for the runner (default: runner's configured model)")
    parser.add_argument("--verbose", action="store_true")
    add_runner_args(parser)
    args = parser.parse_args()

    skill_path = Path(args.skill_path)
    if not (skill_path / "SKILL.md").exists():
        print(f"Error: No SKILL.md found at {skill_path}", file=sys.stderr)
        sys.exit(1)
    eval_set = json.loads(Path(args.eval_set).read_text())
    name, original_description, _ = parse_skill_md(skill_path)
    description = args.description or original_description
    runner = runner_from_args(args)

    if args.verbose:
        print(f"Evaluating ({runner.name}): {description}", file=sys.stderr)
    output = run_eval(eval_set, name, description, args.num_workers, args.timeout,
                      find_claude_project_root(), args.runs_per_query,
                      args.trigger_threshold, args.model, runner)
    if args.verbose:
        s = output["summary"]
        print(f"Results: {s['passed']}/{s['total']} passed", file=sys.stderr)
        for r in output["results"]:
            print(f"  [{'PASS' if r['pass'] else 'FAIL'}] rate={r['triggers']}/{r['runs']} "
                  f"expected={r['should_trigger']}: {r['query'][:70]}", file=sys.stderr)
    print(json.dumps(output, indent=2))


if __name__ == "__main__":
    main()
