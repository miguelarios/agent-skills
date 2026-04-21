#!/usr/bin/env bash
# Install every skill listed in third-party-skills.txt via `npx skills add`.
#
# Default behavior: `-g -y` only — the skills CLI then routes symlinks to the
# agents recorded in ~/.agents/.skill-lock.json's `lastSelectedAgents` field.
# This keeps the canonical copy in ~/.agents/skills/<name> with symlinks into
# each configured agent's dir. DO NOT pass `-a` by default: the CLI silently
# switches from symlink to *copy* when `-a` is present, breaking the canonical
# pattern.
#
# BOOTSTRAP REQUIREMENT: before first use, run ONE skill install interactively
# (no flags after the URL) so the CLI prompts you to pick agents and writes
# them to `lastSelectedAgents`. Every batch run after that reuses that set.
#   npx skills add <any-skill-url>
#
# Manifest format (one entry per line):
#   <url>                       # normal: symlink to lastSelectedAgents
#   <url> | agent1,agent2       # per-skill subset override — WARNING: this
#                                 triggers the copy path, not symlink. Only use
#                                 when you truly need a different agent set.
# Blank lines and lines starting with # are ignored.
#
# Usage:
#   ./install-third-party.sh
#   ./install-third-party.sh --dry-run
#
# Brew-style one-liner (no clone):
#   bash -c "$(curl -fsSL https://raw.githubusercontent.com/miguelarios/agent-skills/main/scripts/install-third-party.sh)"
#
# Override manifest location via env:
#   MANIFEST_URL=https://... ./install-third-party.sh
set -euo pipefail

DEFAULT_MANIFEST_URL="https://raw.githubusercontent.com/miguelarios/agent-skills/main/third-party-skills.txt"
LOCK_FILE="${HOME}/.agents/.skill-lock.json"

# ---------- Parse flags ----------
# When invoked via `bash -c "$(curl ...)" --dry-run` (without a `_` placeholder
# for $0), the flag lands in $0. Fold $0 into the positional args if it looks
# like one of our flags, so both invocation styles work.
if [[ "${0:-}" == --dry-run || "${0:-}" == -h || "${0:-}" == --help ]]; then
  set -- "$0" "$@"
fi

DRY_RUN=0
while [[ $# -gt 0 ]]; do
  case "$1" in
    --dry-run)  DRY_RUN=1; shift ;;
    -h|--help)  sed -n '1,40p' "${BASH_SOURCE[0]:-/dev/stdin}" 2>/dev/null; exit 0 ;;
    *)          echo "Unknown flag: $1" >&2; exit 2 ;;
  esac
done

# ---------- Bootstrap check ----------
if [[ ! -f "$LOCK_FILE" ]] || ! jq -e '.lastSelectedAgents | length > 0' "$LOCK_FILE" >/dev/null 2>&1; then
  echo "WARNING: ~/.agents/.skill-lock.json is missing or has no lastSelectedAgents." >&2
  echo "         Run one install interactively first (e.g.  npx skills add <any-url>)" >&2
  echo "         so the CLI records your agent set. Otherwise this batch will prompt" >&2
  echo "         for every skill or install to an unintended default set." >&2
  echo >&2
fi

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

# ---------- Helpers ----------
# Build `-a agent1 -a agent2 ...` from a CSV list.
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

while IFS= read -r -u 3 raw_line || [[ -n "$raw_line" ]]; do
  line="${raw_line%%#*}"
  line="${line#"${line%%[![:space:]]*}"}"
  line="${line%"${line##*[![:space:]]}"}"
  [[ -z "$line" ]] && continue

  url="${line%%|*}"
  url="${url%"${url##*[![:space:]]}"}"
  override=""
  if [[ "$line" == *"|"* ]]; then
    override="${line#*|}"
    override="${override#"${override%%[![:space:]]*}"}"
    override="${override%"${override##*[![:space:]]}"}"
  fi

  total=$((total + 1))

  if [[ -n "$override" ]]; then
    # Override path: use -a, which switches the CLI from symlink to copy.
    flags="-g -y $(agent_flags "$override")"
    echo "[$total] $url  (agents: $override — COPY MODE)"
  else
    # Default path: -g -y only; CLI symlinks to lastSelectedAgents.
    flags="-g -y "
    echo "[$total] $url"
  fi

  if [[ $DRY_RUN -eq 1 ]]; then
    echo "    (dry-run) npx skills add $flags$url"
    continue
  fi

  # Redirect stdin from /dev/null so `npx skills add` can't consume the rest
  # of the manifest (fd 3 feeds the loop; npx inherits stdin otherwise).
  # shellcheck disable=SC2086
  if ! eval npx skills add $flags"$url" < /dev/null; then
    failed=$((failed + 1))
    failed_urls+=("$url")
    echo "    ✗ failed"
  fi
done 3< "$MANIFEST"

echo
echo "Processed: $total   Failed: $failed"
if [[ $failed -gt 0 ]]; then
  echo "Failed URLs:"
  printf '  %s\n' "${failed_urls[@]}"
  exit 1
fi
