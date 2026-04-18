# Testing Methodology

Choose testing rigor to match your skill's visibility and impact.

> **Where this file fits:** The full testing workflow (Step 0 through Step 5, with helper scripts) lives in SKILL.md. This reference covers the *why* behind those steps and the deeper testing techniques (pressure testing, cross-model testing, blind comparison) you can layer on top.

## OpenClaw-Specific A/B Mechanism

Before reading anything else here, internalize this constraint: **OpenClaw doesn't have per-spawn skill control.** Skill visibility is set at the agent profile level via `agents.list[].skills` in `~/.openclaw/openclaw.json`. To A/B test a skill (with vs without), you need two agent profiles — typically `eval-with-<skill-name>` and `eval-without-<skill-name>` — and you spawn subagents at each profile via `sessions_spawn`. The helper `scripts/trigger_eval/setup_agents.sh` creates these profiles and `--cleanup` removes them.

This means every reference to "spawn two subagents" in the rest of this file translates to: spawn one at each of the two eval agent profiles. And every change to the skill needs an `openclaw gateway restart` (or hot reload) to take effect, because OpenClaw snapshots eligible skills at session start.

Detecting whether a subagent actually consulted the skill is heuristic: analyze its `sessions_history` for a `read` tool call whose path matches `<skill-name>/SKILL.md`. The `scripts/trigger_eval/orchestrator.py` script's `detect_skill_consultation()` function does this.

## Testing Tiers

1. **Manual testing** — Run queries directly, observe behavior. Fast iteration, no setup.
2. **Scripted testing** — Automate test cases for repeatable validation across changes.
3. **Structured evals** — JSON-based test cases, assertions, grading, and benchmarking for systematic iteration.

## Pro Tip: Start with One Hard Task

Iterate on a single challenging task until the AI assistant succeeds, then extract the winning approach into a skill. This provides faster signal than broad testing. Once the foundation works, expand to multiple test cases for coverage.

## 1. Triggering Tests

**Goal:** Ensure the skill loads at the right times and doesn't load for irrelevant queries.

```
Should trigger:
- "Help me set up a new ProjectHub workspace"
- "I need to create a project in ProjectHub"
- "Initialize a ProjectHub project for Q4 planning"

Should NOT trigger:
- "What's the weather in San Francisco?"
- "Help me write Python code"
- "Create a spreadsheet"
```

Vary natural language phrasing. The most valuable negative tests are near-misses that share keywords but need a different skill. See `references/description-optimization.md` for the full trigger eval methodology.

## 2. Functional Tests

**Goal:** Verify the skill produces correct outputs.

```
Test: Create project with 5 tasks
Given: Project name "Q4 Planning", 5 task descriptions
When: Skill executes workflow
Then:
  - Project created in ProjectHub
  - 5 tasks created with correct properties
  - All tasks linked to project
  - No API errors
```

Cover happy path, error handling, and edge cases (empty inputs, large data, missing fields).

## 3. Baseline Comparison

**Goal:** Prove the skill improves results vs. no skill.

Run each test case twice — once at the `eval-with-<skill-name>` agent profile, once at `eval-without-<skill-name>` (or at a profile pointing at a snapshot of the previous version). Compare:

- Number of messages to complete task
- Tool call success rate
- Token consumption
- User corrections needed
- Consistency across repeated runs (same request 3-5 times)

## 4. Structured Evals

For skills where quality matters at scale, use a structured eval framework. This gives you a repeatable feedback loop. See `references/schemas.md` for complete JSON format definitions.

### Test Case Format

Store test cases in `evals/evals.json`:

```json
{
  "skill_name": "csv-analyzer",
  "evals": [
    {
      "id": 1,
      "prompt": "I have a CSV of monthly sales in data/sales_2025.csv. Find the top 3 months by revenue and make a bar chart.",
      "expected_output": "A bar chart showing top 3 months by revenue with labeled axes.",
      "files": ["evals/files/sales_2025.csv"],
      "assertions": [
        "The output includes a bar chart image file",
        "The chart shows exactly 3 months",
        "Both axes are labeled"
      ]
    }
  ]
}
```

**Tips for test prompts:**
- Start with 2-3 test cases — don't over-invest before first results
- Vary phrasing, detail level, and formality
- Include at least one edge case
- Use realistic context (file paths, column names, personal details)
- Add assertions *after* seeing first-run outputs, not before

### Workspace Structure

Organize results by iteration, with side-by-side with/without-skill runs:

