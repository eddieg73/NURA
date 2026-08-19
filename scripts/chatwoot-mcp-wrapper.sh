#!/usr/bin/env bash
# Chatwoot MCP lane wrapper (@fazer-ai/mcp-chatwoot) — reads CHATWOOT_* from profile .env at runtime.
set -euo pipefail
ENV_FILE="/opt/data/profiles/nura/.env"
if [ -f "$ENV_FILE" ]; then
  while IFS='=' read -r k v; do
    case "$k" in
      CHATWOOT_*) export "$k=${v//\"/}" ;;
    esac
  done < <(grep -E '^CHATWOOT_' "$ENV_FILE" || true)
fi
exec npx --yes @fazer-ai/mcp-chatwoot
