---
name: openclaw-skill-creator
description: Create, update, test, package, and iteratively improve skills for OpenClaw. Use when designing, structuring, packaging, or evaluating OpenClaw skills with scripts, references, assets, and trigger/quality evals. Triggers include "create a skill", "create an openclaw skill", "turn this into a skill", "capture this workflow", "make this reusable", "package this as a skill", "improve this skill", "update my skill", "test this skill", "eval this skill", "benchmark a skill", "publish to clawhub", or any request to build, improve, or distribute reusable OpenClaw agent capabilities. Covers planning, drafting, agent-profile-based A/B testing, trigger accuracy evals, description optimization, troubleshooting, distribution via ClawHub, and iteration. OpenClaw-specific.
---

# OpenClaw Skill Creator

A skill for creating skills for OpenClaw and iteratively improving them.

OpenClaw skills follow the [AgentSkills](https://agentskills.io) spec with OpenClaw-specific extensions for gating, installation, slash commands, and multi-agent setups. This skill walks you through the full lifecycle: drafting, testing, evaluating, iterating, and shipping.

At a high level, the loop looks like this:

- Decide what the skill should do and roughly how it should do it
- Write a draft of the skill (SKILL.md + any scripts/references/assets it needs)
- Create a few test prompts and run OpenClaw subagents on them (with the skill loaded and without, side-by-side)
- Help the user evaluate the results both qualitatively and quantitatively
  - While the runs happen in the background, draft assertions if there aren't any. Then explain them to the user.
  - Use `eval-viewer/generate_review.py` to show the user the side-by-side outputs
- Rewrite the skill based on user feedback and any glaring patterns from the benchmark
- Repeat until you and the user are happy
- Optionally, run the description-optimization loop to dial in trigger accuracy
- Package the skill (`.skill` bundle for direct sharing, or publish via ClawHub)

Your job when using this skill is to figure out where the user is in this loop and meet them there. They might say "I want to make a skill for X" — in which case you start at the top, narrow down what they want, draft, test, iterate. Or they might already have a draft, in which case you go straight to the eval/iterate part. Or they might say "just vibe with me and skip the formal evals" — that's fine too, follow their lead.

## Communicating with the user

Skill creation attracts users across a wide range of technical familiarity. Some are seasoned engineers; some are plumbers or grandparents who just discovered they can `npm install` things. Pay attention to context cues from the user's phrasing and adjust your communication.

In the default case, just to give you some idea:

- "evaluation" and "benchmark" are borderline-OK without explanation
- "JSON", "frontmatter", "assertion" → look for cues that the user knows these terms before using them naked
- "agent profile", "session spawn", "subagent" → OpenClaw-specific; brief inline explanation is usually appreciated

Brief term clarifications are fine. Don't assume; don't lecture either.

---

## OpenClaw-Specific Things You Need to Know Up Front

These constraints shape the rest of the workflow. Read them before you do anything else.

### 1. Skill visibility is set at the agent profile level, not per-spawn

OpenClaw doesn't have an Anthropic-style Task tool where you pass a skill path to each subagent. Instead, **each agent profile** in `~/.openclaw/openclaw.json` has a `skills: [...]` list that determines which skills it can see. To A/B test a skill, you create two temporary agent profiles — one *with* the skill in its list, one *without* — and spawn subagents at each profile via `sessions_spawn`. There's a helper for this: `{baseDir}/scripts/trigger_eval/setup_agents.sh <skill-name>`.

This is the single biggest workflow difference from the Anthropic skill-creator. Internalize it before drafting test runs.

### 2. Skill changes need a session boundary or hot reload

OpenClaw snapshots eligible skills when a session starts. Edits to a skill take effect on the next *new* session, unless the skills watcher hot-reloads them. After editing a skill mid-iteration, restart the gateway (`openclaw gateway restart`) or ask the agent to "refresh skills" — otherwise your subagents will run against the stale snapshot.

### 3. Detecting whether a skill was consulted is heuristic

OpenClaw subagents don't emit a "skill loaded" event. To detect whether a subagent actually consulted a skill, you analyze its `sessions_history` for a `read` tool call whose path matches `<skill-name>/SKILL.md`. The helper `{baseDir}/scripts/trigger_eval/orchestrator.py` does this — see its `detect_skill_consultation()` function. It's accurate enough for trigger-rate evals but not perfect.

### 4. Skill locations and precedence

Skills load from three places (highest to lowest precedence):

1. **Workspace skills**: `<workspace>/skills` — per-agent
2. **Managed/local skills**: `~/.openclaw/skills` — shared across all agents on the machine
3. **Bundled skills**: shipped with the install

Workspace wins over managed, which wins over bundled. Use this to override or patch a bundled skill without modifying it. For multi-agent setups, place per-agent skills in the workspace and shared ones in `~/.openclaw/skills`.

---

## Creating a skill

### Capture intent

Start by understanding the user's intent. The current conversation might already contain a workflow the user wants to capture (e.g., they say "turn this into a skill"). If so, extract answers from the conversation history first — the tools used, the sequence of steps, corrections the user made, input/output formats observed. Confirm with the user before proceeding.

Get answers (or strong-confidence inferences) for:

1. What should this skill enable an OpenClaw agent to do?
2. When should this skill trigger? (what user phrases/contexts)
3. What's the expected output format?
4. Does this skill need external binaries, env vars, or API keys? (determines `metadata.openclaw.requires` gating)
5. Should this be agent-only, slash-command-only, or both?
6. Should we set up test cases to verify it works? Skills with objectively verifiable outputs (file transforms, data extraction, code generation, fixed workflow steps) benefit from test cases. Skills with subjective outputs (writing style, art) often don't. Suggest the appropriate default but let the user decide.

Avoid overwhelming the user with all six at once — ask in the order that's most relevant to what they've already shared.

### Interview and research

Proactively ask about edge cases, input/output formats, example files, success criteria, dependencies. Wait to write test prompts until this part is settled.

If useful, research in parallel via subagents — search docs, look for similar existing skills under `skills/`, look up the binary or API the skill will wrap. Come prepared with context to reduce burden on the user.

### Initialize the skill scaffold

Run `{baseDir}/scripts/init_skill.py <skill-name> --path <output-dir>` to scaffold a skeleton with SKILL.md template, OpenClaw metadata placeholder, and optional resource directories.

```bash
{baseDir}/scripts/init_skill.py my-skill --path skills/
{baseDir}/scripts/init_skill.py my-skill --path ~/.openclaw/skills --resources scripts,references
{baseDir}/scripts/init_skill.py my-skill --path skills/ --gated         # adds metadata.openclaw.requires
{baseDir}/scripts/init_skill.py my-skill --path skills/ --slash-command browser_search
```

### Write the SKILL.md

Based on the interview, fill in:

- **`name`** — kebab-case identifier matching the folder name. Max 64 chars, no consecutive hyphens, no XML angle brackets.
- **`description`** — Both *what the skill does* AND *when to trigger it*. This is the primary triggering mechanism — include specific contexts and trigger phrases. All "when to use" info goes here, not in the body. Be slightly "pushy": OpenClaw skills tend to undertrigger, so explicit "use when…" phrases help. Max 1024 chars, no XML angle brackets, third person.
- **`metadata.openclaw`** — single-line JSON with `requires` (bins/env/config), `primaryEnv`, `os`, `install`, `emoji`, `homepage`. Critical: it must be a single line; OpenClaw's parser doesn't support multi-line metadata values.
- **`user-invocable` / `disable-model-invocation` / `command-dispatch` / `command-tool`** — only if the skill should be exposed as a slash command or dispatch directly to a tool.
- **The body** — workflow instructions for the agent. Use `{baseDir}` to reference the skill's own folder at runtime.

For deep-dive specs on frontmatter fields, OpenClaw metadata schema, gating, installer specs, slash commands, and the full security restriction list, read `references/openclaw-config.md`. For description-writing pitfalls and the critical "description = when to use, NOT what it does" rule, read `references/description-optimization.md`. For skill organization patterns (standalone, workflow automation, gated, slash command, iterative refinement), read `references/skill-patterns.md`. For the writing style and progressive-disclosure rules (keep SKILL.md under 500 lines, push detail into references, explain the *why* rather than barking ALWAYS/NEVER), see the "Skill Writing Guide" section below.

### Skill Writing Guide

#### Anatomy

```
skill-name/
├── SKILL.md (required)
│   ├── YAML frontmatter (name, description required; OpenClaw metadata optional)
│   └── Markdown instructions
└── Bundled Resources (optional)
    ├── scripts/    — Executable code for deterministic/repetitive tasks
    ├── references/ — Docs loaded into context as needed
    └── assets/     — Files used in output (templates, icons, fonts)
```

#### Progressive disclosure

Skills load in three levels:

1. **Metadata** (name + description) — Always in context. The agent reads this to decide whether to load the skill.
2. **SKILL.md body** — Loaded when the skill triggers. Target under 500 lines. If you're approaching that limit, split detail into references and add clear pointers from the body.
3. **Bundled resources** — Loaded as needed. Scripts can execute without consuming context. References load only when relevant. Assets are used in output, never loaded into context.

**Domain organization**: When a skill supports multiple variants (e.g., different cloud providers), organize by variant in references and let the SKILL.md body select which to read. The model only loads the relevant one.

#### Writing patterns

Prefer imperative form. Explain *why* — today's models have good theory of mind and respond better to reasoning than to rigid commands. If you find yourself writing ALWAYS or NEVER in caps, that's a yellow flag — reframe and explain the underlying reason.

Teach approaches, not answers. The skill will be used across many prompts, not just the test cases you used to build it. Avoid overfitting.

Use `{baseDir}` to reference the skill's own folder path in instructions — runtime resolves it.

### Test cases

After writing the draft, come up with 2–3 realistic test prompts — the kind of thing a real user would actually say. Share them with the user: "Here are a few test cases I'd like to try. Do these look right, or do you want to add more?" Then run them.

Save the test cases to `evals/evals.json`. Don't write assertions yet — just the prompts. You'll draft assertions in the next step while the runs are in progress.

```json
{
  "skill_name": "my-skill",
  "evals": [
    {
      "id": 1,
      "name": "descriptive-test-name",
      "prompt": "User's task prompt with realistic detail",
      "should_trigger": true,
      "expected_output": "Description of what good looks like",
      "files": [],
      "assertions": []
    }
  ]
}
```

See `references/schemas.md` for the full schema, including the `assertions` field you'll add later. Test prompts should be realistic — file paths, column names, casual phrasing, abbreviations, real context. Include at least one edge case.

---

## Running and evaluating test cases

This section is one continuous sequence — don't stop partway through.

Put results in `<skill-name>-workspace/` as a sibling to the skill directory. Within the workspace, organize results by iteration (`iteration-1/`, `iteration-2/`, etc.) and within that, each test case gets a directory (`eval-<descriptive-name>/`). Don't create all of this upfront — let the helper scripts create directories as you go.

### Step 0: Set up eval agent profiles

This step is unique to OpenClaw. Because skill visibility is set at the agent-profile level (see "OpenClaw-Specific Things You Need to Know Up Front" above), you can't just spawn a subagent and pass a skill path. You need two agent profiles: one with the skill in its `skills:` list, one without.

Run the helper:

```bash
{baseDir}/scripts/trigger_eval/setup_agents.sh <skill-name>
```

This:

1. Backs up `~/.openclaw/openclaw.json` to `/tmp/skill-eval-config-backup-<skill-name>.json`
2. Adds two agent profiles to `agents.list`:
   - `eval-with-<skill-name>` with `skills: ["<skill-name>"]`
   - `eval-without-<skill-name>` with `skills: []`
3. Tells you to run `openclaw gateway restart` so the new profiles take effect

Tell the user: "I've added two temporary eval agent profiles to your OpenClaw config. After we're done iterating, I'll run `setup_agents.sh <skill-name> --cleanup` to restore your original config."

If you're improving an existing skill (rather than creating one), the baseline depends on what you're comparing against. Snapshot the old version before editing (`cp -r <skill-path> <workspace>/skill-snapshot/`) and create a third agent profile pointing at the snapshot if you want a true "old vs new" comparison. For most cases, the with-skill / without-skill split is enough.

### Step 1: Prepare the workspace and spawn all runs in the same turn

First, prep the workspace and per-eval scaffolding:

```bash
{baseDir}/scripts/trigger_eval/run_eval.sh <skill-name> \
  --eval-set evals/evals.json \
  --workspace <skill-name>-workspace
```

This creates `<skill-name>-workspace/iteration-1/eval-<id>/` directories, copies the eval set, writes a `run_config.json`, and seeds an `eval_metadata.json` for each test case.

Then for each test case, spawn **two** subagents in the same turn — one at the with-skill profile, one at the without-skill profile. Don't spawn the with-skill runs first and come back for baselines later — launch everything at once so they all finish around the same time.

Use OpenClaw's `sessions_spawn` (not Claude Code's Task tool). Each spawn call needs:

