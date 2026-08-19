#!/usr/bin/env bash
# OpenEvidence MCP lane wrapper — reads OPENEVIDENCE_* from profile .env at runtime (never in config).
set -euo pipefail
ENV_FILE="/opt/data/profiles/nura/.env"
if [ -f "$ENV_FILE" ]; then
  while IFS='=' read -r k v; do
    case "$k" in
      OPENEVIDENCE_*) export "$k=${v//\"/}" ;;
    esac
  done < <(grep -E '^OPENEVIDENCE_' "$ENV_FILE" || true)
fi
exec python3 /opt/data/mcp-installs/openevidence/server.py
