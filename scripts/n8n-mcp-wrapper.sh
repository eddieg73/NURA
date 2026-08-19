#!/bin/bash
# n8n official MCP transport wrapper — reads token from env at runtime (never embedded).
set -e
ENVF=/opt/data/home/.config/n8n-mcp/env
TOKEN=$(grep -oP '(?<=N8N_API_KEY=).*' "$ENVF" | tr -d '\r\n')
if [ -z "$TOKEN" ]; then
  echo "N8N_API_KEY missing in $ENVF" >&2
  exit 1
fi
exec npx -y supergateway --streamableHttp "https://n8n.nuratech.ai/mcp-server/http" --header "authorization:Bearer $TOKEN"