- `agentId`: `eval-with-<skill-name>` or `eval-without-<skill-name>`
- `task`: the eval prompt verbatim
- A label or session key you can correlate back to the eval

If you're driving spawns programmatically, `{baseDir}/scripts/trigger_eval/orchestrator.py` can generate a structured spawn plan from the eval set:

```bash
{baseDir}/scripts/trigger_eval/orchestrator.py <skill-name>-workspace --skill-name <skill-name> --action plan
```

This writes `spawn_plan.json` to the workspace listing every spawn the agent should issue.

### Step 2: While runs are in progress, draft assertions

Don't sit idle. Draft quantitative assertions for each test case while the spawns run.

Good assertions are objectively verifiable and have descriptive names — they should read clearly in the benchmark viewer so anyone glancing at the results immediately understands what each one checks. Subjective skills (writing style, design quality) are better evaluated qualitatively — don't force assertions onto things that need human judgment.

Common assertion types (see `references/schemas.md` for the full list):

- `skill_consulted` / `skill_not_consulted` — did the agent read the SKILL.md?
- `output_contains` / `output_not_contains` — regex match against output text
- `tool_used` — a specific tool was called during execution
- Custom file/format assertions — wrote a `.docx`, valid JSON, correct row count, etc.

For assertions checkable by code (file exists, valid JSON, correct row count), write a verification script and run it — scripts are more reliable than LLM judgment for mechanical checks, and you can reuse them across iterations.

