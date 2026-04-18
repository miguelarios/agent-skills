#!/usr/bin/env bash
set -euo pipefail

# skill-eval: Setup temporary agent profiles for A/B skill testing
# Usage: setup_agents.sh <skill-name> [--cleanup]

SKILL_NAME="${1:?Usage: setup_agents.sh <skill-name> [--cleanup]}"
ACTION="setup"
[[ "${2:-}" == "--cleanup" ]] && ACTION="cleanup"

CONFIG_PATH="${OPENCLAW_CONFIG_PATH:-$HOME/.openclaw/openclaw.json}"
BACKUP_PATH="/tmp/skill-eval-config-backup-${SKILL_NAME}.json"

EVAL_WITH="eval-with-${SKILL_NAME}"
EVAL_WITHOUT="eval-without-${SKILL_NAME}"

cleanup() {
    echo "🧹 Cleaning up eval agent profiles for: ${SKILL_NAME}"
    if [[ -f "$BACKUP_PATH" ]]; then
        cp "$BACKUP_PATH" "$CONFIG_PATH"
        echo "   ✅ Restored config from backup"
        rm -f "$BACKUP_PATH"
    else
        echo "   No backup found (may already be clean)"
    fi
    echo "   ⚠️  Run 'openclaw gateway restart' for changes to take effect."
}

setup() {
    echo "🔧 Setting up eval agent profiles for skill: ${SKILL_NAME}"
    
    if [[ ! -f "$CONFIG_PATH" ]]; then
        echo "❌ Config not found: ${CONFIG_PATH}"
        exit 1
    fi
    
    # Backup current config
    cp "$CONFIG_PATH" "$BACKUP_PATH"
    echo "   ✅ Backed up config to ${BACKUP_PATH}"
    
    # Add eval agents using jq
    TMP_CONFIG=$(mktemp)
    jq --arg with_id "$EVAL_WITH" \
       --arg without_id "$EVAL_WITHOUT" \
       --arg skill "$SKILL_NAME" \
       '
        if .agents == null then .agents = {} else . end |
        if .agents.list == null then .agents.list = [] else . end |
        # Remove any existing eval agents for this skill
        .agents.list = [.agents.list[] | select(.id != $with_id and .id != $without_id)] |
        # Add new eval agents
        .agents.list += [
            {id: $with_id, skills: [$skill]},
            {id: $without_id, skills: []}
        ]
       ' "$CONFIG_PATH" > "$TMP_CONFIG"
    
    mv "$TMP_CONFIG" "$CONFIG_PATH"
    
    echo "   ✅ Added agent profiles:"
    echo "     → ${EVAL_WITH} (skills: [${SKILL_NAME}])"
    echo "     → ${EVAL_WITHOUT} (skills: [])"
    echo ""
    echo "   ⚠️  Gateway restart required. Run: openclaw gateway restart"
}

case "$ACTION" in
    setup)   setup ;;
    cleanup) cleanup ;;
esac
