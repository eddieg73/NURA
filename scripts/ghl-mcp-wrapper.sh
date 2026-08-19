#!/bin/bash
# GHL MCP wrapper — sealed keys from the profile .env, then the server
set -a
[ -f /opt/data/profiles/nura/.env ] && source /opt/data/profiles/nura/.env
set +a
export GHL_API_KEY="${GHL_API_KEY:-}"
export GHL_LOCATION_ID="${GHL_LOCATION_ID:-}"
export GHL_BASE_URL="${GHL_BASE_URL:-https://rest.gohighlevel.com/v1/}"
exec node /opt/data/mcp-installs/ghl-mcp/dist/main.js "$@"