Update `eval_metadata.json` for each eval and `evals/evals.json` with the assertions you've drafted. Then explain to the user what they'll see in the viewer — both the qualitative outputs and the quantitative benchmark.

### Step 3: As runs complete, capture timing and record results

When each `sessions_spawn` completes, record the result with:

```bash
{baseDir}/scripts/trigger_eval/record_result.sh <eval-dir> \
  --side with_skill \
  --triggered true \
  --output "<truncated output>" \
  --tokens 8472 \
  --duration_ms 23332
```

To determine `--triggered`, fetch `sessions_history` for the spawned session and run it through `orchestrator.py`'s `detect_skill_consultation()` (or call `orchestrator.py --action detect --session-history <path>` directly). The detector looks for `read` tool calls referencing `<skill-name>/SKILL.md` in the session history.

Process each notification as it arrives rather than batching them — timing data is only available at the moment the spawn completes.

### Step 4: Grade, aggregate, and launch the viewer

Once all runs are done:

1. **Grade each run.** For trigger-accuracy mode, use the bash grader:

   ```bash
   {baseDir}/scripts/trigger_eval/grade.sh <skill-name>-workspace --skill-name <skill-name>
   ```

   This produces a basic `benchmark.json` keyed on whether `triggered` matched `should_trigger` for each eval. For quality-mode evaluation against assertions, spawn a grader subagent with `agents/grader.md` instructions, or grade inline. Save grading results to `grading.json` in each run directory. The grading.json `expectations` array must use fields `text`, `passed`, and `evidence` — the viewer depends on these exact field names.

