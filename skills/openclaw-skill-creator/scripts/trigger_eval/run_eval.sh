#!/usr/bin/env bash
set -euo pipefail

# skill-eval: Main eval runner
# Prepares workspace and outputs instructions for the agent to execute spawns.
#
# Usage: run_eval.sh <skill-name> --eval-set <path> [--mode trigger|quality] [--runs 3] [--workspace <dir>]
#
# The agent should call this script, then use sessions_spawn for each eval case
# with agentId "eval-with-<skill>" and "eval-without-<skill>".
# Save outputs to the workspace dirs, then run grade.sh.

SKILL_NAME="${1:?Usage: run_eval.sh <skill-name> --eval-set <path> [--mode trigger|quality] [--runs 3]}"
shift

MODE="trigger"
RUNS=3
EVAL_SET=""
WORKSPACE=""

while [[ $# -gt 0 ]]; do
    case "$1" in
        --eval-set)  EVAL_SET="${2:?--eval-set requires a path}"; shift 2 ;;
        --mode)      MODE="${2:?--mode requires trigger|quality}"; shift 2 ;;
        --runs)      RUNS="${2:?--runs requires a number}"; shift 2 ;;
        --workspace) WORKSPACE="${2:?--workspace requires a path}"; shift 2 ;;
        *) echo "Unknown flag: $1"; exit 1 ;;
    esac
done

if [[ -z "$EVAL_SET" ]]; then
    echo "❌ --eval-set is required"
    exit 1
fi

if [[ ! -f "$EVAL_SET" ]]; then
    echo "❌ Eval set not found: ${EVAL_SET}"
    exit 1
fi

if [[ -z "$WORKSPACE" ]]; then
    WORKSPACE="/tmp/skill-eval-${SKILL_NAME}-$(date +%Y%m%d-%H%M%S)"
fi

ITERATION_DIR="${WORKSPACE}/iteration-1"
mkdir -p "$ITERATION_DIR"
cp "$EVAL_SET" "${WORKSPACE}/eval_set.json"

EVAL_WITH="eval-with-${SKILL_NAME}"
EVAL_WITHOUT="eval-without-${SKILL_NAME}"

# Write run config for the agent
jq -n --arg skill_name "$SKILL_NAME" \
     --arg eval_with "$EVAL_WITH" \
     --arg eval_without "$EVAL_WITHOUT" \
     --arg mode "$MODE" \
     --argjson runs "$RUNS" \
     '{
        skill_name: $skill_name,
        agent_with_skill: $eval_with,
        agent_without_skill: $eval_without,
        mode: $mode,
        runs_per_prompt: $runs
     }' > "${WORKSPACE}/run_config.json"

EVAL_COUNT=$(jq '.evals | length' "$EVAL_SET")

echo "WORKSPACE=${WORKSPACE}"
echo "ITERATION=${ITERATION_DIR}"
echo "EVAL_COUNT=${EVAL_COUNT}"
echo "MODE=${MODE}"
echo "RUNS=${RUNS}"
echo "AGENT_WITH=${EVAL_WITH}"
echo "AGENT_WITHOUT=${EVAL_WITHOUT}"
echo ""

for i in $(seq 0 $((EVAL_COUNT - 1))); do
    EVAL_NAME=$(jq -r --argjson idx "$i" '.evals[$idx].name // "eval-'$i'"' "$EVAL_SET")
    PROMPT=$(jq -r --argjson idx "$i" '.evals[$idx].prompt' "$EVAL_SET")
    SHOULD_TRIGGER=$(jq -r --argjson idx "$i" 'if .evals[$idx].should_trigger == null then true else .evals[$idx].should_trigger end' "$EVAL_SET")
    
    EVAL_DIR="${ITERATION_DIR}/eval-${i}"
    mkdir -p "${EVAL_DIR}/with_skill" "${EVAL_DIR}/without_skill"
    
    # Write eval metadata
    ASSERTIONS=$(jq -r --argjson idx "$i" '.evals[$idx].assertions // []' "$EVAL_SET")
    jq -n --argjson id "$i" \
         --arg name "$EVAL_NAME" \
         --arg prompt "$PROMPT" \
         --argjson should_trigger "$SHOULD_TRIGGER" \
         --argjson assertions "$ASSERTIONS" \
         '{
            eval_id: $id,
            eval_name: $name,
            prompt: $prompt,
            should_trigger: $should_trigger,
            assertions: $assertions,
            with_skill: {status: "pending", triggered: null, output: null, tokens: null, duration_ms: null},
            without_skill: {status: "pending", triggered: null, output: null, tokens: null, duration_ms: null}
         }' > "${EVAL_DIR}/eval_metadata.json"
    
    echo "EVAL_${i}_NAME=${EVAL_NAME}"
    echo "EVAL_${i}_SHOULD_TRIGGER=${SHOULD_TRIGGER}"
done
