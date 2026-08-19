#!/usr/bin/env bash
# Moltbook MCP lane wrapper — reads MOLTBOOK_* from profile .env at runtime.
# SECURITY: API key only ever sent to https://www.moltbook.com/api/v1/* (never anywhere else).
set -euo pipefail
ENV_FILE="/opt/data/profiles/nura/.env"
if [ -f "$ENV_FILE" ]; then
  while IFS='=' read -r k v; do
    case "$k" in
      MOLTBOOK_*) export "$k=${v//\"/}" ;;
    esac
  done < <(grep -E '^MOLTBOOK_' "$ENV_FILE" || true)
fi
exec python3 /opt/data/mcp-installs/moltbook/server.py
