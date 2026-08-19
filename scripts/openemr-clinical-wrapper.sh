#!/usr/bin/env bash
# openemr-clinical MCP lane wrapper — reads OPENEMR_* from profile .env at runtime.
set -euo pipefail
ENV_FILE="/opt/data/profiles/nura/.env"
if [ -f "$ENV_FILE" ]; then
  while IFS='=' read -r k v; do
    case "$k" in
      OPENEMR_*) export "$k=${v//\"/}" ;;
    esac
  done < <(grep -E '^OPENEMR_' "$ENV_FILE" || true)
fi
exec python3 /opt/data/mcp-installs/openemr-clinical/server.py
