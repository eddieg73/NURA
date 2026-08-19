#!/usr/bin/env bash
# Firebase MCP lane wrapper — reads FIREBASE_* from profile .env at runtime (never in config).
set -euo pipefail
ENV_FILE="/opt/data/profiles/nura/.env"
if [ -f "$ENV_FILE" ]; then
  while IFS='=' read -r k v; do
    case "$k" in
      FIREBASE_*) export "$k=${v//\"/}" ;;
    esac
  done < <(grep -E '^FIREBASE_' "$ENV_FILE" || true)
fi
exec python3 /opt/data/mcp-installs/firebase/server.py
