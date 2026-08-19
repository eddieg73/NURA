#!/bin/bash
# Gemini MCP wrapper — the sealed GEMINI_API_KEY (0600!)
ENV_FILE="/opt/data/profiles/nura/.env"
[ -f "$ENV_FILE" ] && while IFS='=' read -r k v; do
  case "$k" in
    GEMINI_API_KEY) export GEMINI_API_KEY="${v//\"/}" ;;
  esac
done < <(grep -E '^GEMINI_API_KEY=' "$ENV_FILE" || true)
export PATH="/opt/data/profiles/nura/bin:/opt/data/profiles/nura/.local/bin:/opt/hermes/bin:/opt/hermes/.venv/bin:$PATH"
exec npx -y gemini-mcp 2>/dev/null
