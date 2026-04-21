#!/usr/bin/env bash
# Install every skill listed in third-party-skills.txt via `npx skills add`.
# Blank lines and lines starting with # are ignored.
#
# Usage:
#   ./scripts/install-third-party.sh              # install all (local manifest)
#   ./scripts/install-third-party.sh --dry-run    # print commands without running
#
# Brew-style one-liner (runs without cloning the repo):
#   bash -c "$(curl -fsSL https://raw.githubusercontent.com/miguelarios/agent-skills/main/scripts/install-third-party.sh)"
#
# Override manifest location via env:
#   MANIFEST_URL=https://... ./install-third-party.sh
set -euo pipefail

DEFAULT_MANIFEST_URL="https://raw.githubusercontent.com/miguelarios/agent-skills/main/third-party-skills.txt"

# Locate manifest: prefer a local copy next to the script, else fetch from the repo.
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

DRY_RUN=0
[[ "${1:-}" == "--dry-run" ]] && DRY_RUN=1

# Warn on duplicate URLs before installing
dupes=$(grep -v '^[[:space:]]*#' "$MANIFEST" | grep -v '^[[:space:]]*$' | sort | uniq -d || true)
if [[ -n "$dupes" ]]; then
  echo "Warning: duplicate URLs in manifest:" >&2
  echo "$dupes" >&2
fi

total=0
failed=0
failed_urls=()

while IFS= read -r line || [[ -n "$line" ]]; do
  line="${line%%#*}"
  line="${line##[[:space:]]}"
  line="${line%%[[:space:]]}"
  [[ -z "$line" ]] && continue

  total=$((total + 1))
  echo "[$total] $line"

  if [[ $DRY_RUN -eq 1 ]]; then
    echo "    (dry-run) npx skills add $line"
    continue
  fi

  if ! npx skills add "$line"; then
    failed=$((failed + 1))
    failed_urls+=("$line")
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
