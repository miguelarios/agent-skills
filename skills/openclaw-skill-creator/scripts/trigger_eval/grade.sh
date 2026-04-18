#!/usr/bin/env bash
set -euo pipefail

# skill-eval: Grade eval outputs
# Usage: grade.sh <workspace-dir> [--skill-name <name>]

WORKSPACE="${1:?Usage: grade.sh <workspace-dir> [--skill-name <name>]}"
shift

SKILL_NAME=""
while [[ $# -gt 0 ]]; do
    case "$1" in
        --skill-name) SKILL_NAME="${2:?--skill-name requires a name}"; shift 2 ;;
        *) echo "Unknown flag: $1"; exit 1 ;;
    esac
done

if [[ -z "$SKILL_NAME" ]]; then
    if [[ -f "${WORKSPACE}/run_config.json" ]]; then
        SKILL_NAME=$(jq -r '.skill_name' "${WORKSPACE}/run_config.json")
    fi
fi

if [[ ! -d "$WORKSPACE" ]]; then
    echo "❌ Workspace not found: ${WORKSPACE}"
    exit 1
fi

ITERATION_DIR="${WORKSPACE}/iteration-1"
if [[ ! -d "$ITERATION_DIR" ]]; then
    echo "❌ No iteration-1 directory found"
    exit 1
fi

TOTAL=0
PASSED=0
FAILED=0
SKIPPED=0
DETAILS="[]"

for EVAL_DIR in "${ITERATION_DIR}"/eval-*; do
    [[ -d "$EVAL_DIR" ]] || continue
    META="${EVAL_DIR}/eval_metadata.json"
    [[ -f "$META" ]] || continue

    EVAL_ID=$(basename "$EVAL_DIR" | sed 's/eval-//')
    EVAL_NAME=$(jq -r '.eval_name // "unknown"' "$META")
    SHOULD_TRIGGER=$(jq -r 'if .should_trigger == null then true else .should_trigger end' "$META")
    WS_STATUS=$(jq -r '.with_skill.status // "pending"' "$META")
    TRIGGERED=$(jq -r '.with_skill.triggered // null' "$META")

    if [[ "$WS_STATUS" == "pending" ]]; then
        SKIPPED=$((SKIPPED + 1))
        continue
    fi

    RESULT="FAIL"
    if [[ "$SHOULD_TRIGGER" == "true" && "$TRIGGERED" == "true" ]]; then
        RESULT="PASS"
        PASSED=$((PASSED + 1))
    elif [[ "$SHOULD_TRIGGER" == "false" && ( "$TRIGGERED" == "false" || "$TRIGGERED" == "null" ) ]]; then
        RESULT="PASS"
        PASSED=$((PASSED + 1))
    else
        FAILED=$((FAILED + 1))
    fi

    TOTAL=$((TOTAL + 1))

    DETAILS=$(echo "$DETAILS" | jq \
        --argjson id "$EVAL_ID" \
        --arg name "$EVAL_NAME" \
        --arg result "$RESULT" \
        --argjson should_trigger "$SHOULD_TRIGGER" \
        --arg triggered "${TRIGGERED:-null}" \
        '. += [{
            eval_id: $id,
            eval_name: $name,
            should_trigger: $should_trigger,
            triggered: $triggered,
            result: $result
        }]')
done

# Calculate rate
if [[ $TOTAL -gt 0 ]]; then
    RATE_INT=$(( PASSED * 100 / TOTAL ))
    RATE_DECIMAL=$(awk -v p="$PASSED" -v t="$TOTAL" 'BEGIN { printf "%.1f", p * 100 / t }')
else
    RATE_INT=0
    RATE_DECIMAL="0.0"
fi

echo "SKILL=${SKILL_NAME}"
echo "TOTAL=${TOTAL}"
echo "PASSED=${PASSED}"
echo "FAILED=${FAILED}"
echo "SKIPPED=${SKIPPED}"
echo "RATE=${RATE_DECIMAL}%"
echo ""

# Write benchmark.json
jq -n \
    --arg skill_name "${SKILL_NAME:-unknown}" \
    --arg mode "trigger" \
    --arg timestamp "$(date -u +%Y-%m-%dT%H:%M:%SZ)" \
    --argjson total "$TOTAL" \
    --argjson passed "$PASSED" \
    --argjson failed "$FAILED" \
    --argjson skipped "$SKIPPED" \
    --argjson rate "$RATE_INT" \
    --argjson details "$DETAILS" \
    '{
        skill_name: $skill_name,
        mode: $mode,
        timestamp: $timestamp,
        total_evals: $total,
        passed: $passed,
        failed: $failed,
        skipped: $skipped,
        pass_rate: $rate,
        details: $details
    }' > "${WORKSPACE}/benchmark.json"

echo "BENCHMARK=${WORKSPACE}/benchmark.json"
