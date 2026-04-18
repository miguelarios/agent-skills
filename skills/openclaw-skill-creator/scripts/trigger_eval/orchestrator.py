#!/usr/bin/env python3
"""
skill-eval orchestrator: Drives the full eval loop.

Spawns subagents for each eval case (with skill / without skill),
detects skill consultation via session history, records results,
and produces a graded benchmark.

This script is designed to run from an agent session that has access
to sessions_spawn, sessions_history, and the eval workspace scripts.

Usage (from agent session):
    python3 scripts/orchestrator.py <workspace-dir> --skill-name <name> [--model <model>]

The agent should:
  1. Run setup_agents.sh to create agent profiles
  2. Run this orchestrator to drive spawns and grading
  3. Run report.sh for the final markdown report

NOTE: This script prepares spawn commands but cannot execute sessions_spawn
      directly — it outputs a structured plan that the agent executes.
      Alternatively, if running inside OpenClaw, the agent can use the
      JSON plan to drive sessions_spawn calls.
"""

import argparse
import json
import os
import sys
from pathlib import Path


def load_eval_set(workspace_dir: str) -> dict:
    """Load the eval set from the workspace."""
    eval_set_path = os.path.join(workspace_dir, "eval_set.json")
    if not os.path.exists(eval_set_path):
        print(f"❌ Eval set not found: {eval_set_path}", file=sys.stderr)
        sys.exit(1)
    with open(eval_set_path) as f:
        return json.load(f)


def load_run_config(workspace_dir: str) -> dict:
    """Load the run config from the workspace."""
    config_path = os.path.join(workspace_dir, "run_config.json")
    if not os.path.exists(config_path):
        print(f"❌ Run config not found: {config_path}", file=sys.stderr)
        sys.exit(1)
    with open(config_path) as f:
        return json.load(f)


def generate_spawn_plan(workspace_dir: str, skill_name: str, model: str | None = None) -> dict:
    """
    Generate a structured spawn plan for the agent to execute.

    Returns a JSON object with spawn commands for each eval case.
    The agent should execute these via sessions_spawn and then
    call detect_and_record() on the results.
    """
    eval_set = load_eval_set(workspace_dir)
    run_config = load_run_config(workspace_dir)
    iteration_dir = os.path.join(workspace_dir, "iteration-1")

    plan = {
        "skill_name": skill_name,
        "model": model,
        "agent_with_skill": run_config["agent_with_skill"],
        "agent_without_skill": run_config["agent_without_skill"],
        "spawns": [],
    }

    for ev in eval_set["evals"]:
        eval_id = ev["id"]
        eval_dir = os.path.join(iteration_dir, f"eval-{eval_id}")

        # With-skill spawn
        with_spawn = {
            "eval_id": eval_id,
            "eval_name": ev.get("name", f"eval-{eval_id}"),
            "side": "with_skill",
            "agentId": run_config["agent_with_skill"],
            "task": ev["prompt"],
            "should_trigger": ev.get("should_trigger", True),
            "eval_dir": eval_dir,
            "label": f"eval-{eval_id}-with",
        }
        if model:
            with_spawn["model"] = model
        plan["spawns"].append(with_spawn)

        # Without-skill spawn
        without_spawn = {
            "eval_id": eval_id,
            "eval_name": ev.get("name", f"eval-{eval_id}"),
            "side": "without_skill",
            "agentId": run_config["agent_without_skill"],
            "task": ev["prompt"],
            "should_trigger": ev.get("should_trigger", True),
            "eval_dir": eval_dir,
            "label": f"eval-{eval_id}-without",
        }
        if model:
            without_spawn["model"] = model
        plan["spawns"].append(without_spawn)

    return plan


