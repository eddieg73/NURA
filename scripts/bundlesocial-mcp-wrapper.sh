#!/usr/bin/env bash
# bundle.social MCP lane wrapper — reads BUNDLESOCIAL_* from profile .env at runtime (never in config).
set -euo pipefail
ENV_FILE="/opt/data/profiles/nura/.env"
if [ -f "$ENV_FILE" ]; then
  while IFS='=' read -r k v; do
    case "$k" in
      BUNDLESOCIAL_*) export "$k=${v//\"/}" ;;
    esac
  done < <(grep -E '^BUNDLESOCIAL_' "$ENV_FILE" || true)
fi
exec npx --yes bundlesocial-mcp
