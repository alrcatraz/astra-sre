#!/bin/bash
# astra-sre diagnose.sh — Phase 2 parallel diagnostic entry point
# Wraps diagnose.py with env sourcing.
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
DIAGNOSE_PY="$SCRIPT_DIR/diagnose.py"

# Source env for KB path and API keys
ENV_FILE="${HOME}/.hermes/.env"
if [ -f "$ENV_FILE" ]; then
  set -a
  source "$ENV_FILE"
  set +a
fi

exec python3 "$DIAGNOSE_PY" "$@"
