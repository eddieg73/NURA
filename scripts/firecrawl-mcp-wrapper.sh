#!/bin/bash
# Firecrawl MCP wrapper — the sealed FIRECRAWL_API_KEY from the profile .env (never in config!)
ENV_FILE="/opt/data/profiles/nura/.env"
[ -f "$ENV_FILE" ] && while IFS='=' read -r k v; do
  case "$k" in
    FIRECRAWL_*) export "$k=${v//\"/}" ;;
  esac
done < <(grep -E '^FIRECRAWL_' "$ENV_FILE" || true)
export PATH="/opt/data/profiles/nura/bin:/opt/data/profiles/nura/.local/bin:/opt/hermes/bin:/opt/hermes/.venv/bin:$PATH"
exec npx -y firecrawl-mcp 2>/dev/null
