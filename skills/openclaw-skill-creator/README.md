# openclaw-skill-creator

An OpenClaw-specific skill for creating, testing, and distributing Agent Skills — following the [AgentSkills](https://agentskills.io) open standard with OpenClaw extensions for gating, slash commands, ClawHub distribution, and multi-agent setups.

Forked from the agent-agnostic [skill-creator](https://github.com/anthropics/skill-creator), adapted with OpenClaw-specific conventions from [OpenClaw docs](https://docs.openclaw.ai/tools/skills.md).

## Structure

```
openclaw-skill-creator/
├── SKILL.md                      ← workflow-narrative for the agent
├── agents/
│   ├── grader.md
│   ├── comparator.md
│   └── analyzer.md
├── assets/
│   └── eval_review.html
├── eval-viewer/
│   ├── generate_review.py
│   └── viewer.html
├── references/
│   ├── description-optimization.md
│   ├── distribution.md
│   ├── openclaw-config.md
│   ├── schemas.md
│   ├── skill-patterns.md
│   ├── testing-methodology.md
│   ├── troubleshooting.md
│   └── writing-scripts.md
└── scripts/
    ├── aggregate_benchmark.py
    ├── generate_report.py
    ├── init_skill.py
    ├── package_skill.py
    ├── quick_validate.py
    └── trigger_eval/             ← merged from former skill-eval/
        ├── setup_agents.sh       ← creates eval-with-X / eval-without-X agent profiles
        ├── run_eval.sh           ← preps the eval workspace
        ├── orchestrator.py       ← spawn-plan + skill-consultation detector
        ├── record_result.sh      ← records a single subagent run's result
        ├── grade.sh              ← grades trigger-accuracy results
        ├── report.sh             ← generates a markdown trigger eval report
        └── generate_evals.sh     ← generates a starter eval set template
```

## What's OpenClaw-Specific

Compared to the agent-agnostic skill-creator, this version adds:

### SKILL.md is workflow-first
Mirrors the structure of Anthropic's official skill-creator: opens with the high-level loop, then walks through Capture Intent → Interview → Init → Write → Test → Iterate → Optimize Description → Package, with the OpenClaw-specific A/B mechanics (agent-profile setup, `sessions_spawn`, session-history-based trigger detection) baked into the testing workflow as Step 0 through Step 5. Declarative reference content (frontmatter spec, gating, patterns) lives in `references/` rather than the body.

### Trigger eval subsystem
Merged in from the former standalone `skill-eval` skill. Lives at `scripts/trigger_eval/`. Provides the OpenClaw-specific A/B test machinery: temporary agent profiles, spawn plan generation, session-history scanning for skill consultation, and basic trigger-accuracy grading.

### SKILL.md
- OpenClaw skill locations and precedence (workspace → managed → bundled)
- Multi-agent skill sharing guidance
- `metadata.openclaw` frontmatter (gating, installers, emoji, OS filtering)
- OpenClaw-specific optional fields (`user-invocable`, `disable-model-invocation`, `command-dispatch`, `command-tool`, `command-arg-mode`)
- `{baseDir}` placeholder usage
- Token cost awareness section
- Session snapshot / hot reload behavior
- Distribution via ClawHub instead of generic packaging
- Updated checklist with gating, slash commands, and `{baseDir}` items

### references/openclaw-config.md (new)
Comprehensive reference for OpenClaw configuration affecting skills: load-time gating, `~/.openclaw/openclaw.json` overrides, environment injection, installer specs, skills watcher, remote macOS nodes, and plugin-shipped skills.

### references/distribution.md (rewritten)
Covers ClawHub as primary distribution channel (`clawhub install`, `clawhub update`, `clawhub sync`), local installation paths, plugin-shipped skills, and `.skill` packaging as a secondary option for GitHub/direct sharing.

### references/skill-patterns.md (extended)
Added two new patterns:
- **Pattern E: Slash Command Skills** — direct tool dispatch bypassing the model
- **Pattern F: Gated Skills** — skills filtered by binary/env/platform requirements

### references/troubleshooting.md (extended)
Added OpenClaw-specific sections: skill not appearing (gating issues), metadata JSON parse errors, slash command not working, gating not filtering correctly.

### scripts/init_skill.py (extended)
- `--gated` flag scaffolds `metadata.openclaw` with `requires` placeholders
- `--slash-command TOOL_NAME` creates a minimal slash command skill with `command-dispatch: tool`
- `{baseDir}` hint in template
- `~/.openclaw/` path expansion support

### scripts/quick_validate.py (extended)
- Validates `metadata` is single-line JSON (OpenClaw parser requirement)
- Validates `metadata.openclaw` structure (requires, primaryEnv, os, install, etc.)
- Validates `command-dispatch` / `command-tool` consistency
- Validates `user-invocable` and `disable-model-invocation` are booleans
- Warns when `primaryEnv` is not in `requires.env`
- Accepts OpenClaw-specific frontmatter fields

### Unchanged (platform-agnostic, still applies)
- Core principles (concise, degrees of freedom, procedures over declarations, coherent units)
- Testing methodology and eval tooling
- Agent roles (grader, comparator, analyzer)
- Description optimization methodology
- Writing scripts reference
- JSON schemas for evals/grading/benchmarks
- Package script (retained for GitHub/direct sharing use case)