2. **Aggregate into a richer benchmark.** For multi-assertion quality evals:

   ```bash
   {baseDir}/scripts/aggregate_benchmark.py <skill-name>-workspace/iteration-1 --skill-name <skill-name>
   ```

   This produces `benchmark.json` and `benchmark.md` with pass_rate, time, and tokens for each configuration, with mean ± stddev and the delta. Put each with_skill version before its baseline counterpart in the output.

3. **Do an analyst pass.** Read the benchmark data and surface patterns the aggregate stats might hide. See `agents/analyzer.md` for what to look for — assertions that always pass regardless of skill (non-discriminating), high-variance evals (possibly flaky), time/token tradeoffs, etc.

4. **Launch the viewer:**

   ```bash
   nohup python {baseDir}/eval-viewer/generate_review.py \
     <skill-name>-workspace/iteration-1 \
     --skill-name "<skill-name>" \
     --benchmark <skill-name>-workspace/iteration-1/benchmark.json \
     > /dev/null 2>&1 &
   VIEWER_PID=$!
   ```

   For iteration 2+, also pass `--previous-workspace <skill-name>-workspace/iteration-<N-1>` so the viewer shows side-by-side comparisons with the previous iteration's outputs and the user's previous feedback.

   **Headless or no-display environments:** use `--static <output_path>` to write a standalone HTML file instead of starting a server. Feedback will be downloaded as `feedback.json` when the user clicks "Submit All Reviews". After download, copy it into the workspace directory for the next iteration to pick up.

   Use `generate_review.py` — don't write your own boutique HTML.