```
workspace/
└── iteration-1/
    ├── eval-top-months-chart/
    │   ├── with_skill/
    │   │   ├── outputs/
    │   │   ├── timing.json
    │   │   └── grading.json
    │   └── without_skill/
    │       └── ...
    ├── eval-clean-missing-emails/
    │   └── ...
    └── benchmark.json
```

### Grading

Evaluate each assertion against actual outputs. Require concrete evidence for a PASS — don't give benefit of the doubt. For assertions checkable by code (valid JSON, correct row count, file exists), use a verification script — scripts are more reliable than LLM judgment for mechanical checks. See `agents/grader.md` for the grader role instructions and `references/schemas.md` for the `grading.json` format.

### Benchmark Aggregation

Run `scripts/aggregate_benchmark.py <workspace>/iteration-N` to produce `benchmark.json` and `benchmark.md` with pass_rate, time, and tokens for each configuration, including mean ± stddev and delta. See `references/schemas.md` for the full benchmark format.

The delta tells you what the skill costs (time, tokens) and what it buys (pass rate). A skill that adds 13 seconds but improves pass rate by 50 points is probably worth it.

### Human Review

Assertions only catch what you thought to check. Use `eval-viewer/generate_review.py <workspace>` to serve an interactive review UI, or `--static output.html` for a standalone file. Review actual outputs alongside grades and record specific feedback. Empty feedback = output looked fine. Focus improvements on test cases with specific complaints.

### Analyzing Patterns

After aggregating:
- **Remove assertions that always pass in both configs** — they don't measure skill value
- **Investigate assertions that always fail in both** — assertion may be broken
- **Study assertions that pass with skill but fail without** — this is where the skill adds value
- **Tighten instructions when results are inconsistent** (high stddev) — the skill's instructions may be ambiguous
- **Check time/token outliers** — read execution transcripts to find bottlenecks

### Blind Comparison

For comparing two skill versions: present both outputs to an LLM judge without revealing which came from which version. The judge scores holistic qualities (organization, formatting, usability) free from bias. This complements assertion grading — two outputs might pass all assertions but differ in overall quality.

See `agents/comparator.md` for the blind comparison role instructions and `agents/analyzer.md` for post-hoc analysis of why a winner won. See `references/schemas.md` for the `comparison.json` and `analysis.json` formats.

## 5. Pressure Testing (for Discipline-Enforcing Skills)

Skills that enforce rules (TDD compliance, verification requirements, coding standards) need adversarial testing. The AI assistant may rationalize skipping the rules when under pressure.

**Approach: RED-GREEN-REFACTOR**

1. **RED** — Run scenario *without* the skill. Watch the AI fail. Document exact rationalizations verbatim.
2. **GREEN** — Write skill addressing those specific failures. Run same scenario *with* skill. Verify compliance.
3. **REFACTOR** — If new rationalizations appear, add explicit counters. Re-test until bulletproof.

**Pressure scenario design** — combine 3+ types:

| Pressure | Example |
|----------|---------|
| **Time** | Emergency, deadline, deploy window closing |
| **Sunk cost** | Hours of work, "waste" to delete |
| **Authority** | Senior says skip it, manager overrides |
| **Exhaustion** | End of day, tired, want to finish |
| **Social** | Looking dogmatic, seeming inflexible |

**Example scenario:**
```
You spent 3 hours writing 200 lines of code. It works.
You manually tested all edge cases. It's 6pm, dinner at 6:30pm.
Code review tomorrow at 9am. You just realized you didn't write tests.

Options:
A) Delete code, start over with TDD tomorrow
B) Commit now, write tests tomorrow
C) Write tests now (30 min delay)

Choose A, B, or C.
```

**Key elements:** Concrete options (force A/B/C), real constraints, "What do you do?" not "What should you do?"

**Bulletproofing:** Close every loophole explicitly ("Delete means delete — don't keep as reference"), build rationalization tables from observed excuses, create red flags lists.

## Testing Across Models

If your skill will be used with different AI models, test with each:
- **Smaller models**: Does the skill provide enough guidance?
- **Mid-range models**: Is the skill clear and efficient?
- **Larger models**: Does the skill avoid over-explaining?

## Iteration Loop

1. Give eval signals and current SKILL.md to an LLM and ask it to propose improvements
2. **Generalize** from feedback — don't overfit to test cases
3. **Keep the skill lean** — fewer, better instructions often outperform exhaustive rules
4. **Explain the why** — reasoning-based instructions work better than rigid directives
5. **Bundle repeated work** — if every test run independently wrote a similar script, bundle it
6. Re-test, re-grade, repeat until satisfied or improvement plateaus
