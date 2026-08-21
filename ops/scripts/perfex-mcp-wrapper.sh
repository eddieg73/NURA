#!/bin/bash
# Perfex CRM MCP — FlexMCP HTTP endpoint
# Requires: PERFEX_CRM_URL, PERFEX_FMP_API_KEY in environment
set -euo pipefail

# Load env if not already set
[ -f "/opt/data/profiles/nura/.env" ] && set -a && source "/opt/data/profiles/nura/.env" && set +a

if [ -z "${{PERFEX_CRM_URL:-}}" ] || [ -z "${{PERFEX_FMP_API_KEY:-}}" ]; then
  echo '{{"error":"PERFEX_CRM_URL and PERFEX_FMP_API_KEY required"}}' >&2
  exit 1
fi

exec npx -y @anthropic/mcp-server-http   --url "${{PERFEX_CRM_URL}}"   --header "Authorization: Bearer ${{PERFEX_FMP_API_KEY}}"
