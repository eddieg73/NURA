#!/usr/bin/env bash
# Granola MCP lane wrapper — reads GRANOLA_API_KEY from profile .env at runtime.
set -euo pipefail
ENV_FILE="/opt/data/profiles/nura/.env"
if [ -f "$ENV_FILE" ]; then
  while IFS='=' read -r k v; do
    case "$k" in
      GRANOLA_*) export "$k=${v//\"/}" ;;
    esac
  done < <(grep -E '^GRANOLA_' "$ENV_FILE" || true)
fi
exec python3 /opt/data/mcp-installs/granola/server.py
