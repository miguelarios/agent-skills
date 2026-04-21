#!/usr/bin/env bash
# Install every skill listed in ../third-party-skills.txt via `npx skills add`.
# Blank lines and lines starting with # are ignored.
#
# Usage:
#   ./scripts/install-third-party.sh              # install all
#   ./scripts/install-third-party.sh --dry-run    # print commands without running
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
MANIFEST="$SCRIPT_DIR/../third-party-skills.txt"

if [[ ! -f "$MANIFEST" ]]; then
  echo "Manifest not found: $MANIFEST" >&2
  exit 1
fi

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
