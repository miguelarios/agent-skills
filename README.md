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

**Bootstrap (one time)**: before the first batch run, install *any* single skill interactively (without `-y`) so the skills CLI writes your agent selection to `~/.agents/.skill-lock.json → lastSelectedAgents`. Every batch run after that reuses that set.

```bash
npx skills add https://github.com/googleworkspace/cli/tree/main/skills/gws-shared
# pick the agents you want — this populates lastSelectedAgents
```

**One-liner (no clone needed):**

```bash
bash -c "$(curl -fsSL https://raw.githubusercontent.com/miguelarios/agent-skills/main/scripts/install-third-party.sh)"
```

- Uses `-g -y` only. The skills CLI routes symlinks to whatever agents are in `lastSelectedAgents` — canonical copy lives in `~/.agents/skills/<name>` with symlinks into each agent's dir.
- Flags:
  - `--dry-run` — preview without installing.
  - `--quiet` / `-q` — suppress the npx TUI banners; show one line per skill (`[13/31] <url> ... ✓`).

**Why no `-a` flag?** Passing `-a <agent>` to `npx skills add` silently switches the install mode from *symlink* to *copy*. That breaks the canonical-plus-symlink pattern and produces independent copies that drift. The script never passes `-a` by default; use a per-skill override only when you genuinely need a subset (and accept the copy).

**Per-skill agent override** (rare — triggers copy mode): append `| agent1,agent2`:

```
# Normal: symlink to lastSelectedAgents
https://github.com/googleworkspace/cli/tree/main/skills/gws-gmail
# Override: COPY to Claude Code only
https://github.com/googleworkspace/cli/tree/main/skills/gws-slides | claude-code
```

**From a local clone:**

```bash
./scripts/install-third-party.sh --dry-run  # preview
./scripts/install-third-party.sh            # install
```

Add a new entry by appending its URL to `third-party-skills.txt` (or removing an entry to stop tracking it).

## Skills

| Skill | Description |
|-------|-------------|
| [agent-skill-creator](skills/agent-skill-creator/) | Create and iterate on agent skills |
| [openclaw-skill-creator](skills/openclaw-skill-creator/) | Create skills using the OpenClaw framework |
| [recipe-manager](skills/recipe-manager/) | Manage recipes in Obsidian |
| [superwhisper-custom-mode](skills/superwhisper-custom-mode/) | Configure SuperWhisper custom modes |
