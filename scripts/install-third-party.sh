#!/usr/bin/env bash
# Install every skill listed in third-party-skills.txt via `npx skills add`.
# Manifest format (one entry per line):
#   <url>                       # uses the --agents flag (or prompts if unset)
#   <url> | agent1,agent2       # per-skill override (overrides --agents)
# Blank lines and lines starting with # are ignored.
#
# Usage:
#   ./install-third-party.sh --agents claude-code,codex,openclaw
#   ./install-third-party.sh --agents claude-code --dry-run
#   ./install-third-party.sh                        # interactive (prompts per skill)
#
# Brew-style one-liner (runs without cloning the repo):
#   bash -c "$(curl -fsSL https://raw.githubusercontent.com/miguelarios/agent-skills/main/scripts/install-third-party.sh)" _ --agents claude-code,codex
#
# Override manifest location via env:
#   MANIFEST_URL=https://... ./install-third-party.sh --agents ...
set -euo pipefail

DEFAULT_MANIFEST_URL="https://raw.githubusercontent.com/miguelarios/agent-skills/main/third-party-skills.txt"

# ---------- Parse flags ----------
DRY_RUN=0
AGENTS_CSV=""
while [[ $# -gt 0 ]]; do
  case "$1" in
    --dry-run)      DRY_RUN=1; shift ;;
    --agents)       AGENTS_CSV="${2:-}"; shift 2 ;;
    --agents=*)     AGENTS_CSV="${1#--agents=}"; shift ;;
    -h|--help)      sed -n '1,18p' "$0" 2>/dev/null || sed -n '1,18p' <(echo ""); exit 0 ;;
    *)              echo "Unknown flag: $1" >&2; exit 2 ;;
  esac
done

# ---------- Locate manifest ----------
SCRIPT_PATH="${BASH_SOURCE[0]:-$0}"
if [[ -f "$SCRIPT_PATH" ]]; then
  SCRIPT_DIR="$(cd "$(dirname "$SCRIPT_PATH")" && pwd)"
  LOCAL_MANIFEST="$SCRIPT_DIR/../third-party-skills.txt"
else
  LOCAL_MANIFEST=""
fi

MANIFEST_CLEANUP=""
if [[ -n "${MANIFEST_URL:-}" ]]; then
  MANIFEST="$(mktemp)"
  MANIFEST_CLEANUP="$MANIFEST"
  echo "Fetching manifest from $MANIFEST_URL"
  curl -fsSL "$MANIFEST_URL" -o "$MANIFEST"
elif [[ -n "$LOCAL_MANIFEST" && -f "$LOCAL_MANIFEST" ]]; then
  MANIFEST="$LOCAL_MANIFEST"
else
  MANIFEST="$(mktemp)"
  MANIFEST_CLEANUP="$MANIFEST"
  echo "No local manifest found — fetching from $DEFAULT_MANIFEST_URL"
  curl -fsSL "$DEFAULT_MANIFEST_URL" -o "$MANIFEST"
fi
trap '[[ -n "$MANIFEST_CLEANUP" ]] && rm -f "$MANIFEST_CLEANUP"' EXIT

# ---------- Build default agent flags ----------
# Returns the -a flags for a comma-separated agent list, or empty string.
agent_flags() {
  local csv="$1"
  [[ -z "$csv" ]] && return 0
  local IFS=','
  local a
  for a in $csv; do
    a="${a// /}"
    [[ -n "$a" ]] && printf -- '-a %q ' "$a"
  done
}

DEFAULT_AGENT_FLAGS="$(agent_flags "$AGENTS_CSV")"

if [[ -z "$DEFAULT_AGENT_FLAGS" ]]; then
  echo "Warning: no --agents provided — npx skills will prompt once per skill." >&2
  echo "         Pass e.g. --agents claude-code,codex,openclaw to install non-interactively." >&2
fi

# ---------- Dedup warning ----------
dupes=$(grep -v '^[[:space:]]*#' "$MANIFEST" \
        | sed 's/|.*//' | awk 'NF' | sort | uniq -d || true)
if [[ -n "$dupes" ]]; then
  echo "Warning: duplicate URLs in manifest:" >&2
  echo "$dupes" >&2
fi

# ---------- Install loop ----------
total=0
failed=0
failed_urls=()

while IFS= read -r raw_line || [[ -n "$raw_line" ]]; do
  # Strip comments and whitespace
  line="${raw_line%%#*}"
  line="${line#"${line%%[![:space:]]*}"}"
  line="${line%"${line##*[![:space:]]}"}"
  [[ -z "$line" ]] && continue

  # Split "URL | agents"
  url="${line%%|*}"
  url="${url%"${url##*[![:space:]]}"}"
  override=""
  if [[ "$line" == *"|"* ]]; then
    override="${line#*|}"
    override="${override#"${override%%[![:space:]]*}"}"
    override="${override%"${override##*[![:space:]]}"}"
  fi

  if [[ -n "$override" ]]; then
    flags="$(agent_flags "$override")"
  else
    flags="$DEFAULT_AGENT_FLAGS"
  fi
  # Non-interactive when we have agents specified
  [[ -n "$flags" ]] && flags="-y $flags"

  total=$((total + 1))
  echo "[$total] $url${override:+  (agents: $override)}"

  if [[ $DRY_RUN -eq 1 ]]; then
    echo "    (dry-run) npx skills add $flags$url"
    continue
  fi

  # shellcheck disable=SC2086
  if ! eval npx skills add $flags"$url"; then
    failed=$((failed + 1))
    failed_urls+=("$url")
    echo "    ✗ failed"
  fi
done < "$MANIFEST"

echo
echo "Processed: $total   Failed: $failed"
if [[ $failed -gt 0 ]]; then
  echo "Failed URLs:"
  printf '  %s\n' "${failed_urls[@]}"
  exit 1
fi
