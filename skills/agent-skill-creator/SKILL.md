---
name: agent-skill-creator
description: Create, update, test, or package agent skills. Use when designing, structuring, or packaging skills with scripts, references, and assets. Triggers include "create a skill", "turn this into a skill", "capture this workflow", "make this reusable", "package this as a skill", "improve this skill", "update my skill", or any request to build reusable agent capabilities. Covers planning, description optimization, testing, troubleshooting, distribution, and iteration. Agent-agnostic.
---

# Skill Creator

Guide for creating effective agent skills. Skills are platform-agnostic and work across different AI assistants and environments.

## About Skills

Skills are modular, self-contained packages that extend an AI assistant's capabilities with specialized knowledge, workflows, and tools. They transform a general-purpose assistant into a specialized agent equipped with procedural knowledge no model fully possesses.

**What skills provide:**
1. **Specialized workflows** — multi-step procedures for specific domains
2. **Tool integrations** — instructions for working with specific file formats, APIs, or MCP servers
3. **Domain expertise** — company-specific knowledge, schemas, business logic
4. **Bundled resources** — scripts, references, and assets for complex and repetitive tasks

**Skills work identically across** AI platforms, desktop and web interfaces, and API-based integrations. Create once, use everywhere.

## Core Principles

### Concise is Key

The context window is a public good. Skills share it with the system prompt, conversation history, other skills' metadata, and the user's request.

**Default assumption: the AI assistant is already very smart.** Only add context it doesn't already have. Challenge each piece: "Does the AI really need this?" and "Does this paragraph justify its token cost?"

Prefer concise examples over verbose explanations.

### Set Appropriate Degrees of Freedom

Match specificity to the task's fragility:

- **High freedom** (text-based instructions): Multiple approaches valid, decisions depend on context.
- **Medium freedom** (pseudocode or parameterized scripts): Preferred pattern exists, some variation acceptable.
- **Low freedom** (specific scripts, few parameters): Operations fragile, consistency critical, exact sequence required.

Think of the AI assistant exploring a path: a narrow bridge with cliffs needs guardrails (low freedom), while an open field allows many routes (high freedom).

### Favor Procedures Over Declarations

Teach the AI assistant *how to approach* a class of problems, not *what to produce* for a specific instance. A skill that says "Read the schema from references/schema.yaml, join tables using the `_id` foreign key convention, apply filters as WHERE clauses" generalizes across queries. A skill that says "Join orders to customers on customer_id and sum amount" only works for that one task.

Skills can still include specific details — output templates, constraints, tool-specific instructions — but the *approach* should generalize even when individual details are specific.

### Design Coherent Units

Scope a skill like you'd scope a function: it should encapsulate a coherent unit of work that composes well with other skills. Too narrow forces multiple skills to load for a single task (overhead + conflicting instructions). Too broad makes triggering imprecise. A skill for querying a database and formatting results may be one coherent unit; a skill that also covers database administration is probably trying to do too much.

## Anatomy of a Skill

```
skill-name/
├── SKILL.md (required)
│   ├── YAML frontmatter (name + description, required)
│   └── Markdown instructions
└── Bundled Resources (optional)
    ├── scripts/      — Executable code (Python/Bash/etc.)
    ├── references/   — Documentation loaded into context as needed
    └── assets/       — Files used in output (templates, icons, fonts)
```

### Three-Level Progressive Disclosure

1. **Metadata** (name + description) — Always in context (~100 words). The AI assistant reads this to decide whether to load the skill.
2. **SKILL.md body** — Loaded when skill triggers. Target under 500 lines / 5k words.
3. **Bundled resources** — Loaded as needed. Scripts execute without consuming context; references load only when relevant.

### SKILL.md

- **Frontmatter** (YAML): `name` and `description` fields. This is the *only* thing the AI assistant reads to decide whether to use the skill, so the description must be clear and comprehensive.
- **Body** (Markdown): Instructions and guidance. Only loaded *after* the skill triggers.

### Bundled Resources

**Scripts** (`scripts/`): Executable code for tasks needing deterministic reliability or frequently rewritten logic. Token-efficient — can execute without loading into context. See `references/writing-scripts.md` for how to design scripts that agents can use effectively.

**References** (`references/`): Documentation loaded as-needed to inform the AI assistant's process. Use for schemas, API docs, domain knowledge, policies, detailed guides. Keep SKILL.md lean by moving detailed content here. For files >10k words, include grep patterns in SKILL.md. Avoid duplicating content between SKILL.md and references.

**Assets** (`assets/`): Files used in output, not loaded into context. Templates, images, boilerplate code, fonts. Example: `assets/slides_template.pptx`.

### What NOT to Include

Only include files that directly support the skill's function. Do not create README.md, CHANGELOG.md, INSTALLATION_GUIDE.md, or other auxiliary documentation. The skill should contain only what an AI agent needs to do the job.

