# Skill Patterns

Effective patterns for different skill types. Most skills combine multiple patterns.

## Choosing Your Approach

- **Problem-first**: "I need to set up a project workspace" → Skill orchestrates the right tool calls in the right sequence. Users describe outcomes; the skill handles tools.
- **Tool-first**: "I have Notion MCP connected" → Skill teaches the AI assistant optimal workflows and best practices. Users have access; the skill provides expertise.

## Pattern A: Standalone Skills (No External Tools)

**Used for:** Creating consistent, high-quality output — documents, presentations, apps, designs, code.

**Key techniques:**
- Embedded style guides and brand standards
- Template structures for consistent output
- Quality checklists before finalizing
- Uses only built-in capabilities (code execution, file creation)

## Pattern B: Sequential Workflow Orchestration

**Used for:** Multi-step processes that must happen in a specific order.

```markdown
## Workflow: Onboard New Customer

### Step 1: Create Account
Call MCP tool: `ServiceName:create_customer`
Parameters: name, email, company

### Step 2: Setup Payment
Call MCP tool: `ServiceName:setup_payment_method`
Wait for: payment method verification

### Step 3: Create Subscription
Call MCP tool: `ServiceName:create_subscription`
Parameters: plan_id, customer_id (from Step 1)

### Step 4: Send Welcome Email
Call MCP tool: `ServiceName:send_email`
Template: welcome_email_template
```

**Key techniques:**
- Explicit step ordering with dependencies
- Validation at each stage
- Rollback instructions for failures
- Always use fully qualified MCP tool names (`ServerName:tool_name`)

## Pattern C: Multi-Service Coordination

**Used for:** Workflows spanning multiple MCP servers or services.

```markdown
## Workflow: Design Handoff

### Phase 1: Design Export (Figma MCP)
1. Export design assets from Figma
2. Generate design specifications
3. Create asset manifest

### Phase 2: Asset Storage (Drive MCP)
1. Create project folder in Drive
2. Upload all assets
3. Generate shareable links

### Phase 3: Task Creation (Linear MCP)
1. Create development tasks
2. Attach asset links to tasks
3. Assign to engineering team

### Phase 4: Notification (Slack MCP)
1. Post handoff summary to #engineering
2. Include asset links and task references
```

**Key techniques:**
- Clear phase separation
- Data passing between services
- Validation before moving to next phase
- Centralized error handling

## Pattern D: Iterative Refinement with Quality Gates

**Used for:** Tasks where output quality improves with iteration.

```markdown
### Initial Draft
1. Fetch data via MCP
2. Generate first draft
3. Save to temporary file

### Quality Check
1. Run validation script: `scripts/check_report.py`
2. Identify issues (missing sections, formatting, data errors)

### Refinement Loop
1. Address each identified issue
2. Regenerate affected sections
3. Re-validate
4. Repeat until quality threshold met

### Finalization
1. Apply final formatting
2. Save final version
```

**Key techniques:**
- Explicit quality criteria
- Validation scripts for deterministic checking
- Clear stopping conditions
- Feedback loops: run validator → fix → repeat

## Pattern E: Context-Aware Tool Selection

**Used for:** Same outcome, different tools depending on context.

```markdown
## Smart File Storage

### Decision Tree
1. Check file type and size
2. Determine best storage:
   - Large files (>10MB): Cloud storage MCP
   - Collaborative docs: Docs MCP
   - Code files: GitHub MCP
   - Temporary files: Local storage

### Execute
- Call appropriate MCP tool
- Apply service-specific metadata
- Generate access link

### Explain
- Tell user why that storage was chosen
```

## Pattern F: Domain-Specific Intelligence

**Used for:** Skills that add specialized knowledge beyond tool access.

**Key techniques:**
- Domain expertise embedded in logic
- Compliance-before-action pattern
- Comprehensive audit trails

## Pattern G: Gotchas Sections

Often the highest-value content in a skill is a list of **gotchas** — environment-specific facts that defy reasonable assumptions. These aren't general advice ("handle errors appropriately") but concrete corrections to mistakes the AI assistant *will* make without being told otherwise.

```markdown
## Gotchas

- The `users` table uses soft deletes. Queries must include
  `WHERE deleted_at IS NULL` or results will include deactivated accounts.
- The user ID is `user_id` in the database, `uid` in the auth service,
  and `accountId` in the billing API. All three refer to the same value.
- The `/health` endpoint returns 200 as long as the web server is running,
  even if the database connection is down. Use `/ready` for full service health.
```

**Key principles:**
- Keep gotchas in SKILL.md where the agent reads them *before* encountering the situation
- When an agent makes a mistake you have to correct, add the correction to gotchas — this is one of the most direct ways to improve a skill iteratively
- Gotchas are NOT general best practices — they're specific facts that contradict what the AI would otherwise assume

## Instruction Patterns

### Checklists for Multi-Step Workflows

An explicit checklist helps the agent track progress and avoid skipping steps:

```markdown
## Form processing workflow

Progress:
- [ ] Step 1: Analyze the form (run `scripts/analyze_form.py`)
- [ ] Step 2: Create field mapping (edit `fields.json`)
- [ ] Step 3: Validate mapping (run `scripts/validate_fields.py`)
- [ ] Step 4: Fill the form (run `scripts/fill_form.py`)
- [ ] Step 5: Verify output (run `scripts/verify_output.py`)
```

### Plan-Validate-Execute

For batch or destructive operations, have the agent create an intermediate plan, validate it, then execute:

1. Extract form fields → `form_fields.json`
2. Create `field_values.json` mapping fields to values
3. Validate: `scripts/validate_fields.py form_fields.json field_values.json`
4. If validation fails, revise and re-validate
5. Execute: `scripts/fill_form.py input.pdf field_values.json output.pdf`

The key ingredient is the validation step that checks the plan against the source of truth. Verbose error messages ("Field 'signature_date' not found — available fields: ...") let the agent self-correct.

### Templates for Output Format

When you need specific output format, provide a template — agents pattern-match well against concrete structures:

````markdown
## Report structure

Use this template, adapting sections as needed:

```markdown
# [Analysis Title]

## Executive summary
[One-paragraph overview]

## Key findings
- Finding 1 with supporting data
- Finding 2 with supporting data

## Recommendations
1. Specific actionable recommendation
2. Specific actionable recommendation
```
````

Short templates go inline; longer ones go in `assets/` with a reference from SKILL.md.

## Writing Best Practices

**Be specific and actionable:**
```
# Good
Run `python scripts/validate.py --input {filename}` to check data format.
If validation fails, common issues include:
- Missing required fields (add them to CSV)
- Invalid date formats (use YYYY-MM-DD)

# Bad
Validate data before proceeding.
```

**Provide defaults, not menus:** Pick one default approach, mention alternatives briefly as escape hatches.

**Prefer scripts for critical operations:** Code is deterministic; language interpretation isn't. See `references/writing-scripts.md` for design guidance.
