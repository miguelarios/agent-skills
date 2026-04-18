# OpenClaw Configuration Reference

This document covers OpenClaw-specific configuration that affects skills: gating, config overrides, installer specs, environment injection, and sandboxing considerations.

## Load-Time Gating

OpenClaw filters skills at load time using `metadata.openclaw` in frontmatter. If a skill's requirements aren't met, it's excluded from the session entirely — the model never sees it.

### Gating Fields

All fields are optional. If no `metadata.openclaw` is present, the skill is always eligible.

```yaml
metadata: {"openclaw": {"requires": {"bins": ["uv"], "env": ["GEMINI_API_KEY"], "config": ["browser.enabled"]}, "primaryEnv": "GEMINI_API_KEY"}}
```

- **`requires.bins`** — All listed binaries must exist on `PATH`. Checked on the host at skill load time.
- **`requires.anyBins`** — At least one listed binary must exist on `PATH`.
- **`requires.env`** — Each env var must exist in the process environment or be provided via `skills.entries.<key>.env` or `skills.entries.<key>.apiKey` in config.
- **`requires.config`** — Each path (e.g., `browser.enabled`) must be truthy in `~/.openclaw/openclaw.json`.
- **`os`** — List of platforms: `darwin`, `linux`, `win32`. If set, the skill is only eligible on those OSes.
- **`always: true`** — Skip all other gates. The skill is always included.

### Gating Decision Flow

1. If `always: true` → include
2. If `os` is set and current platform not in list → exclude
3. If any `requires.bins` missing → exclude
4. If no `requires.anyBins` present → exclude
5. If any `requires.env` missing (and not in config) → exclude
6. If any `requires.config` path falsy → exclude
7. Otherwise → include (unless disabled in config)

### Sandboxing Note

`requires.bins` is checked on the **host** at skill load time. If the agent runs sandboxed, the binary must also exist inside the container. Install via `agents.defaults.sandbox.docker.setupCommand` (runs once after container creation). Package installs require network egress, a writable root FS, and a root user in the sandbox.

## Config Overrides (`~/.openclaw/openclaw.json`)

Skills can be toggled and configured under `skills.entries`:

```json5
{
  "skills": {
    "entries": {
      "nano-banana-pro": {
        "enabled": true,
        "apiKey": "GEMINI_KEY_HERE",
        "env": {
          "GEMINI_API_KEY": "GEMINI_KEY_HERE"
        },
        "config": {
          "endpoint": "https://example.invalid",
          "model": "nano-pro"
        }
      },
      "peekaboo": { "enabled": true },
      "sag": { "enabled": false }
    }
  }
}
```

**Rules:**
- Config keys match the **skill name** by default. If a skill defines `metadata.openclaw.skillKey`, use that key instead.
- `enabled: false` disables the skill even if it's bundled/installed.
- `env`: injected only if the variable isn't already set in the process environment.
- `apiKey`: convenience for skills that declare `metadata.openclaw.primaryEnv`. The value is injected as that env var.
- `config`: optional bag for custom per-skill fields.
- `allowBundled`: optional allowlist for bundled skills only. If set, only listed bundled skills are eligible (managed/workspace skills unaffected).

**Note:** If the skill name contains hyphens, quote the key in JSON5.

## Environment Injection

When an agent run starts, OpenClaw:

1. Reads skill metadata
2. Applies any `skills.entries.<key>.env` or `skills.entries.<key>.apiKey` to `process.env`
3. Builds the system prompt with eligible skills
4. Restores the original environment after the run ends

This is scoped to the agent run, not a global shell environment. Secrets stay out of prompts and logs.

## Installer Specs

The `install` field in `metadata.openclaw` tells the macOS Skills UI how to install dependencies. Each entry is an installer spec:

```yaml
metadata: {"openclaw": {"requires": {"bins": ["gemini"]}, "install": [{"id": "brew", "kind": "brew", "formula": "gemini-cli", "bins": ["gemini"], "label": "Install Gemini CLI (brew)"}]}}
```

### Installer Kinds

- **`brew`** — Homebrew formula. Fields: `formula`, `bins`, `label`.
- **`node`** — npm/pnpm/yarn/bun global install. Honors `skills.install.nodeManager` in config (default: npm).
- **`go`** — Go install. If `go` is missing and `brew` is available, the gateway installs Go via Homebrew first.
- **`uv`** — Python UV installer.
- **`download`** — Direct download. Fields: `url` (required), `archive` (`tar.gz`|`tar.bz2`|`zip`), `extract` (default: auto), `stripComponents`, `targetDir` (default: `~/.openclaw/tools/<skillKey>`).

### Selection Logic

- If multiple installers listed, the gateway picks a single preferred option (brew when available, otherwise node).
- If all installers are `download`, OpenClaw lists each entry so the user can see available artifacts.
- Installer specs can include `os: ["darwin"|"linux"|"win32"]` to filter by platform.

## Skills Watcher

OpenClaw watches skill folders by default and refreshes the skills snapshot when `SKILL.md` files change:

```json5
{
  "skills": {
    "load": {
      "watch": true,
      "watchDebounceMs": 250,
      "extraDirs": ["/path/to/shared/skills"]
    }
  }
}
```

Changes are picked up on the next agent turn (hot reload). This is useful during development.

## Remote macOS Nodes

If the Gateway runs on Linux but a macOS node is connected with `system.run` allowed, OpenClaw can treat macOS-only skills as eligible when the required binaries are present on that node. The agent executes those skills via the `nodes` tool (typically `nodes.run`).

When designing skills that may run on remote nodes, note that if the macOS node goes offline, the skills remain visible but invocations will fail until the node reconnects.

## Plugin-Shipped Skills

Plugins can ship their own skills by listing `skills` directories in `openclaw.plugin.json` (paths relative to plugin root). Plugin skills load when the plugin is enabled and participate in normal skill precedence rules. Gate them via `metadata.openclaw.requires.config` on the plugin's config entry.