5. **Tell the user** something like: "I've opened the results in your browser. The 'Outputs' tab lets you click through each test case and leave feedback; 'Benchmark' shows the quantitative comparison. When you're done, come back here and let me know."

### What the user sees in the viewer

The "Outputs" tab shows one test case at a time:

- **Prompt**: the task that was given
- **Output**: the files the skill produced, rendered inline where possible
- **Previous Output** (iteration 2+): collapsed section showing last iteration's output
- **Formal Grades** (if grading was run): collapsed section showing assertion pass/fail
- **Feedback**: a textbox that auto-saves as they type
- **Previous Feedback** (iteration 2+): their comments from last time, shown below the textbox

The "Benchmark" tab shows the stats summary: pass rates, timing, and token usage for each configuration, with per-eval breakdowns.

Navigation is via prev/next buttons or arrow keys. When done, they click "Submit All Reviews" which saves all feedback to `feedback.json`.

### Step 5: Read the feedback

When the user tells you they're done, read `feedback.json`:

```json
{
  "reviews": [
    {"run_id": "eval-0-with_skill", "feedback": "the chart is missing axis labels", "timestamp": "..."},
    {"run_id": "eval-1-with_skill", "feedback": "", "timestamp": "..."},
    {"run_id": "eval-2-with_skill", "feedback": "perfect, love this", "timestamp": "..."}
  ],
  "status": "complete"
}
```

Empty feedback means the user thought it was fine. Focus your improvements on the test cases where the user had specific complaints.

Kill the viewer and clean up the eval agent profiles when you're done with this iteration:

```bash
kill $VIEWER_PID 2>/dev/null
# Only run cleanup once you're fully done iterating, not between iterations:
# {baseDir}/scripts/trigger_eval/setup_agents.sh <skill-name> --cleanup
```

---

## Improving the skill

This is the heart of the loop. You've run the test cases, the user has reviewed the results, and now you need to make the skill better based on their feedback.

### How to think about improvements

1. **Generalize from the feedback.** The skill will be used across many prompts, not just the 2–3 you tested. The user knows their test cases inside and out and can assess outputs quickly, which is why iterating against a small set works — but if the skill only works for *those* examples, it's useless. Rather than fiddly overfitting changes or oppressive ALL-CAPS rules, try branching out and using different framings or recommending different patterns of working. It's cheap to try and you might land on something great.

