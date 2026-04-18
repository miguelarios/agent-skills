# Claude Skills Repo Strategy: Public + Private

## Problem
Some Claude skills should be public on GitHub (shareable), others should stay private.

## Recommended: Two GitHub Repos

```
~/.agents/skills/
├── public-skill-1/    → symlink from public repo
├── public-skill-2/
├── private-skill-1/   → symlink from private repo
└── private-skill-2/
```

## Setup

```bash
# Create two repos on GitHub
# 1. github.com/you/claude-skills        (public)
# 2. github.com/you/claude-skills-private (private)

# Clone them side by side
cd ~/.agents
git clone git@github.com:you/claude-skills.git public
git clone git@github.com:you/claude-skills-private.git private

# Symlink each skill into the skills/ directory Claude reads from
ln -s ../public/tavily-cli skills/tavily-cli
ln -s ../private/my-secret-skill skills/my-secret-skill
```

## Result
- `~/.agents/public/` → public GitHub repo (share with the world)
- `~/.agents/private/` → private GitHub repo (your eyes only)
- `~/.agents/skills/` → symlinks pointing to skills from both repos

## Why This Works
- Each repo is independently version-controlled
- Adding a new skill = add it to the right repo + create one symlink
- The symlink layer (`skills/`) is what Claude reads, and it doesn't care where the files come from
- You can share the public repo URL for others to install skills from

## Current State (for reference)
Skills currently in `~/.agents/skills/`:
- find-skills
- tavily-best-practices
- tavily-cli
- tavily-crawl
- tavily-extract
- tavily-map
- tavily-research
- tavily-search

These are already symlinks pointing to `../../.agents/skills/<name>` (self-referencing — likely from the install process).

## Open Questions
- GitHub username / repo names?
- Which existing skills are public vs private?
- Any automation needed for the symlink setup?
