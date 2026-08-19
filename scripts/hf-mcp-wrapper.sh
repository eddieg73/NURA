#!/bin/bash
# HuggingFace MCP wrapper — the sealed HF_TOKEN (0600!)
ENV_FILE="/opt/data/profiles/nura/.env"
[ -f "$ENV_FILE" ] && while IFS='=' read -r k v; do
  case "$k" in
    HF_TOKEN) export HF_TOKEN="${v//\"/}" ;;
  esac
done < <(grep -E '^HF_TOKEN=' "$ENV_FILE" || true)
export PATH="/opt/data/profiles/nura/bin:/opt/data/profiles/nura/.local/bin:/opt/hermes/bin:/opt/hermes/.venv/bin:$PATH"
exec npx -y huggingface-mcp-server
