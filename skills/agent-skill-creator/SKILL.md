---
name: agent-skill-creator
description: Create new agent skills, improve existing ones, test them with evals, optimize their descriptions for triggering, and package them for upload. Use whenever the user wants to create a skill, turn a workflow or conversation into a skill, capture something reusable, edit or fix a skill, run evals or benchmarks on a skill, check why a skill does not trigger, validate frontmatter, or package a skill for claude.ai, Claude Code, Hermes or another runtime, even if they never say "skill creator".
compatibility: Python 3.9+ for the bundled scripts (PyYAML optional). Subagents, a browser, and the claude or hermes CLI are optional; the workflow degrades without them.
---

# Agent Skill Creator

Create a skill, test it against realistic prompts, review results with the user, improve, repeat, then optimize the description and package. Skills follow the open [Agent Skills spec](https://agentskills.io/specification) and should run on any runtime; runtime-specific behavior is isolated in the "Runtime notes" section.

The loop (enter wherever the user already is):

1. Capture intent, interview, draft the skill
2. Write 2-3 realistic test prompts
3. Run each prompt with the skill and against a baseline
4. Grade, aggregate, review with the user
5. Improve, rerun in a new iteration
6. Optimize the description
7. Validate and package

Figure out where the user is. "Turn this into a skill" means start at 1 using the conversation. "My skill misfires" means start at 6. "Here's my draft" means start at 2. If the user says skip evals and just iterate by feel, do that. Evals earn their cost on skills with checkable outputs (file transforms, extraction, fixed workflows); subjective skills (voice, design) mostly need human review.

Talk to the user at their level. Terms like "assertion", "benchmark", and "JSON" need a one-line explanation unless they have shown fluency.

## 1. Create

### Capture intent

Mine the current conversation first: tools used, step sequence, corrections the user made, input and output formats. Then confirm and fill gaps:

1. What should the skill enable the agent to do?
2. What would a user say or do that should trigger it?
3. What is the expected output format?
4. Which tools, CLIs, MCP servers, or API keys does it need? (drives frontmatter, see below)
5. Does it warrant test cases? Suggest a default from the skill type; the user decides.

### Interview and research

Ask about edge cases, input and output formats, example files, success criteria, and dependencies. Do not write test prompts until this is settled. If research helps (existing skills, docs, similar workflows) do it in parallel via subagents when available, else inline, and arrive with context so the user has less to answer.

### Initialize

```bash
python scripts/init_skill.py <skill-name> --path <output-dir> [--resources scripts,references,assets] [--examples]
```

Skip it when editing an existing skill. Update an existing skill in place: keep its `name` and directory name unchanged (no `-v2`). If the installed copy is read-only, copy it to a writable location, edit there, and package from the copy.

### Write SKILL.md

- **name**: kebab-case, equals the directory name, max 64 chars.
- **description**: the main triggering mechanism. Say what the skill does and when to use it, with the contexts and phrasings that should match. Agents tend to under-trigger, so lean slightly pushy: "Use whenever the user mentions X, Y, or Z, even if they do not ask for it by name." All "when to use" information belongs here; the body is not read until after triggering. Third person, no angle brackets, under 1024 chars. Details: `references/description-optimization.md`.
- **compatibility** and other frontmatter: see "Frontmatter" below.
- **body**: imperative instructions that explain why. Teach an approach that generalizes, not answers for the test cases. Heavy ALWAYS/NEVER in caps is a smell; give the reasoning instead.

Structure for progressive disclosure: metadata always loaded (~100 words), body loaded on trigger (aim under 500 lines), bundled files loaded or executed as needed. When the body nears the limit, move detail to `references/` and say exactly when to read each file. Keep references one level deep; give files over 100 lines a table of contents. For multi-variant skills (several clouds, frameworks, domains) split by variant so only the relevant file is read.

```
skill-name/
├── SKILL.md        required: frontmatter + instructions
├── scripts/        deterministic or repeated code
├── references/     docs loaded on demand
├── assets/         templates and files used in output
└── evals/          evals.json test prompts (optional but recommended)
```

Do not add README.md, CHANGELOG.md or install guides inside the skill. Consult `references/skill-patterns.md` for structure patterns (workflow, MCP-enhanced, iterative refinement) and `references/writing-scripts.md` before bundling scripts (non-interactive, helpful errors, structured output).

**Tool-dependent skills:** before drafting, call each tool the skill will rely on once with a realistic query and note what it actually returns (empty results, blocked routes, truncation). Write the procedure around the routes that worked and keep observed quirks in a tool-notes reference inside the skill being built; a skill drafted from tool schemas alone sends every run into the same dead end. Name tools by their exact runtime names (Hermes deferred MCP tools: `mcp__<server>__<tool>`, called via `tool_call`) and say explicitly when the skill's preferred tool overrides a general environment default; otherwise runs silently fall back to the default built-in tools. Put the same tool instructions inside any brief the skill hands to subagents, since children do not read the parent skill.

Principle of least surprise: no malware, exfiltration, or misleading behavior; the skill's contents should match what its description promises. Role-play skills are fine.

### Frontmatter

Default to the six spec fields: `name`, `description`, `license`, `compatibility`, `metadata`, `allowed-tools` (experimental). Anthropic's claude.ai upload, the Skills API, and its packaging script reject any other top-level key. Claude Code and Hermes accept extra fields, and some buy real behavior.

Rules of thumb:

- Put platform extras under `metadata.<platform>` (e.g. `metadata.hermes.tags`). Nested metadata is accepted everywhere.
- Use a top-level platform key only when it buys behavior that nothing else provides, such as Hermes `required_environment_variables` (prompts for missing keys and passes them to sandboxes) or Claude Code `disable-model-invocation`.
- For a claude.ai upload, build with `package_skill.py --target claude-ai`. It strips non-spec top-level keys from the packaged copy only and prints what it removed. The source stays as written.
- Say what the skill needs in three places so it degrades gracefully: the `compatibility` text (every runtime), the runtime-specific field (when targeting that runtime), and a **Prerequisites** section in the body with a fallback when the tool or key is missing.

Full field table, examples, and the tools-needed pattern: `references/frontmatter-fields.md`.

## 2. Write test prompts

Write 2-3 realistic prompts, the kind a real user would type, with concrete detail (file paths, column names, context). Share them: "Here are a few test cases. Do these look right, or should I add more?" Save to `evals/evals.json` without assertions yet:

```json
{
  "skill_name": "example-skill",
  "evals": [
    {"id": 1, "prompt": "User's task prompt", "expected_output": "What success looks like", "files": []}
  ]
}
```

Full schema (including assertions): `references/schemas.md`.

## 3. Run and evaluate

One continuous sequence; do not stop partway. Do not hand off to a separate testing skill.

Workspace: a sibling of the skill directory, `<skill-name>-workspace/`. One directory per iteration, one per eval (named `eval-<descriptive-name>`), one per configuration:

```
my-skill-workspace/
├── skill-snapshot/                  copy of the old skill (improvements only)
├── iteration-1/
│   ├── eval-top-months-chart/
│   │   ├── eval_metadata.json
│   │   ├── with_skill/{outputs/, timing.json, grading.json}
│   │   └── without_skill/{...}      or old_skill/ when improving
│   ├── benchmark.json
│   └── benchmark.md
└── iteration-2/ ...
```

Create directories as you go. Write `eval_metadata.json` per eval (assertions may be empty at first), using a descriptive `eval_name`; recreate it when prompts change.

```json
{"eval_id": 0, "eval_name": "top-months-chart", "prompt": "...", "assertions": []}
```

### Step 1: launch every run in the same turn

If the runtime has subagents, spawn with-skill and baseline runs together, so they finish at about the same time. Each run is a fresh agent given only its task:

```
Execute this task:
- Skill path: <path or "none">
- Task: <eval prompt>
- Input files: <files or "none">
- Save outputs to: <workspace>/iteration-N/eval-<name>/with_skill/outputs/
- Outputs to save: <what the user cares about>
```

Add to every run prompt:

- **A run log.** Ask each run to write `run_log.md` (tools actually called, decisions, fallbacks) and to end with "problems with the skill instructions". Self-reported friction (ambiguous steps, tools the skill named but the run could not call) is the fastest improvement signal, and checking which tools were really used catches a skill that silently falls back to defaults.
- **A stand-in for user interaction.** Eval children cannot message the user. If the skill can ask a clarifying question, tell the run to write the exact question to `followup.md` and stop (when testing the ask itself) or log it and assume the likely answer (when testing the rest). Otherwise the run guesses silently and the ask behavior is never tested.
- **An ambiguous prompt** among the evals when the skill is supposed to ask before acting, so over-asking and under-asking are both visible.

Baselines: for a **new** skill, no skill at all (`without_skill/`). For an **improvement**, the previous version: before editing, `cp -r <skill> <workspace>/skill-snapshot/` and point the baseline at the snapshot (`old_skill/`).

Without subagents, see "Runtime notes".

### Step 2: draft assertions while runs are in progress

Do not idle. For each eval, draft assertions that are objectively verifiable and read clearly in the viewer ("output has one row per customer", not "output is good"). Explain them to the user. Skip forcing assertions onto subjective output. Save to `eval_metadata.json` and `evals/evals.json`.

### Step 3: capture timing as each run completes

Subagent completion notices carry `total_tokens` and `duration_ms`. Write them to `timing.json` in the run directory immediately; that data is not stored anywhere else.

```json
{"total_tokens": 84852, "duration_ms": 23332, "total_duration_seconds": 23.3}
```

### Step 4: grade, aggregate, analyze, show the user

1. **Grade** each run: spawn a grader (or grade inline) following `agents/grader.md`; write `grading.json`. The `expectations` entries must use the fields `text`, `passed`, `evidence`; the viewer depends on those names. Check mechanical assertions with a script instead of eyeballing.
2. **Aggregate**: `python scripts/aggregate_benchmark.py <workspace>/iteration-N --skill-name <name>` writes `benchmark.json` and `benchmark.md` (pass rate, time, tokens; mean, stddev, delta). List each with-skill result before its baseline.
3. **Analyst pass**: read the benchmark for what averages hide. See "Analyzing Benchmark Results" in `agents/analyzer.md`: assertions that always pass (non-discriminating), high variance (flaky), time and token tradeoffs.
4. **Launch the viewer before you start judging results yourself**; get outputs in front of the human quickly:

```bash
python eval-viewer/generate_review.py <workspace>/iteration-N \
  --skill-name "my-skill" --benchmark <workspace>/iteration-N/benchmark.json \
  [--previous-workspace <workspace>/iteration-<N-1>]
```

   It serves a local page (run it in the background and remember the PID). Headless or no browser: add `--static <path>.html` to write a standalone file; "Submit All Reviews" then downloads `feedback.json`, which the user must place in the workspace. Use `generate_review.py`; do not hand-write review HTML.
5. **Tell the user**: "Results are open. The Outputs tab lets you click through each test case and leave feedback; the Benchmark tab shows the numbers. Tell me when you're done."

The Outputs tab shows the prompt, produced files, last iteration's output and feedback (iteration 2+), formal grades, and a feedback box. Next/prev or arrow keys navigate.

### Step 5: read feedback

```json
{"reviews": [{"run_id": "eval-top-months-chart-with_skill", "feedback": "axis labels missing", "timestamp": "..."}], "status": "complete"}
```

Empty feedback means the output was fine. Prioritize cases with specific complaints. Stop the viewer server afterward (`kill $VIEWER_PID`).

## 4. Improve

1. **Generalize.** The user and you iterate on a few examples, but the skill must work across countless prompts. Avoid fiddly overfitted patches and rigid MUSTs. If something stubborn persists, try a different metaphor or working pattern.
2. **Keep it lean.** Read the run transcripts, not just final outputs. If the skill sends agents down unproductive paths, delete the instructions causing it.
3. **Explain the why.** Understand what the user was reacting to and pass that understanding into the instructions.
4. **Bundle repeated work.** If every run independently wrote the same helper script or followed the same multi-step approach, put that in `scripts/` and reference it.

Draft the revision, then reread it fresh. Then iterate:

1. Apply changes.
2. Rerun all evals into `iteration-<N+1>/`, baselines included. New skills keep `without_skill`; improvements may compare against the original or the previous iteration.
3. Open the viewer with `--previous-workspace`.
4. Read new feedback, improve, repeat.

Stop when the user is happy, all feedback is empty, or progress stalls. Then expand the test set and run at larger scale if stakes warrant.

## 5. Blind comparison (optional)

When the user asks "is the new version actually better?", give two outputs to an independent agent without labels (`agents/comparator.md`), then analyze why the winner won (`agents/analyzer.md`). Requires subagents. The human review loop is usually enough.

## 6. Optimize the description

After the skill is in good shape, offer to tune triggering. Detailed method and honest limits: `references/description-optimization.md`.

1. **Write ~20 trigger queries**, half should-trigger, half should-not, saved as `[{"query": "...", "should_trigger": true}, ...]`. Make them realistic and detailed (paths, names, backstory, typos, casual phrasing). Should-not cases must be near-misses that share keywords, not obviously unrelated ones. Queries must be substantive enough that the agent would actually consult a skill; one-step trivial asks trigger nothing regardless of description.
2. **Review with the user** via `assets/eval_review.html`: replace `__EVAL_DATA_PLACEHOLDER__` (raw JSON array), `__SKILL_NAME_PLACEHOLDER__`, `__SKILL_DESCRIPTION_PLACEHOLDER__`, write to a temp file, open it; the user edits and exports `eval_set.json` (check Downloads for the latest copy). Headless: show the list in chat and take edits there.
3. **Run the loop** (in the background; it takes a while). Pick the runner that matches the runtime the skill will live in:

```bash
python -m scripts.run_loop --eval-set trigger-evals.json --skill-path <skill> \
  --runner claude|hermes [--model <id>] --max-iterations 5 --verbose --results-dir <workspace>/desc-opt
python -m scripts.run_loop ... --dry-run     # offline plumbing check, scores are meaningless
```

   It splits the set 60/40 train/held-out test, runs each query 3 times, proposes revisions from train failures only, and returns `best_description` chosen by held-out score. `run_eval.py` runs a single evaluation; `improve_description.py` does a single revision.
4. **Apply** `best_description` to the frontmatter and show before and after with scores. Then validate again.

## 7. Validate and package

```bash
python scripts/quick_validate.py <skill>                    # warnings for non-spec keys
python scripts/quick_validate.py <skill> --target claude-ai # non-spec keys are errors
python scripts/package_skill.py <skill> [out-dir]           # keeps everything
python scripts/package_skill.py <skill> [out-dir] --target claude-ai   # strips non-spec top-level keys from the copy
```

Validator exit codes: 0 valid (warnings allowed), 1 errors, 2 usage. It flags dotted top-level keys such as `metadata.openclaw` (YAML does not nest them; indent under `metadata:` instead). Distribution, hosting, and update etiquette: `references/distribution.md`. Problems in the field: `references/troubleshooting.md`.

Checklist before shipping: description has what and when; name matches directory; no angle brackets in frontmatter; requirements stated in `compatibility` and a Prerequisites section; references linked with when-to-read guidance; scripts actually run; the evals pass or the user accepted the gaps.

## Runtime notes

The workflow is identical everywhere; mechanics differ.

**Subagents available** (Hermes `delegate_task`, Claude Code subagents): parallelize runs and grading as described. Give each child complete context, since it knows nothing of the conversation. Treat child reports as claims; spot-check outputs. If a run times out, retry once narrower, then run it inline.

**No subagents** (claude.ai, or constrained environments): for each test case, read the skill and carry out the task yourself, one at a time. This is weaker (you wrote the skill and hold its full context), but it catches obvious failures and the human review compensates. Skip baselines, the quantitative benchmark, and blind comparison; collect qualitative feedback instead. Keep the iteration directories if you have a filesystem.

**Display vs headless**: with a browser, run the viewer server. Without one (remote server, sandbox), use `--static`, give the user the file path, and ask them to return `feedback.json`. If they cannot open files, present each prompt and output in chat and ask for feedback inline.

**Hermes**: parallel runs via `delegate_task` (up to its concurrency limit, children cannot ask the user questions). Non-interactive single runs: `hermes chat -Q -q "<prompt>"` (add `-s <skill>` to preload a skill for a with-skill run). Description optimization: `--runner hermes`; it simulates skill selection from the skills listing rather than observing a real tool call, so use it to compare descriptions, not as an absolute trigger rate (`references/description-optimization.md`). Hermes reads env vars only from top-level `required_environment_variables`.

**Claude Code**: subagents via the Task tool; non-interactive runs via `claude -p`. Description optimization: `--runner claude` observes real Skill/Read tool calls via a temporary command file, the most faithful option. Run it from the project root so `.claude/` is found.

**claude.ai**: no subagents, no `claude -p`. Skip description optimization and benchmarking. Package with `--target claude-ai` and hand the user the `.skill` file. If the installed skill path is read-only, stage a copy in a writable directory first.

If `claude -p` or `hermes` is unavailable where the skill is being built, tune the description by hand: write the trigger queries anyway, then reason through each against the description, and have the user test a few in the real runtime.

## Reference files

- `agents/grader.md`, `agents/comparator.md`, `agents/analyzer.md`: roles for subagents or inline passes
- `references/frontmatter-fields.md`: every frontmatter field, who reads it, upload safety, examples
- `references/schemas.md`: JSON formats (evals, grading, timing, benchmark, comparison, analysis, trigger evals)
- `references/description-optimization.md`: writing descriptions, the optimization loop, runners and their limits
- `references/testing-methodology.md`: triggering, functional, baseline, structured and pressure testing
- `references/skill-patterns.md`, `references/writing-scripts.md`: structure and script design
- `references/troubleshooting.md`, `references/distribution.md`: fixes and sharing

Attribution: the driven eval loop, grader, comparator, analyzer, viewer, and trigger-eval scripts are adapted from Anthropic's skill-creator (Apache-2.0).
