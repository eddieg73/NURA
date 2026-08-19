#!/usr/bin/env bash
set -euo pipefail

unset PYTHONHOME QDRANT_LOCAL_PATH QDRANT_API_KEY
export PYTHONPATH=""
export QDRANT_URL="${QDRANT_URL:-http://127.0.0.1:6333}"
export COLLECTION_NAME="${COLLECTION_NAME:-nura-os}"

# GUARD (2026-08-01): memory lane must stay local. Remote qdrant requires explicit opt-in.
if [ "${QDRANT_URL}" != "http://127.0.0.1:6333" ] && [ "${NURA_ALLOW_REMOTE_QDRANT:-0}" != "1" ]; then
  echo "REFUSED: QDRANT_URL is not local (${QDRANT_URL}). Memory lane stays 127.0.0.1:6333. Set NURA_ALLOW_REMOTE_QDRANT=1 only for a NEW named lane." >&2
  exit 1
fi

/opt/data/scripts/qdrant_server_manager.py ensure --quiet

log_file="/opt/data/logs/qdrant-mcp.log"
mkdir -p "$(dirname "$log_file")"
chmod 700 "$(dirname "$log_file")"
printf '\n[%s] starting qdrant MCP uid=%s cwd=%s\n' "$(date -u +%FT%TZ)" "$(id -u)" "$(pwd)" >> "$log_file"

exec /opt/data/mcp-qdrant-venv/bin/mcp-server-qdrant "$@" 2>> "$log_file"