2. **Keep instructions lean.** Remove things that aren't pulling weight. Read the subagent transcripts (not just the outputs) — if the skill is making the agent waste time on unproductive steps, cut those instructions and see what happens.

3. **Explain the why.** Today's models are smart and have good theory of mind. Even if the user's feedback is terse or frustrated, try to understand what they actually want and transmit that understanding into the instructions. If you find yourself writing ALWAYS or NEVER in all caps, or using rigid structures, that's a yellow flag — reframe with reasoning so the model understands *why* the thing you're asking for matters.

4. **Look for repeated work across test cases.** If all 3 test runs independently wrote a `create_docx.py` or a `build_chart.py`, that's a strong signal the skill should bundle that script. Write it once, drop it in `scripts/`, and reference it from the SKILL.md. This saves every future invocation from reinventing the wheel.

This task matters. Your thinking time is not the blocker — take your time, write a draft revision, look at it with fresh eyes, improve it. Get into the user's head.

### The iteration loop

After improving the skill:

1. Apply your improvements to the skill files
2. Restart the OpenClaw gateway (or trigger a hot reload) so the new version is snapshotted for the next session
3. Rerun all test cases into a new `iteration-<N+1>/` directory, including baseline runs. For new skills, baseline is always `without_skill`. For improving an existing skill, use your judgment — original version, or previous iteration.
4. Launch the viewer with `--previous-workspace` pointing at the previous iteration
5. Wait for the user to review and tell you they're done
6. Read the new feedback, improve again, repeat

Keep going until the user says they're happy, all feedback is empty, or you're not making meaningful progress.

---

## Description Optimization

The `description` field is the primary mechanism that determines whether OpenClaw loads a skill. After creating or improving a skill, offer to optimize the description for better triggering accuracy.

The full methodology — train/validation splits, structured iteration loop, anti-overfitting tactics — lives in `references/description-optimization.md`. Read that file before running the loop. The high-level shape is:

1. **Generate ~20 trigger eval queries** (8–10 should-trigger, 8–10 should-not-trigger). The most valuable should-not-trigger queries are *near misses* — queries that share keywords but actually need a different skill. Avoid obviously irrelevant negatives like "write a fibonacci function" for a PDF skill — they don't test anything.

2. **Review the eval set with the user** using `assets/eval_review.html`. Replace `__EVAL_DATA_PLACEHOLDER__`, `__SKILL_NAME_PLACEHOLDER__`, `__SKILL_DESCRIPTION_PLACEHOLDER__`, save to a temp file, and open it. The user can edit queries, toggle should-trigger, add/remove entries, and export the final set.

3. **Split the set 60/40** into train and validation. Keep the split fixed across iterations.

