#!/usr/bin/env bash
set -euo pipefail

# skill-eval: Record eval results from a subagent run
# Usage: record_result.sh <eval-dir> --side with_skill|without_skill [--triggered true|false] [--output "text"] [--tokens N] [--duration_ms N]
#
# This is called by the agent after a sessions_spawn completes, to save results
# into the eval workspace.

EVAL_DIR="${1:?Usage: record_result.sh <eval-dir> --side <side> [--triggered <bool>] [--output <text>] [--tokens <N>] [--duration_ms <N>]}"
shift

SIDE=""
TRIGGERED=""
OUTPUT=""
TOKENS=""
DURATION_MS=""

while [[ $# -gt 0 ]]; do
    case "$1" in
        --side)       SIDE="${2:?--side requires with_skill|without_skill}"; shift 2 ;;
        --triggered)  TRIGGERED="${2:?--triggered requires true|false}"; shift 2 ;;
        --output)     OUTPUT="${2:?--output requires text}"; shift 2 ;;
        --tokens)     TOKENS="${2:?--tokens requires a number}"; shift 2 ;;
        --duration_ms) DURATION_MS="${2:?--duration_ms requires a number}"; shift 2 ;;
        *) echo "Unknown flag: $1"; exit 1 ;;
    esac
done

if [[ -z "$SIDE" ]]; then
    echo "❌ --side is required"
    exit 1
fi

META="${EVAL_DIR}/eval_metadata.json"
if [[ ! -f "$META" ]]; then
    echo "❌ Metadata not found: ${META}"
    exit 1
fi

# Update the metadata
TMP=$(mktemp)
jq --arg side "$SIDE" \
   --arg status "completed" \
   --arg triggered "${TRIGGERED:-null}" \
   --arg output "${OUTPUT:-null}" \
   --argjson tokens "${TOKENS:-null}" \
   --argjson duration_ms "${DURATION_MS:-null}" \
   '.[$side] = {
        status: $status,
        triggered: (if $triggered == "null" then null else ($triggered == "true") end),
        output: $output,
        tokens: ($tokens | if . == null then null else tonumber end),
        duration_ms: ($duration_ms | if . == null then null else tonumber end)
   }' "$META" > "$TMP"

mv "$TMP" "$META"

# Save output text separately if provided
if [[ -n "$OUTPUT" ]]; then
    echo "$OUTPUT" > "${EVAL_DIR}/${SIDE}/output.txt"
fi

echo "✅ Recorded ${SIDE} result for $(basename "$EVAL_DIR")"
