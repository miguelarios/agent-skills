# skill-creator

An agent-agnostic skill for creating, testing, and packaging Agent Skills — the open standard for extending AI agent capabilities.

Built by synthesizing the best practices from every major skill-creation reference available as of March 2026, including Anthropic's built-in skill-creator, their PDF guide, the agentskills.io open specification, and community skill-creators from OpenClaw and Superpowers.

## Structure

```
skill-creator/
├── SKILL.md
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
    └── quick_validate.py
```

## File Provenance

### SKILL.md (325 lines — original)

The procedural core. Covers core principles, anatomy, frontmatter spec, progressive disclosure patterns, skill creation process (7 steps), and a quick checklist. Stays under 500 lines by pushing depth into reference files.

**Sources synthesized:**
- **Anthropic built-in skill-creator** — "explain the why" writing philosophy, iterative improvement guidance, generalize-don't-overfit principle
- **Anthropic PDF guide (Complete Guide to Building Skills)** — all six skill pattern categories, complete YAML frontmatter spec with optional fields, three-level progressive disclosure model
- **OpenClaw V2 skill-creator** — 6-step creation process, concrete planning examples (PDF → script, webapp → template, BigQuery → schema), "What NOT to Include" section
- **Superpowers writing-skills** — CSO insight referenced in description section, naming conventions (gerund-first)
- **agentskills.io** — "favor procedures over declarations" principle, "design coherent units" scoping guidance, gotchas as iteration signal

---

### references/description-optimization.md (166 lines — original)

In-depth guide to writing and systematically optimizing the `description` field for triggering accuracy.

**Sources synthesized:**
- **Superpowers writing-skills (CSO section)** — The critical finding that descriptions summarizing workflow cause the AI to shortcut and skip the SKILL.md body. The "description = when to use, NOT what it does" rule. Good/bad examples with concrete before/after.
- **Anthropic PDF guide** — Good/bad description examples, trigger phrase guidance, negative trigger patterns for overtriggering
- **agentskills.io (optimizing-descriptions.md)** — Train/validation split methodology (60/40), overfitting prevention, trigger rate computation with 3x runs per query, 5-iteration optimization loop, selecting by validation score not train score
- **Anthropic built-in skill-creator** — "Pushy" descriptions to combat undertriggering

### references/distribution.md (105 lines — original)

Packaging, GitHub hosting, MCP integration documentation, positioning advice.

**Sources synthesized:**
- **Anthropic PDF guide (Chapter 4)** — GitHub repo structure (README at repo level, not in skill folder), installation guides for MCP-enhanced skills, positioning guidance (outcomes not features)
- **OpenClaw V2 skill-creator** — Packaging workflow with `.skill` files, MCP integration documentation template
- **Anthropic built-in skill-creator** — Packaging via `package_skill.py`, updating existing skills guidance

### references/schemas.md (430 lines — from Anthropic built-in skill-creator)

Complete JSON format definitions for every file in the eval ecosystem: `evals.json`, `grading.json`, `timing.json`, `benchmark.json`, `comparison.json`, `analysis.json`, `history.json`, and `metrics.json`.

**Source:** Directly from Anthropic's built-in skill-creator (`references/schemas.md`). Model name in the benchmark example changed from `claude-sonnet-4-20250514` to `<model-name>` for agent-agnosticism. Otherwise unmodified — these are the canonical format definitions the eval tooling expects.

### references/skill-patterns.md (239 lines — original)

Detailed examples for six skill pattern types plus gotchas, instruction patterns, and writing best practices.

**Sources synthesized:**
- **Anthropic PDF guide (Chapter 5)** — Five workflow patterns: sequential orchestration, multi-MCP coordination, iterative refinement, context-aware tool selection, domain-specific intelligence. Problem-first vs. tool-first framing ("Home Depot" analogy).
- **OpenClaw V2 skill-creator** — Pattern categorization (standalone, workflow, MCP-enhanced), concrete multi-MCP example (Figma → Drive → Linear → Slack)
- **agentskills.io (best-practices.md)** — Gotchas pattern as highest-value skill content, plan-validate-execute pattern with intermediate validation, checklists for multi-step workflows, template pattern, validation loops
- **Anthropic built-in skill-creator** — Output format templates (strict vs. flexible), examples pattern

