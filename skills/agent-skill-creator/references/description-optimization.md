# Description Optimization

The `description` field is the single most important factor in whether your skill gets used. The AI assistant reads it to decide which skill to load from potentially hundreds available.

## The Critical Rule: Description = When to Use, NOT What It Does

**Never summarize your skill's workflow in the description.** Testing has shown that when a description summarizes the skill's process, the AI assistant may follow the description as a shortcut instead of reading the full SKILL.md body. The skill body becomes documentation the AI assistant skips.

```yaml
# BAD: Summarizes workflow — AI assistant may follow this instead of reading skill
description: Use when executing plans - dispatches subagent per task with code review between tasks

# BAD: Too much process detail
description: Use for TDD - write test first, watch it fail, write minimal code, refactor

# GOOD: Triggering conditions only, no workflow summary
description: Use when executing implementation plans with independent tasks in the current session

# GOOD: Triggering conditions only
description: Use when implementing any feature or bugfix, before writing implementation code
```

**The trap:** Descriptions that summarize workflow create a shortcut the AI assistant will take.

## Writing Effective Descriptions

### Structure

`[What it does] + [When to use it] + [Key trigger phrases]`

### Format Rules

- Use imperative phrasing: "Use this skill when..." not "This skill does..."
- Focus on user intent, not implementation details
- Write in third person (injected into system prompt)
- Under 1024 characters (aim for under 500 when possible)
- No XML angle brackets (`<>`)
- Include specific tasks users might say
- Mention file types if relevant
- Err on the side of being "pushy" — explicitly list contexts where the skill applies
- Include synonyms and variations of key terms

### Good Examples

```yaml
# Specific, actionable, includes trigger phrases
description: Analyzes Figma design files and generates developer handoff documentation. Use when user uploads .fig files, asks for "design specs", "component documentation", or "design-to-code handoff".

# Clear value prop with trigger phrases
description: End-to-end customer onboarding workflow for PayFlow. Handles account creation, payment setup, and subscription management. Use when user says "onboard new customer", "set up subscription", or "create PayFlow account".

# Includes negative triggers to prevent over-triggering
description: Advanced data analysis for CSV files. Use for statistical modeling, regression, clustering. Do NOT use for simple data exploration (use data-viz skill instead).

# Broad applicability with explicit edge cases
description: >
  Analyze CSV and tabular data files — compute summary statistics,
  add derived columns, generate charts, and clean messy data. Use when
  the user has a CSV, TSV, or Excel file and wants to explore, transform,
  or visualize the data, even if they don't explicitly mention "CSV" or "analysis."
```

### Bad Examples

```yaml
# Too vague — won't trigger for anything useful
description: Helps with projects.

# Missing triggers — AI assistant won't know when to load it
description: Creates sophisticated multi-page documentation systems.

# Too technical, no user-facing triggers
description: Implements a Project entity model with hierarchical relationships.

# First person — wrong voice for system prompt injection
description: I can help you with async tests when they're flaky.
```

## Keyword Coverage

Use words the AI assistant would search for when matching a query to a skill:

- **Error messages**: "Hook timed out", "ENOTEMPTY", "race condition"
- **Symptoms**: "flaky", "hanging", "zombie", "pollution"
- **Synonyms**: "timeout/hang/freeze", "cleanup/teardown/afterEach"
- **Tools**: Actual commands, library names, file types
- **Natural phrases**: What a user would literally type

## Naming Conventions

Prefer active voice, verb-first names:
- `creating-skills` not `skill-creation`
- `condition-based-waiting` not `async-test-helpers`

Gerunds (-ing) work well for processes: `creating-skills`, `testing-skills`, `debugging-with-logs`.

Avoid vague names: "Helper", "Utils", "Tools", "Documents", "Data".

## Systematic Description Optimization

For skills where triggering accuracy matters, use this structured eval loop rather than ad-hoc testing.

### Step 1: Design Trigger Eval Queries

Create ~20 realistic user prompts labeled with whether they should trigger:

```json
[
  {"query": "I've got a spreadsheet in ~/data/q4_results.xlsx with revenue in col C — can you add a profit margin column?", "should_trigger": true},
  {"query": "whats the quickest way to convert this json file to yaml", "should_trigger": false}
]
```

**Should-trigger queries (8-10):** Vary phrasing (formal/casual), explicitness (names the domain vs. describes the need), detail level (terse vs. context-heavy), and complexity (single-step vs. multi-step). The most useful are cases where the skill would help but the connection isn't obvious.

**Should-not-trigger queries (8-10):** Focus on **near-misses** — queries sharing keywords but needing something different. "Write a fibonacci function" is too easy; "write a python script that reads a CSV and uploads rows to postgres" (shares CSV keyword but is actually ETL, not analysis) is a real test.

**Make them realistic:** Include file paths, column names, personal context, casual language, abbreviations, typos.

**Review with user:** Use `assets/eval_review.html` to present the query set for review. Replace the placeholder data and skill name, save to a temp file, and open in a browser. The user can edit queries, toggle should-trigger, add/remove entries, and export the final set as JSON.

### Step 2: Split Train/Validation

Split your queries 60/40 to avoid overfitting:

- **Train set (~60%)**: Used to identify failures and guide improvements
- **Validation set (~40%)**: Held out — only used to check whether improvements generalize

Ensure both sets have proportional mixes of should-trigger and should-not-trigger. Keep the split fixed across iterations.

### Step 3: Test and Iterate

1. **Evaluate** current description on both sets. Use train results to guide changes; validation results to check generalization.
2. **Identify failures** in the train set only.
3. **Revise the description:**
   - Failing should-trigger → description too narrow, broaden scope
   - Failing should-not-trigger → description too broad, add specificity
   - Avoid adding specific keywords from failed queries (that's overfitting) — address the general category instead
   - If stuck after several iterations, try a structurally different framing
4. **Repeat** until train set passes or improvement plateaus.
5. **Select best iteration** by validation pass rate (not train rate).

Five iterations is usually enough. Run each query 3x to account for nondeterminism and compute trigger rates. Use `scripts/generate_report.py` to visualize results as an HTML report showing per-query pass/fail across iterations with train/test split coloring.

### Step 4: Verify with Fresh Queries

After selecting the best description, test with 5-10 entirely new queries as a final sanity check.

## Debugging Triggering Issues

**Undertriggering** (skill doesn't load when it should):
- Add more trigger phrases and synonyms
- Include file types and tool names explicitly
- Make description slightly "pushier"
- Include edge cases: "even if they don't explicitly mention X"

**Overtriggering** (skill loads for unrelated queries):
- Add negative triggers: "Do NOT use for..."
- Be more specific about scope
- Clarify boundaries with other skills

**Debug approach:** Ask the AI assistant: "When would you use the [skill name] skill?" It will quote the description back. Adjust based on what's missing or too broad.

## Anti-Pattern: "When to Use" in the Body

All "when to use" information belongs in the description, not in the SKILL.md body. The body is only loaded *after* the skill triggers, so a "When to Use This Skill" section in the body is never seen during the triggering decision.
