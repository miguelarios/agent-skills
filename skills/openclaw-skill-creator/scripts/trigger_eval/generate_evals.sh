#!/usr/bin/env bash
set -euo pipefail

# skill-eval: Generate an eval set from a skill's description
# Usage: generate_evals.sh <skill-name> [--output <path>] [--count 20]

SKILL_NAME="${1:?Usage: generate_evals.sh <skill-name> [--output <path>] [--count 20]}"
shift

OUTPUT=""
COUNT=20

while [[ $# -gt 0 ]]; do
    case "$1" in
        --output) OUTPUT="${2:?--output requires a path}"; shift 2 ;;
        --count)  COUNT="${2:?--count requires a number}"; shift 2 ;;
        *) echo "Unknown flag: $1"; exit 1 ;;
    esac
done

# Find the skill
SKILL_PATH=""
for dir in \
    "${PWD}/skills/${SKILL_NAME}" \
    "${HOME}/workspaces/main/skills/${SKILL_NAME}" \
    "${HOME}/.openclaw/skills/${SKILL_NAME}" \
    "${HOME}/.agents/skills/${SKILL_NAME}"; do
    if [[ -f "${dir}/SKILL.md" ]]; then
        SKILL_PATH="${dir}/SKILL.md"
        break
    fi
done

if [[ -z "$SKILL_PATH" ]]; then
    echo "❌ Skill not found: ${SKILL_NAME}"
    echo "   Searched: ./skills/, ~/.openclaw/skills/, ~/.agents/skills/"
    exit 1
fi

# Extract description from frontmatter
DESCRIPTION=$(awk '/^---/{n++; next} n==1 && /^description:/{gsub(/^description:[[:space:]]*/, ""); print; exit}' "$SKILL_PATH")

echo "📋 Skill: ${SKILL_NAME}"
echo "📄 Path: ${SKILL_PATH}"
echo "📝 Description: ${DESCRIPTION}"
echo ""
echo "ℹ️  Use this description to create eval prompts."
echo "   For automated generation, run this from an agent session"
echo "   and ask it to create ${COUNT} eval queries (mix of should-trigger"
echo "   and should-not-trigger) based on the description above."
echo ""
echo "   Then save them in the eval set JSON format:"
echo '   [{"id": 1, "name": "...", "prompt": "...", "should_trigger": true/false}]'

if [[ -n "$OUTPUT" ]]; then
    mkdir -p "$(dirname "$OUTPUT")"
    jq -n --arg skill_name "$SKILL_NAME" \
         --arg description "$DESCRIPTION" \
         '{skill_name: $skill_name, description: $description, evals: []}' > "$OUTPUT"
    echo "   Template written to: ${OUTPUT}"
fi
