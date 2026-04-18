# Troubleshooting

Common issues and solutions, organized by symptom.

## Skill Never Loads Automatically

**Likely cause:** Description too generic or missing trigger phrases.

**Solutions:**
- Revise description to include specific trigger phrases users would say
- Add file types, tool names, and action verbs
- See `references/description-optimization.md` for good/bad examples
- Make description slightly "pushier" to combat undertriggering
- Include edge cases: "even if they don't explicitly mention X"

**Debug approach:** Ask the AI assistant: "When would you use the [skill name] skill?" It will quote the description back. Adjust based on what's missing.

**Important nuance:** AI assistants typically only consult skills for tasks requiring knowledge beyond what they can handle alone. A simple "read this PDF" may not trigger a PDF skill because the agent can handle it with basic tools. Skills trigger most reliably for specialized knowledge, unfamiliar APIs, domain-specific workflows, or uncommon formats.

## Skill Loads for Unrelated Queries

**Likely cause:** Description too broad, lacking scope boundaries.

**Solutions:**
- Add negative triggers:
  ```yaml
  description: Advanced data analysis for CSV files. Use for statistical
  modeling, regression, clustering. Do NOT use for simple data exploration
  (use data-viz skill instead).
  ```
- Narrow scope:
  ```yaml
  # Too broad
  description: Processes documents
  # Specific
  description: Processes PDF legal documents for contract review
  ```
- Clarify boundaries with other skills

## Skill Loads but MCP Calls Fail

**Likely cause:** Connection, authentication, or tool naming issues.

**Checklist:**
1. Verify MCP server is connected (check settings/extensions)
2. Confirm authentication (API keys valid, permissions correct, tokens refreshed)
3. Test MCP independently (without skill): "Use [Service] MCP to fetch my projects"
   - If this fails, the issue is MCP, not the skill
4. Verify tool names match MCP server documentation (case-sensitive)
5. Use fully qualified tool names: `ServerName:tool_name`

## Skill Executes but Results Are Inconsistent

**Likely causes:** Vague instructions, missing error handling, or model laziness.

**Solutions:**
1. **Add validation gates** with specific checks before critical operations
2. **Bundle scripts for critical validations** — code is deterministic; language isn't
3. **Use verifiable intermediate outputs** — have the AI create a plan file and validate before executing
4. **Read execution transcripts**, not just final outputs — if the agent wastes time on unproductive steps, instructions may be too vague, inapplicable, or offer too many options without a clear default
5. **Add encouragement** (more effective in user prompts than in skills):
   ```markdown
   - Take your time to do this thoroughly
   - Quality is more important than speed
   - Do not skip validation steps
   ```

## Skill Performance is Slow or Degraded

**Likely cause:** Too much content loaded, or too many skills active.

**Solutions:**
1. Move detailed docs to `references/`, keep SKILL.md under 500 lines / 5,000 words
2. Reduce active skills — evaluate if >20-50 are enabled simultaneously
3. Check for content that loads unnecessarily — could large references use grep patterns?

## Skill Won't Upload

| Error | Fix |
|-------|-----|
| "Could not find SKILL.md" | Rename to exactly `SKILL.md` (case-sensitive) |
| "Invalid frontmatter" | Check `---` delimiters, close quotes, valid YAML |
| "Invalid skill name" | Use kebab-case: `my-cool-skill` not `My Cool Skill` |
| "Description contains angle brackets" | Remove all `<>` from description |
| "Name too long" | Max 64 characters |
| "Consecutive hyphens" | `my-skill` not `my--skill` |

## Skill Not Appearing in OpenClaw

**Likely cause:** Gating requirements not met, or skill not in a recognized location.

**Checklist:**
1. Verify skill is in a recognized location: `<workspace>/skills/`, `~/.openclaw/skills/`, or a dir in `skills.load.extraDirs`
2. Check `metadata.openclaw.requires` — are all bins on PATH? Are env vars set?
3. Check `metadata.openclaw.os` — does it include the current platform?
4. Check `~/.openclaw/openclaw.json` — is the skill disabled via `skills.entries.<name>.enabled: false`?
5. Check `skills.allowBundled` — if set, only listed bundled skills are eligible
6. Try `openclaw agent --message "list skills"` or ask the agent to "refresh skills"
7. Remember: skills snapshot at session start. Changes require a new session or hot reload via the skills watcher.

## Metadata JSON Parse Error

**Likely cause:** Multi-line metadata or invalid JSON.

**Solutions:**
- OpenClaw's parser requires `metadata` to be a **single-line JSON object**
- Collapse any multi-line metadata into one line
- Validate JSON: `echo '{"openclaw": {...}}' | python -m json.tool`
- Common JSON errors: trailing commas, unquoted keys, single quotes instead of double quotes

## Slash Command Not Working

**Likely cause:** Missing `command-tool` or skill not set as `user-invocable`.

**Checklist:**
1. Verify `command-dispatch: tool` is set
2. Verify `command-tool` names a valid tool
3. Verify `user-invocable: true` (default, but check if explicitly set to false)
4. If `disable-model-invocation: true`, the skill won't appear in model suggestions — only via `/command`

## Gating Not Filtering Correctly

**Likely cause:** Binary not on PATH, or env var provided differently than expected.

**Solutions:**
- `requires.bins` checks the **host** PATH at load time, not the sandbox
- `requires.env` is satisfied if the var exists in the process **or** is provided via `skills.entries.<key>.env` or `apiKey` in config
- `primaryEnv` must match an entry in `requires.env` for the `apiKey` config shortcut to work
- Use `which <binary>` to verify bin availability
- For sandboxed agents, the binary must also be in the container — install via `agents.defaults.sandbox.docker.setupCommand`

## Instructions Not Followed

- **Instructions too verbose** — Keep concise, use numbered steps
- **Critical info buried** — Put important instructions early, use `CRITICAL:` prefix
- **Ambiguous language** — Replace "validate things properly" with specific checks
- **Too many options** — Provide one default approach, not five alternatives
- **Missing "why"** — Explain reasoning; agents follow instructions better when they understand the purpose
