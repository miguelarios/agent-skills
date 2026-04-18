---
name: mcporter
description: Use the mcporter CLI to list, configure, auth, and call MCP servers/tools directly (HTTP or stdio), including ad-hoc servers, config edits, and CLI/type generation.
homepage: http://mcporter.dev
metadata: {"clawdbot":{"emoji":"📦","requires":{"bins":["mcporter"]},"install":[{"id":"node","kind":"node","package":"mcporter","bins":["mcporter"],"label":"Install mcporter (node)"}]}}
---

# mcporter

Use `mcporter` to work with MCP servers directly.

Quick start
- `mcporter list`
- `mcporter list <server> --schema`
- `mcporter call <server.tool> key=value`

Call tools — **prefer function-call syntax**
- Function syntax (recommended): `mcporter call 'server.tool(arg1: value1, arg2: ["array"])' --output json`
- Full URL: `mcporter call https://api.example.com/mcp.fetch url:https://example.com`
- Stdio: `mcporter call --stdio "bun run ./server.ts" scrape url=https://example.com`
- JSON payload: `mcporter call <server.tool> --args '{"limit":5}'`

CLI flag forms like `--arg key '["value"]'` won't parse JSON arrays correctly, and `--json` mode silently drops fields. Function-call syntax is the only mode that reliably handles all argument types (strings, arrays, objects, nested values), so reach for it by default.

Auth + config
- OAuth: `mcporter auth <server | url> [--reset]`
- Config: `mcporter config list|get|add|remove|import|login|logout`

Daemon
- `mcporter daemon start|status|stop|restart`

Codegen
- CLI: `mcporter generate-cli --server <name>` or `--command <url>`
- Inspect: `mcporter inspect-cli <path> [--json]`
- TS: `mcporter emit-ts <server> --mode client|types`

Notes
- Config default: `./config/mcporter.json` (override with `--config`).
- Prefer `--output json` for machine-readable results.

## Workflow: Always Check Schema First

Before calling any MCP tool, inspect its schema. This surfaces correct argument types, required vs optional params, and dedicated tools you might otherwise miss (e.g., `delete_email` vs `move_email` to Trash).

```bash
# List available MCP servers
mcporter list

# List all tools on a server with their descriptions
mcporter list-tools <server> --schema --output json | jq '.tools[] | "\(.name): \(.description)"'

# Inspect a specific tool's input schema
mcporter list-tools <server> --json | jq '.tools[] | select(.name == "<tool_name>") | {name, description, inputSchema}'
```

Never guess at parameter names or types. Common mistakes: `calendar_id` should be `calendar`, `contact_id` should be `uid`, and array vs string types vary by tool.

## Calling Tools: Correct vs Wrong

**Correct — function-call syntax handles arrays natively:**

```bash
mcporter call 'email.send_email(to: ["user@example.com"], subject: "Hello", text: "Body")' --output json
```

**Wrong — `--arg` flag won't parse the array:**

```bash
mcporter call email.send_email --arg to '["user@example.com"]' --output json
```

**Always verify:** After making changes, list/check the result to confirm it worked.