## YAML Frontmatter

The frontmatter is how the AI assistant decides whether to load your skill. Get this right.

### Required Fields

```yaml
---
name: your-skill-name
description: What it does. Use when [specific trigger phrases].
---
```

**name** (required):
- kebab-case only (lowercase letters, digits, hyphens)
- Must match folder name
- Max 64 characters, no consecutive hyphens, no leading/trailing hyphens
- No XML angle brackets (`<>`)

**description** (required):
- Must include both *what the skill does* and *when to use it*
- Max 1024 characters, no XML angle brackets
- Include specific trigger phrases users would say
- Mention file types if relevant
- Write in third person (injected into system prompt)

**Good descriptions:**
```yaml
description: Analyzes Figma design files and generates developer handoff documentation. Use when user uploads .fig files, asks for "design specs", "component documentation", or "design-to-code handoff".

description: End-to-end customer onboarding workflow for PayFlow. Handles account creation, payment setup, and subscription management. Use when user says "onboard new customer", "set up subscription", or "create PayFlow account".
```

**Bad descriptions:**
```yaml
description: Helps with projects.
description: Creates sophisticated multi-page documentation systems.
```

**For in-depth description optimization guidance**, including the critical insight about why descriptions should never summarize workflow, and a structured eval loop with train/validation splits, see `references/description-optimization.md`. For reviewing trigger eval queries with users, use the interactive template at `assets/eval_review.html`.

### Optional Fields

- **license**: For open-source skills (e.g., `MIT`, `Apache-2.0`)
- **allowed-tools**: Restrict tool access (e.g., `"Bash(python:*) WebFetch"`) — experimental, support varies by client
- **compatibility**: Environment requirements, 1-500 characters (e.g., `"Requires Python 3.12+ and uv"`)
- **metadata**: Custom key-value pairs (`author`, `version`, `mcp-server`)

### Security Restrictions

- **No XML angle brackets** (`<>`) in frontmatter — it appears in the system prompt and could inject instructions
- **Avoid reserved platform names** in skill names

## Progressive Disclosure Patterns

Keep SKILL.md under 500 lines. Split into reference files when approaching this limit, and clearly describe *when* to read each file — "Read references/api-errors.md if the API returns a non-200 status" is better than "see references/ for details."

**Pattern 1 — High-level guide with references:**
```markdown
## Advanced features
- **Form filling**: See references/forms.md for complete guide
- **API reference**: See references/api.md for all methods
```

**Pattern 2 — Domain-specific organization:**
```
bigquery-skill/
├── SKILL.md (overview + navigation)
└── references/
    ├── finance.md    ← loaded only for finance queries
    ├── sales.md      ← loaded only for sales queries
    └── product.md    ← loaded only for product queries
```

**Pattern 3 — Conditional details:**
```markdown
## Editing documents
For simple edits, modify XML directly.
**For tracked changes**: See references/redlining.md
**For OOXML details**: See references/ooxml.md
```

**Guidelines:**
- Keep references one level deep from SKILL.md (no nested references)
- For files >100 lines, include a table of contents at top

## Skill Patterns

Skills generally fall into categories. Consult `references/skill-patterns.md` for detailed examples of each:

- **Standalone skills** — Document/asset creation with no external tools
- **Workflow automation** — Multi-step processes with validation gates
- **MCP-enhanced workflows** — Coordinating external services via MCP
- **Problem-first workflows** — Sequential orchestration with dependencies
- **Tool-first workflows** — Multi-MCP coordination across services
- **Iterative refinement** — Quality gates with validation loops

## Skill Creation Process

1. **Understand** the skill with concrete examples
2. **Plan** reusable skill contents (scripts, references, assets)
3. **Initialize** the skill (run `init_skill.py`)
4. **Edit** the skill (implement resources and write SKILL.md)
5. **Test** the skill against real usage
6. **Package and distribute** (run `package_skill.py`)
7. **Iterate** based on feedback

### Step 1: Understand the Skill

Skip only when usage patterns are already clearly understood.

Gather concrete examples of how the skill will be used. Ask:

- "What functionality should this skill support?"
- "Can you give examples of how it would be used?"
- "What would a user say that should trigger this skill?"

Avoid overwhelming users with too many questions at once. Conclude when there's a clear picture of the functionality the skill should support.

### Step 2: Plan Reusable Contents

For each concrete example, analyze:
1. How would you execute this from scratch?
2. What scripts, references, or assets would help when doing this repeatedly?

Examples of this analysis:
- PDF rotation → same code rewritten each time → `scripts/rotate_pdf.py`
- Frontend webapp → same boilerplate each time → `assets/hello-world/` template
- BigQuery queries → schema re-discovered each time → `references/schema.md`

### Step 3: Initialize the Skill

Run `scripts/init_skill.py` to scaffold:

