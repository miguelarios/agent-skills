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

## Third-party skills I use

Skills from other repos that I install but don't maintain are tracked in [`third-party-skills.txt`](third-party-skills.txt).

**One-liner (no clone needed):**

```bash
bash -c "$(curl -fsSL https://raw.githubusercontent.com/miguelarios/agent-skills/main/scripts/install-third-party.sh)"
```

Add `--dry-run` to preview without installing:

```bash
bash -c "$(curl -fsSL https://raw.githubusercontent.com/miguelarios/agent-skills/main/scripts/install-third-party.sh)" _ --dry-run
```

**From a local clone:**

```bash
./scripts/install-third-party.sh            # install every URL in the manifest
./scripts/install-third-party.sh --dry-run  # preview without running
```

Add a new entry by appending its URL to `third-party-skills.txt` (or removing an entry to stop tracking it).

## Skills

| Skill | Description |
|-------|-------------|
| [agent-skill-creator](skills/agent-skill-creator/) | Create and iterate on agent skills |
| [openclaw-skill-creator](skills/openclaw-skill-creator/) | Create skills using the OpenClaw framework |
| [recipe-manager](skills/recipe-manager/) | Manage recipes in Obsidian |
| [superwhisper-custom-mode](skills/superwhisper-custom-mode/) | Configure SuperWhisper custom modes |
