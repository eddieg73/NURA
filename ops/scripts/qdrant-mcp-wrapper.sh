#!/usr/bin/env bash
set -euo pipefail

unset PYTHONHOME QDRANT_LOCAL_PATH QDRANT_API_KEY
export PYTHONPATH=""
export QDRANT_URL="http://127.0.0.1:6333"
export COLLECTION_NAME="nura-os"

/opt/data/scripts/qdrant_server_manager.py ensure --quiet

log_file="/opt/data/logs/qdrant-mcp.log"
mkdir -p "$(dirname "$log_file")"
chmod 700 "$(dirname "$log_file")"
printf '\n[%s] starting qdrant MCP uid=%s cwd=%s\n' "$(date -u +%FT%TZ)" "$(id -u)" "$(pwd)" >> "$log_file"

exec /opt/data/mcp-qdrant-venv/bin/mcp-server-qdrant "$@" 2>> "$log_file"
