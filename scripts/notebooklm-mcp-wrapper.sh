#!/bin/bash
# NotebookLM MCP wrapper — the sealed-key + the Google-session (0600!)
ENV_FILE="/opt/data/profiles/nura/.env"
[ -f "$ENV_FILE" ] && while IFS='=' read -r k v; do
  case "$k" in
    NOTEBOOKLM_*) export "$k=${v//\"/}" ;;
  esac
done < <(grep -E '^NOTEBOOKLM_' "$ENV_FILE" || true)
export PATH="/opt/data/profiles/nura/bin:/opt/data/profiles/nura/.local/bin:/opt/hermes/bin:/opt/hermes/.venv/bin:$PATH"
exec npx -y notebooklm-mcp 2>/dev/null
