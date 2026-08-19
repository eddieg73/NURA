#!/usr/bin/env bash
set -euo pipefail

# Notion MCP wrapper: extracts token from ntn auth.json
AUTH_FILE="${HOME}/.config/notion/auth.json"

if [[ ! -f "$AUTH_FILE" ]]; then
  echo "ERROR: Notion auth not found at $AUTH_FILE — run 'ntn login' first" >&2
  exit 1
fi

# Extract the first workspace token
TOKEN=$(python3 -c "
import json, sys
with open('$AUTH_FILE') as f:
    data = json.load(f)
if not data:
    sys.exit(1)
# Get first workspace's token
token = list(data.values())[0]
print(token)
" 2>/dev/null)

if [[ -z "${TOKEN:-}" ]]; then
  echo "ERROR: Could not extract Notion token from $AUTH_FILE" >&2
  exit 2
fi

export NOTION_API_TOKEN="$TOKEN"

# Use the hosted Notion MCP endpoint
exec npx -y @notionhq/notion-mcp-server "$@"
