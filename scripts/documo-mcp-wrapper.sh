#!/usr/bin/env bash
# Documo MCP lane wrapper — reads DOCUMO_* from profile .env at runtime (never in config).
set -euo pipefail
ENV_FILE="/opt/data/profiles/nura/.env"
if [ -f "$ENV_FILE" ]; then
  while IFS='=' read -r k v; do
    case "$k" in
      DOCUMO_*) export "$k=${v//\"/}" ;;
    esac
  done < <(grep -E '^DOCUMO_' "$ENV_FILE" || true)
fi
exec python3 /opt/data/mcp-installs/documo/server.py
