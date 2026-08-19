#!/usr/bin/env bash
# OpenEMR MCP lane wrapper — reads OPENEMR_* from profile .env at runtime (never in config).
set -euo pipefail
ENV_FILE="/opt/data/profiles/nura/.env"
if [ -f "$ENV_FILE" ]; then
  while IFS='=' read -r k v; do
    case "$k" in
      OPENEMR_*) export "$k=${v//\"/}" ;;
    esac
  done < <(grep -E '^OPENEMR_' "$ENV_FILE" || true)
fi
exec /opt/data/mcp-installs/openemr/.venv/bin/openemr-mcp
