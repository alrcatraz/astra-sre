#!/bin/bash
# astra-sre-refresh.sh — Monthly maintenance tasks
# 1. Check if Hermes version has changed
# 2. Run learn.py for new repeat patterns
# Silent mode (no_agent): only output when there's something to report
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
LEARN_PY="$SCRIPT_DIR/learn.py"
HERMES_VERSION_FILE="${HOME}/.hermes/.version"
REPORT=""

# ── Check Hermes version ──────────────────────────────────────
if command -v hermes &>/dev/null; then
    CURRENT_VER=$(hermes --version 2>/dev/null | head -1 || echo "unknown")
    if [ -f "$HERMES_VERSION_FILE" ]; then
        LAST_VER=$(cat "$HERMES_VERSION_FILE")
    else
        LAST_VER="unknown"
    fi

    if [ "$CURRENT_VER" != "$LAST_VER" ]; then
        REPORT+="📦 Hermes version changed: ${LAST_VER} → ${CURRENT_VER}"$'\n'
        REPORT+="    Check if Gateway message length limits in dynamic_ref need updating"$'\n'
        echo "$CURRENT_VER" > "$HERMES_VERSION_FILE"
    fi
fi

# ── Run learn.py for new patterns ──────────────────────────────
# kB_access.py reads $ASTRA_KB_PATH; source .env if available
ENV_FILE="${HOME}/.hermes/.env"
if [ -f "$ENV_FILE" ]; then
    set -a
    source "$ENV_FILE"
    set +a
fi

LEARN_OUTPUT=$(python3 "$LEARN_PY" --cron 2>&1) || true
if [ -n "$LEARN_OUTPUT" ]; then
    REPORT+="${LEARN_OUTPUT}"$'\n'
fi

# ── Output ────────────────────────────────────────────────────
if [ -n "$REPORT" ]; then
    echo "$REPORT"
fi
exit 0