### references/testing-methodology.md (196 lines — original)

Full testing methodology from manual testing through structured evals and pressure testing.

**Sources synthesized:**
- **Anthropic PDF guide (Chapter 3)** — Three testing tiers (manual, scripted, programmatic), triggering/functional/performance test categories, success criteria definition, "iterate on a single task first" pro tip
- **agentskills.io (evaluating-skills.md)** — Structured eval framework with evals.json, workspace directory structure, grading with evidence, benchmark aggregation with delta, human review workflow, blind comparison, pattern analysis (which assertions to keep/remove/tighten)
- **Superpowers writing-skills** — RED-GREEN-REFACTOR for discipline-enforcing skills, pressure scenario design (combining time/sunk-cost/authority/exhaustion), rationalization tables, bulletproofing techniques, meta-testing
- **Anthropic built-in skill-creator** — Baseline comparison methodology (with-skill vs. without-skill runs), iteration loop guidance

### references/troubleshooting.md (94 lines — original)

Symptom-based troubleshooting guide for common skill issues.

**Sources synthesized:**
- **Anthropic PDF guide (Chapter 5 troubleshooting section)** — Upload errors table, YAML formatting pitfalls, model laziness workarounds, "ask the AI when it would use your skill" debug technique
- **OpenClaw V2 skill-creator** — Five symptom-based sections (undertriggering, overtriggering, MCP failures, inconsistent execution, performance), diagnosis/solution structure with code examples
- **agentskills.io (best-practices.md)** — Nuance about agents not consulting skills for tasks they can handle alone, execution transcript analysis for diagnosing vague instructions

### references/writing-scripts.md (189 lines — original)

Guide for designing scripts that AI agents can use effectively in non-interactive shells.

**Sources synthesized:**
- **agentskills.io (using-scripts.md)** — Primary source. No interactive prompts (hard requirement), `--help` documentation, structured output to stdout with diagnostics to stderr, helpful error messages with available options, idempotent operations, `--dry-run` for destructive actions, meaningful exit codes, output size control, inline dependency declarations (PEP 723 + uv)
- **Anthropic PDF guide** — "Solve, don't punt" error handling pattern, documented constants vs. magic numbers, prefer scripts for deterministic operations
- **Anthropic built-in skill-creator** — "Look for repeated work across test cases" signal for when to bundle a script

---

### agents/grader.md (223 lines — from Anthropic built-in skill-creator)

Subagent instructions for evaluating assertions against execution transcripts and outputs with evidence-based pass/fail grading.

**Source:** Directly from Anthropic's built-in skill-creator (`agents/grader.md`). Unmodified. Agent-agnostic by design — instructs "the Grader" without platform-specific references.

### agents/comparator.md (202 lines — from Anthropic built-in skill-creator)

Subagent instructions for blind A/B comparison between two outputs without knowing which skill produced them.

**Source:** Directly from Anthropic's built-in skill-creator (`agents/comparator.md`). Unmodified.

### agents/analyzer.md (274 lines — from Anthropic built-in skill-creator)

Subagent instructions for post-hoc analysis of blind comparison results and benchmark pattern analysis.

**Source:** Directly from Anthropic's built-in skill-creator (`agents/analyzer.md`). Unmodified.

---

### assets/eval_review.html (146 lines — from Anthropic built-in skill-creator)

Interactive browser template for reviewing trigger eval queries with users. Users can edit queries, toggle should-trigger, add/remove entries, and export as JSON.

**Source:** Directly from Anthropic's built-in skill-creator (`assets/eval_review.html`). Unmodified.

---

### eval-viewer/generate_review.py (471 lines — from Anthropic built-in skill-creator)

Generates and serves an interactive review UI for eval outputs. Supports inline file rendering, feedback collection, previous-iteration comparison, and `--static` for standalone HTML output.

