# Agent Skills

A collection of skills for AI coding agents (Claude Code, Codex, Goose, etc.).

## Install

```bash
# Install all skills to Claude Code, Codex, and Goose
npx skills add -g miguelarios/agent-skills -a claude-code -a codex -a goose -y

# Install a specific skill
npx skills add -g miguelarios/agent-skills -s recipe-manager -a claude-code -a codex -a goose -y
```

## Update

```bash
# Check for updates
npx skills check

# Pull latest versions
npx skills update
```

## Skills

| Skill | Description |
|-------|-------------|
| [agent-skill-creator](skills/agent-skill-creator/) | Create and iterate on agent skills |
| [openclaw-skill-creator](skills/openclaw-skill-creator/) | Create skills using the OpenClaw framework |
| [recipe-manager](skills/recipe-manager/) | Manage recipes in Obsidian |
| [superwhisper-custom-mode](skills/superwhisper-custom-mode/) | Configure SuperWhisper custom modes |