def detect_skill_consultation(session_history: dict, skill_name: str) -> dict:
    """
    Analyze session history to determine if a skill was consulted.

    Detection heuristic: Look for a 'read' tool call where the path
    contains '<skill_name>/SKILL.md' or similar patterns.

    Returns:
        {
            "triggered": bool,
            "tool_calls": list[str],  # descriptions of matching tool calls
            "total_tool_calls": int,
            "evidence": str
        }
    """
    triggered = False
    skill_calls = []
    total_tool_calls = 0
    evidence = ""

    # Patterns that indicate skill consultation
    skill_patterns = [
        f"{skill_name}/SKILL.md",
        f"{skill_name}\\\\SKILL.md",  # Windows-style
        f"skills/{skill_name}",
        f"SKILL.md",  # Generic — any skill read
    ]

    messages = session_history.get("messages", [])
    for msg in messages:
        content = msg.get("content", [])
        if not isinstance(content, list):
            continue

        for block in content:
            if block.get("type") == "toolCall":
                total_tool_calls += 1
                tool_name = block.get("name", "")
                arguments = block.get("arguments", {})
                path = arguments.get("path", "")

                # Check if this is a skill read
                if tool_name == "read":
                    for pattern in skill_patterns:
                        if pattern.lower() in path.lower():
                            triggered = True
                            skill_calls.append({
                                "tool": tool_name,
                                "path": path,
                                "pattern_matched": pattern,
                            })
                            break

                # Also check exec calls that might reference skills
                if tool_name == "exec" and "skill" in arguments.get("command", "").lower():
                    # Less certain — flag but don't count as triggered
                    skill_calls.append({
                        "tool": tool_name,
                        "command": arguments.get("command", "")[:100],
                        "pattern_matched": "exec-skill-reference",
                    })

    if triggered:
        matched_paths = [c["path"] for c in skill_calls if "path" in c]
        evidence = f"Skill consulted via read: {', '.join(matched_paths)}"
    elif total_tool_calls == 0:
        evidence = "No tool calls made — agent answered from model knowledge"
    else:
        evidence = f"Agent made {total_tool_calls} tool call(s) but none referenced the skill"

    return {
        "triggered": triggered,
        "skill_calls": skill_calls,
        "total_tool_calls": total_tool_calls,
        "evidence": evidence,
    }


def generate_record_commands(plan: dict, results: dict) -> list[str]:
    """
    Generate record_result.sh commands from spawn results.

    Args:
        plan: The spawn plan
        results: Dict mapping spawn label -> {session_key, history, triggered, tokens, duration_ms}

    Returns:
        List of shell commands to execute
    """
    commands = []
    scripts_dir = Path(__file__).parent

    for spawn in plan["spawns"]:
        label = spawn["label"]
        if label not in results:
            continue

        result = results[label]
        eval_dir = spawn["eval_dir"]
        side = spawn["side"]
        triggered = "true" if result.get("triggered") else "false"
        output = result.get("output", "")[:500]  # Truncate
        tokens = result.get("tokens", 0)
        duration_ms = result.get("duration_ms", 0)

        cmd = (
            f"bash {scripts_dir}/record_result.sh {eval_dir} "
            f"--side {side} "
            f"--triggered {triggered} "
            f"--output {json.dumps(output)} "
            f"--tokens {tokens} "
            f"--duration_ms {duration_ms}"
        )
        commands.append(cmd)

    return commands


def plan_to_json(plan: dict, output_path: str | None = None) -> str:
    """Serialize the spawn plan to JSON."""
    plan_json = json.dumps(plan, indent=2)
    if output_path:
        with open(output_path, "w") as f:
            f.write(plan_json)
        print(f"📄 Spawn plan written to: {output_path}")
    return plan_json


def main():
    parser = argparse.ArgumentParser(description="skill-eval orchestrator")
    parser.add_argument("workspace_dir", help="Path to the eval workspace")
    parser.add_argument("--skill-name", required=True, help="Name of the skill to evaluate")
    parser.add_argument("--model", default=None, help="Model override for eval runs")
    parser.add_argument("--action", choices=["plan", "detect", "grade"], default="plan",
                        help="Action to perform: plan (generate spawn plan), detect (analyze history), grade (run full grade)")
    parser.add_argument("--session-history", help="Path to session history JSON (for detect action)")
    parser.add_argument("--output", help="Output path for results")

    args = parser.parse_args()

    if args.action == "plan":
        plan = generate_spawn_plan(args.workspace_dir, args.skill_name, args.model)
        plan_to_json(plan, args.output or os.path.join(args.workspace_dir, "spawn_plan.json"))
        print(f"\n📋 Generated {len(plan['spawns'])} spawn commands")
        print(f"   Agent with skill:    {plan['agent_with_skill']}")
        print(f"   Agent without skill: {plan['agent_without_skill']}")
        print(f"   Model: {args.model or 'default'}")
        print(f"\n⚠️  Execute these spawns from your agent session using sessions_spawn.")
        print(f"   Then run with --action detect to analyze results.")

    elif args.action == "detect":
        if not args.session_history:
            print("❌ --session-history required for detect action", file=sys.stderr)
            sys.exit(1)
        with open(args.session_history) as f:
            history = json.load(f)
        result = detect_skill_consultation(history, args.skill_name)
        print(json.dumps(result, indent=2))

    elif args.action == "grade":
        scripts_dir = Path(__file__).parent
        import subprocess
        result = subprocess.run(
            ["bash", str(scripts_dir / "grade.sh"), args.workspace_dir, "--skill-name", args.skill_name],
            capture_output=True, text=True
        )
        print(result.stdout)
        if result.stderr:
            print(result.stderr, file=sys.stderr)


if __name__ == "__main__":
    main()