**Source:** Directly from Anthropic's built-in skill-creator (`eval-viewer/generate_review.py`). Unmodified.

### eval-viewer/viewer.html (1,325 lines — from Anthropic built-in skill-creator)

The interactive review UI template with tabs for outputs, benchmark stats, and feedback.

**Source:** Directly from Anthropic's built-in skill-creator (`eval-viewer/viewer.html`). Unmodified.

---

### scripts/init_skill.py (347 lines — adapted from OpenClaw V2)

Scaffolds a new skill directory with SKILL.md template, TODO placeholders, structural pattern suggestions (workflow/task/reference/capabilities-based), and optional resource directories.

**Source:** Adapted from OpenClaw V2's `init_skill.py`. Changes: all "Codex" references replaced with "the AI assistant" for agent-agnosticism. Example script template updated with agentic design tips (no interactive prompts, structured output, `--help`). Gotchas section added to SKILL.md template.

### scripts/package_skill.py (133 lines — adapted from OpenClaw V2)

Validates and packages a skill folder into a distributable `.skill` file (zip with `.skill` extension). Rejects symlinks for security.

**Source:** Adapted from OpenClaw V2's `package_skill.py`. Import path changed from `scripts.quick_validate` to flat `quick_validate` for portability.

### scripts/quick_validate.py (167 lines — adapted from OpenClaw V2)

Validates SKILL.md frontmatter format, naming conventions, description constraints, and file organization. Includes a fallback YAML parser for environments without PyYAML.

**Source:** Adapted from OpenClaw V2's `quick_validate.py`. `compatibility` added to allowed frontmatter properties (was missing in V2, contradicting its own documentation). Fallback parser preserved for portability — Anthropic's version requires PyYAML.

### scripts/aggregate_benchmark.py (401 lines — from Anthropic built-in skill-creator)

Reads `grading.json` files from a workspace directory structure and produces `benchmark.json` with mean/stddev/delta statistics plus human-readable `benchmark.md`.

**Source:** Directly from Anthropic's built-in skill-creator (`scripts/aggregate_benchmark.py`). Unmodified. Platform-agnostic — stdlib only.

### scripts/generate_report.py (326 lines — from Anthropic built-in skill-creator)

Generates HTML reports from description optimization loop output with per-query pass/fail visualization, train/test split coloring, and auto-refresh for live monitoring.

**Source:** From Anthropic's built-in skill-creator (`scripts/generate_report.py`). One change: "Claude tests different versions" → "the optimizer tests different versions" for agent-agnosticism.

---

## Sources Referenced

| Source | What | Where |
|--------|------|-------|
| **Anthropic built-in skill-creator** | The skill that ships with Claude Code / claude.ai for creating skills | `/mnt/skills/examples/skill-creator/` or [GitHub](https://github.com/anthropics/skills/tree/main/skills/skill-creator) |
| **Anthropic PDF guide** | "The Complete Guide to Building Skills for Claude" | [PDF](https://resources.anthropic.com/hubfs/The-Complete-Guide-to-Building-Skill-for-Claude.pdf) |
| **agentskills.io** | The open specification for Agent Skills | [agentskills.io](https://agentskills.io) |
| **OpenClaw V2 skill-creator** | Community skill-creator with platform-agnostic framing | OpenClaw project |
| **Superpowers writing-skills** | TDD-focused skill creation methodology with CSO insights | Superpowers project |

## License

The original reference files (`references/description-optimization.md`, `distribution.md`, `skill-patterns.md`, `testing-methodology.md`, `troubleshooting.md`, `writing-scripts.md`) and `SKILL.md` are original works.

Files sourced from Anthropic's built-in skill-creator (`agents/`, `assets/eval_review.html`, `eval-viewer/`, `references/schemas.md`, `scripts/aggregate_benchmark.py`, `scripts/generate_report.py`) are under Apache 2.0 per Anthropic's license.

Scripts adapted from OpenClaw V2 (`scripts/init_skill.py`, `scripts/package_skill.py`, `scripts/quick_validate.py`) retain their original license terms.
