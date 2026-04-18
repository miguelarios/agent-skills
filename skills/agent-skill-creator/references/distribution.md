# Distribution and Sharing

## Packaging

Use `scripts/package_skill.py` to create a distributable `.skill` file:

```bash
scripts/package_skill.py <path/to/skill-folder>
scripts/package_skill.py <path/to/skill-folder> ./dist
```

The script validates the skill first, then creates a `.skill` file (zip archive with `.skill` extension). Symlinks are rejected for security.

The resulting file can be:
- Uploaded to AI platforms via skills directories
- Installed in local skills directories
- Shared via GitHub or other channels

## Validation

Before packaging, validate your skill against the specification:

```bash
scripts/quick_validate.py <path/to/skill-folder>
```

Checks frontmatter format, naming conventions, description constraints, and file organization.

## Hosting on GitHub

For public skills, structure the repository clearly:

```
your-skill/
├── README.md                    # Repo-level README (for human visitors)
├── your-skill.skill             # Downloadable package
└── your-skill/                  # Skill folder (for contributors)
    ├── SKILL.md
    ├── scripts/
    ├── references/
    └── assets/
```

**README content** (for humans, not included in .skill package):
- What problems the skill solves
- Clear installation instructions
- Example usage with screenshots
- Requirements and dependencies

**Version management:**
- Tag releases
- Maintain CHANGELOG at repo level (not in skill folder)
- The skill folder itself should never contain README.md or CHANGELOG.md

## MCP Integration Documentation

For skills that enhance an MCP server, document how to use both together:

```markdown
## Installing [Your Service] skill

1. Download skill:
   - Clone repo: `git clone https://github.com/yourcompany/skills`
   - Or download ZIP from Releases

2. Install in AI platform:
   - Open Settings > Capabilities > Skills
   - Upload skill folder (zipped)

3. Enable skill:
   - Toggle on [Your Service] skill
   - Ensure your MCP server is connected

4. Test:
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

For MCP-enhanced skills, highlight the combination:

```
"Our MCP server gives the AI assistant access to your Linear projects.
Our skill teaches it your team's sprint planning workflow. Together,
they enable AI-powered project management."
```

## Updating an Existing Skill

- **Preserve the original name.** Don't rename to `skill-name-v2`.
- **Copy to a writable location before editing** if the installed path is read-only.
- **Re-package and re-upload** using the same packaging workflow.
- **Communicate changes** to users if behavior changes significantly.