```bash
scripts/init_skill.py <skill-name> --path <output-dir>
scripts/init_skill.py <skill-name> --path <output-dir> --resources scripts,references
scripts/init_skill.py <skill-name> --path <output-dir> --resources scripts --examples
```

Creates a skill directory with SKILL.md template, TODO placeholders, and optional resource directories.

### Step 4: Edit the Skill

The skill is being created for another AI assistant instance to use. Include information that would be beneficial and non-obvious. Consider what procedural knowledge, domain-specific details, or reusable assets would help another instance execute effectively.

**Writing guidelines:**
- Use imperative/infinitive form
- Explain the *why* behind instructions — AI assistants respond better to reasoning than rigid commands
- Prefer concrete examples over verbose explanations
- If you find yourself writing ALWAYS/NEVER in caps, reframe as reasoning instead
- Teach *approaches*, not *answers* — the skill should generalize beyond the examples used to build it

**For pattern guidance**, consult `references/skill-patterns.md`.

**For script design guidance**, consult `references/writing-scripts.md`.

**Update frontmatter:**
- Write the description with both *what* and *when* — all "when to use" info goes in the description, not the body
- For optimization techniques, see `references/description-optimization.md`

**Test scripts** by actually running them to verify no bugs and expected output.

### Step 5: Test the Skill

Testing rigor should match the skill's visibility and impact. See `references/testing-methodology.md` for the full methodology covering:

- **Triggering tests** — Does it load for the right queries and not for wrong ones?
- **Functional tests** — Does it produce correct outputs?
- **Baseline comparison** — Is it better than no skill at all?
- **Structured evals** — JSON-based test cases, assertions, grading, and benchmarking
- **Pressure testing** — For discipline-enforcing skills, does it hold up under pressure?

**Eval tooling** (all platform-agnostic, stdlib-only Python):
- `scripts/aggregate_benchmark.py` — Aggregates grading results into benchmark statistics with mean/stddev/delta
- `scripts/generate_report.py` — Generates HTML reports from description optimization loops
- `eval-viewer/generate_review.py` — Serves an interactive review UI for eval outputs; supports `--static` for standalone HTML

**Agent role files** — For environments that support spawning subagents, read the appropriate file before assigning the role:
- `agents/grader.md` — Evaluates assertions against outputs with evidence-based pass/fail
- `agents/comparator.md` — Blind A/B comparison between two outputs without knowing which skill produced them
- `agents/analyzer.md` — Post-hoc analysis of why a winner won, with improvement suggestions

**JSON schemas** — See `references/schemas.md` for the complete format definitions of `evals.json`, `grading.json`, `timing.json`, `benchmark.json`, `comparison.json`, `analysis.json`, and `history.json`.

**Quick approach:** Iterate on a single challenging task until the AI assistant succeeds, then extract the winning approach into the skill. Expand to multiple test cases for coverage.

### Step 6: Package and Distribute

Validate and package:

```bash
scripts/quick_validate.py <path/to/skill-folder>
scripts/package_skill.py <path/to/skill-folder> [output-dir]
```

Creates a `.skill` file (zip with `.skill` extension) ready for upload or sharing.

For distribution guidance (GitHub hosting, MCP integration docs), see `references/distribution.md`.

### Step 7: Iterate

Skills are living documents. Track improvements through real usage:

- **Pattern recognition**: "After 3 similar requests, skill struggled with X" → update SKILL.md
- **Triggering issues**: "User had to manually enable skill for Y" → improve description
- **Execution problems**: "MCP tool Z failed with error E" → add error handling
- **Gotcha discovered**: Agent keeps making the same wrong assumption → add to gotchas section

For common issues and fixes, see `references/troubleshooting.md`.

## Quick Checklist

### Before Packaging

- [ ] 2-3 concrete use cases identified
- [ ] Required tools identified (built-in or MCP)
- [ ] Folder named in kebab-case
- [ ] SKILL.md exists (exact case)
- [ ] YAML frontmatter has `---` delimiters
- [ ] `name`: kebab-case, no spaces, no capitals, matches folder name
- [ ] `description`: includes WHAT and WHEN, under 1024 chars, third person
- [ ] No XML angle brackets anywhere in frontmatter
- [ ] Instructions are clear and actionable
- [ ] Error handling included for critical operations
- [ ] Examples provided for non-obvious workflows
- [ ] References clearly linked from SKILL.md with when-to-read guidance
- [ ] Scripts tested by running them
- [ ] Scripts designed for non-interactive agentic use (see `references/writing-scripts.md`)

### After Upload

- [ ] Triggers correctly on obvious tasks
- [ ] Triggers on paraphrased requests
- [ ] Does NOT trigger on unrelated topics
- [ ] Functional tests pass
- [ ] Tool integrations work (if applicable)
- [ ] User feedback collected and incorporated
