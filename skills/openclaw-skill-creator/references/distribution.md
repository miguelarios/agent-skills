# Distribution and Sharing

## Local Installation

The simplest way to use a skill is to place it directly in one of OpenClaw's skill directories:

- **Workspace skills** (per-agent): `<workspace>/skills/<skill-name>/`
- **Managed/local skills** (shared): `~/.openclaw/skills/<skill-name>/`

OpenClaw discovers skills automatically. Ask the agent to "refresh skills" or restart the gateway to pick up new additions. If the skills watcher is enabled, changes to `SKILL.md` trigger a hot reload on the next agent turn.

## ClawHub (Public Registry)

[ClawHub](https://clawhub.com) is the public skills registry for OpenClaw. Use it to discover, install, update, and share skills.

### Installing Skills

```bash
# Install a skill into the current workspace
clawhub install <skill-slug>

# Update all installed skills
clawhub update --all

# Scan and publish updates
clawhub sync --all
```

By default, `clawhub install` places skills in `./skills` under the current working directory (or falls back to the configured OpenClaw workspace). OpenClaw picks them up as `<workspace>/skills` on the next session.

### Publishing to ClawHub

To publish a skill, ensure it passes validation first:

```bash
scripts/quick_validate.py <path/to/skill-folder>
```

Then use `clawhub sync` to publish. Browse published skills at [https://clawhub.com](https://clawhub.com).

## Validation

Before distributing, validate your skill against the specification:

```bash
scripts/quick_validate.py <path/to/skill-folder>
```

Checks frontmatter format, naming conventions, description constraints, metadata JSON validity, and file organization.

## Packaging as .skill File

For sharing outside ClawHub (GitHub releases, direct transfer), use `scripts/package_skill.py`:

```bash
scripts/package_skill.py <path/to/skill-folder>
scripts/package_skill.py <path/to/skill-folder> ./dist
```

Creates a `.skill` file (zip archive with `.skill` extension). The recipient extracts it into their `~/.openclaw/skills/` or workspace `skills/` directory.

## Hosting on GitHub

For public skills, structure the repository clearly:

```
your-skill/
├── README.md                    # Repo-level README (for human visitors)
├── your-skill.skill             # Downloadable package (optional)
└── your-skill/                  # Skill folder
    ├── SKILL.md
    ├── scripts/
    ├── references/
    └── assets/
```

**README content** (for humans, not included in .skill package):
- What problems the skill solves
- Clear installation instructions (both `clawhub install` and manual)
- Example usage with screenshots
- Requirements and dependencies
- OpenClaw config needed (env vars, API keys)

**Version management:**
- Tag releases
- Maintain CHANGELOG at repo level (not in skill folder)
- The skill folder itself should never contain README.md or CHANGELOG.md

## Plugin-Shipped Skills

Plugins can ship their own skills by listing `skills` directories in `openclaw.plugin.json` (paths relative to the plugin root). Plugin skills load when the plugin is enabled and participate in the normal skill precedence rules. Gate them via `metadata.openclaw.requires.config` on the plugin's config entry.

See [Plugins](/plugin) in the OpenClaw docs for discovery/config details.

## MCP Integration Documentation

For skills that enhance an MCP server, document how to use both together:

```markdown
## Installing [Your Service] skill

1. Install via ClawHub:
   `clawhub install your-service-skill`

2. Or manually:
   - Clone repo: `git clone https://github.com/yourcompany/skills`
   - Copy skill folder to `~/.openclaw/skills/`

3. Configure API key in `~/.openclaw/openclaw.json`:
   ```json
   {"skills": {"entries": {"your-service-skill": {"apiKey": "YOUR_KEY"}}}}
   ```

4. Ensure your MCP server is connected

5. Test:
   - Ask: "Set up a new project in [Your Service]"
```

## Positioning Your Skill

Focus on outcomes, not implementation:

```
# Good
"The ProjectHub skill enables teams to set up complete project workspaces
in seconds instead of spending 30 minutes on manual setup."

# Bad
"The ProjectHub skill is a folder containing YAML frontmatter and Markdown
instructions that calls our MCP server tools."
```

## Updating an Existing Skill

- **Preserve the original name.** Don't rename to `skill-name-v2`.
- **Copy to a writable location before editing** if the installed path is read-only (e.g., bundled skills).
- **Re-publish** via `clawhub sync` or re-upload for direct distribution.
- **Communicate changes** to users if behavior changes significantly.
