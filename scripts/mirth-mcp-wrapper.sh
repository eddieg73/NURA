#!/usr/bin/env bash
# Mirth Connect MCP lane wrapper — reads MIRTH_* from profile .env at runtime (never in config).
set -euo pipefail
ENV_FILE="/opt/data/profiles/nura/.env"
if [ -f "$ENV_FILE" ]; then
  while IFS='=' read -r k v; do
    case "$k" in
      MIRTH_*) export "$k=${v//\"/}" ;;
    esac
  done < <(grep -E '^MIRTH_' "$ENV_FILE" || true)
fi
exec python3 /opt/data/mcp-installs/mirth/server.py
