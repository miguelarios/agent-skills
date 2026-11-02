# Frontmatter Fields

Contents: field table · design rule · examples · the tools-needed pattern · upload safety

## Field table

"Upload-safe" means claude.ai uploads, the Skills API, and Anthropic's `package_skill.py` accept it. Those hard-reject any other top-level key ("Unexpected key(s) in SKILL.md frontmatter"). Claude Code accepts extra fields; Hermes ignores unknown keys. Nested keys under `metadata` are never validated by the upload path.

| Field | Lives | Read by | Upload-safe | What it does |
|---|---|---|---|---|
| `name` | top | all | yes | Identifier. kebab-case, equals directory, max 64 chars. |
| `description` | top | all | yes | Triggering text. Max 1024 chars, no angle brackets. |
| `license` | top | spec; informational | yes | License name or file reference. |
| `compatibility` | top | spec; shown to agents | yes | Free text, max 500 chars, environment needs. |
| `metadata` | top | spec; free-form map | yes | Custom keys; nest platform extras here. |
| `allowed-tools` | top | spec (experimental); Claude Code honors it | yes | Pre-approved tools, e.g. `Bash(python:*) WebFetch`. Support varies. |
| `when_to_use` | top | Claude Code | **no** | Extra trigger text appended to description. Description + `when_to_use` truncate at 1536 chars in the listing. |
| `argument-hint`, `arguments` | top | Claude Code | no | Slash-command argument UX. |
| `disable-model-invocation` | top | Claude Code | no | Only the user can invoke the skill. |
| `user-invocable` | top | Claude Code | no | Hide from the slash menu when false. |
| `disallowed-tools` | top | Claude Code | no | Tools blocked while the skill is active. |
| `model`, `effort` | top | Claude Code | no | Override model or effort for the skill. |
| `context` (fork), `agent`, `background` | top | Claude Code | no | Run the skill in a forked subagent. |
| `hooks` | top | Claude Code | no | Lifecycle hooks scoped to the skill. |
| `required_environment_variables` | top | Hermes | no | List of `{name, prompt, help, required_for}`. Hermes prompts for missing keys in the CLI and passes them into sandboxes. Legacy alias: `prerequisites.env_vars`. Hermes reads env vars only at top level. |
| `platforms` | top | Hermes | no | Host OS filter: `linux`, `macos`, `windows`. |
| `required_credential_files` | top | Hermes | no | Credential files to mount into sandboxes. |
| `metadata.hermes.tags` | nested | Hermes | yes | Search and grouping. |
| `metadata.hermes.related_skills` | nested | Hermes | yes | Cross-links. |
| `metadata.hermes.requires_toolsets`, `requires_tools` | nested | Hermes | yes | Show the skill only when those tools exist. |
| `metadata.hermes.fallback_for_toolsets`, `fallback_for_tools` | nested | Hermes | yes | Hide the skill when the primary tool exists (the skill is the fallback). |
| `metadata.hermes.config` | nested | Hermes | yes | List of `{key, description, default, prompt}` stored in `config.yaml` under `skills.config`. |
| `metadata.hermes.blueprint` | nested | Hermes | yes | `schedule`, `deliver`, `prompt`, `no_agent` for cron-style runs. |
| `metadata.openclaw.requires.bins` (etc.) | nested | OpenClaw (legacy) | yes | Required binaries. Verified accepted by claude.ai as nested metadata. |
| `metadata.sync.sets`, `metadata.sync.public` | nested | Miguel's skillsync tooling | yes | Example of custom metadata: which sync sets (`personal`, `work`) carry the skill, and whether it is published. Preserve when editing. |

Common mistake: a dotted top-level key such as `metadata.openclaw: {...}`. YAML does not nest that; it is an unknown top-level key. Indent under `metadata:` instead. `quick_validate.py` flags it with a fix hint.

## Design rule

1. Default to the six spec fields.
2. Put platform extras under `metadata.<platform>`.
3. Use a top-level platform key only when it buys real behavior no other field can (e.g. Hermes `required_environment_variables`, Claude Code `disable-model-invocation`).
4. Keep one SKILL.md per skill. Differences between agents go in body sections ("If your runtime has subagents...", "If `claude -p` is unavailable...").
5. For claude.ai, package with `package_skill.py --target claude-ai`: it strips non-spec top-level keys from the packaged copy, prints what it removed, and never edits the source. The build is an artifact; do not store it or edit it.

Validator behavior: `quick_validate.py <skill>` warns on non-spec top-level keys and names who reads them. With `--target claude-ai` or `--target spec` they are errors.

## Examples

### Portable only (works everywhere, uploads as is)

```yaml
---
name: csv-to-chart
description: Turn CSV or XLSX data into charts. Use whenever the user has tabular data and wants a visualization, even if they do not say "chart".
license: MIT
compatibility: Needs Python 3.9+ with matplotlib. No network.
metadata:
  author: miguel
  version: "1.2"
---
```

### Hermes-enhanced (API key skill)

```yaml
---
name: weather-brief
description: Fetch a forecast and summarize it. Use when the user asks about weather, rain, or what to wear.
compatibility: Needs WEATHER_API_KEY and curl (or any HTTP tool). Works offline-degraded without the key.
platforms: [linux, macos]
required_environment_variables:
  - name: WEATHER_API_KEY
    prompt: Weather API key
    help: https://example.com/keys
    required_for: live forecasts
metadata:
  hermes:
    tags: [weather, api]
    requires_tools: [terminal]
---
```

Hermes prompts for the key and passes it to sandboxes. The top-level fields are stripped by `--target claude-ai`; the `compatibility` text and body Prerequisites survive.

### Claude Code-enhanced

```yaml
---
name: release-notes
description: Draft release notes from merged PRs. Use when preparing a release.
compatibility: Needs git and gh authenticated.
allowed-tools: Bash(git:*) Bash(gh:*)
when_to_use: Also when the user pastes a changelog and asks to polish it.
disable-model-invocation: true
argument-hint: "[version]"
---
```

Only `allowed-tools` is a spec field. The rest are Claude Code behavior and are stripped for claude.ai.

## The tools-needed pattern (three ways)

State requirements in all three places so the skill still works when one is ignored:

1. **`compatibility` text** (every runtime, upload-safe): "Needs WEATHER_API_KEY and curl."
2. **Runtime fields** when targeting that runtime: Hermes `required_environment_variables`, `metadata.hermes.requires_tools`, or Claude Code `allowed-tools`.
3. **A Prerequisites section in the body**, with a fallback:

```markdown
## Prerequisites
- `WEATHER_API_KEY` in the environment. If missing, ask the user to set it; offer to summarize from a pasted forecast instead.
- `curl`. If unavailable, use the runtime's web fetch tool.
```

Never put real secrets in any of these; name the variable only.