4. **Run the trigger eval loop.** OpenClaw doesn't have a one-shot `run_loop.py` like Anthropic's harness, but the components exist:
   - Use `setup_agents.sh` to ensure the eval agent profiles exist
   - For each query, spawn a subagent at `eval-with-<skill-name>` and check whether it consulted the skill (via `orchestrator.py`'s detection)
   - Run each query 3× to account for nondeterminism
   - Compute trigger rate on the train set, identify failures, revise the description, re-run on train, then validate on the held-out test set
   - Iterate up to ~5 times. Select the best iteration by *test* score, not train score, to avoid overfitting.

5. **Apply the winning description** to the skill's frontmatter. Show the user before/after and report the scores.

For the rationale behind each step (especially the critical "description = when to use, NOT what it does" rule and the train/test split), `references/description-optimization.md` is the source of truth.

---

## Packaging and Distribution

Once the skill is in good shape, the user has two main options for sharing it:

### Option 1: ClawHub (recommended for public/shared distribution)

ClawHub is OpenClaw's first-party skill registry. Users install skills via `clawhub install <skill-name>` and update with `clawhub update`. For multi-machine setups, `clawhub sync` keeps installations in sync.

To publish, follow `references/distribution.md` — it covers ClawHub publication, the metadata fields the registry expects, and how to handle updates.

### Option 2: `.skill` bundle (for direct sharing or GitHub)

For one-off sharing, GitHub distribution, or environments without ClawHub access:

```bash
{baseDir}/scripts/package_skill.py <path/to/skill-folder>
```

This produces a `.skill` file the user can drop into `~/.openclaw/skills/` or share directly.

### Option 3: Plugin-shipped skills

Skills can ship inside an OpenClaw plugin (npm package). See `references/distribution.md` for the plugin packaging format.

Before packaging or publishing, validate the skill:

```bash
{baseDir}/scripts/quick_validate.py <path/to/skill-folder>
```

This checks frontmatter syntax, OpenClaw metadata structure (single-line JSON, valid `requires` shape, consistent `command-dispatch` config), security restrictions (no XML angle brackets), and naming conventions.

---

## Reference Files

The `agents/` directory contains instructions for specialized subagents. Read them when you need to spawn the relevant subagent:

- `agents/grader.md` — How to evaluate assertions against outputs
- `agents/comparator.md` — How to do blind A/B comparison between two outputs (skill v1 vs skill v2)
- `agents/analyzer.md` — How to analyze patterns in benchmark results

The `references/` directory has additional documentation:

- `references/openclaw-config.md` — OpenClaw metadata schema, gating, installer specs, slash command config, security restrictions, `~/.openclaw/openclaw.json` overrides
- `references/skill-patterns.md` — Categories of skills with examples (standalone, workflow automation, CLI-enhanced, slash command, gated, problem-first, tool-first, iterative refinement)
- `references/description-optimization.md` — The full description-optimization methodology, including the train/validation split and the "description = when to use" rule
- `references/testing-methodology.md` — Testing tiers, assertion design, baseline comparison, blind comparison, pressure testing for discipline-enforcing skills
- `references/schemas.md` — JSON structures for `evals.json`, `eval_metadata.json`, `grading.json`, `benchmark.json`, `comparison.json`, `analysis.json`
- `references/writing-scripts.md` — Design guidance for bundled scripts (non-interactive, idempotent, clear errors)
- `references/distribution.md` — ClawHub publication, plugin-shipped skills, `.skill` bundling
- `references/troubleshooting.md` — Common issues: skill not appearing (gating issues), metadata JSON parse errors, slash command not working, gating not filtering correctly

The `scripts/` directory has the helper scripts:

- `scripts/init_skill.py` — Scaffold a new skill directory with templates
- `scripts/quick_validate.py` — Validate frontmatter and OpenClaw metadata
- `scripts/aggregate_benchmark.py` — Aggregate per-eval results into a benchmark
- `scripts/generate_report.py` — Generate HTML reports from benchmark data
- `scripts/package_skill.py` — Package a skill folder into a `.skill` bundle
- `scripts/trigger_eval/setup_agents.sh` — Create temporary `eval-with-X` / `eval-without-X` agent profiles
- `scripts/trigger_eval/run_eval.sh` — Prepare the eval workspace and per-eval scaffolding
- `scripts/trigger_eval/orchestrator.py` — Generate spawn plan, detect skill consultation in session history
- `scripts/trigger_eval/record_result.sh` — Record a single subagent run's result into the workspace
- `scripts/trigger_eval/grade.sh` — Grade trigger-accuracy results and produce a basic `benchmark.json`
- `scripts/trigger_eval/report.sh` — Generate a markdown trigger eval report
- `scripts/trigger_eval/generate_evals.sh` — Generate a starter eval set template from a skill's description

---

Repeating the core loop one more time for emphasis:

- Figure out what the skill is about
- Draft or edit the skill (use `init_skill.py` to scaffold)
- Set up the eval agent profiles (`setup_agents.sh`) — OpenClaw-specific
- Run subagents at the with-skill and without-skill profiles on the test prompts
- Generate `benchmark.json` and run `eval-viewer/generate_review.py` so the human can review
- Read feedback, improve the skill, restart the gateway, repeat
- Optionally, run the description-optimization loop
- Validate (`quick_validate.py`) and package (`package_skill.py`) or publish to ClawHub

Good luck.
