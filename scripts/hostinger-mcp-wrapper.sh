#!/usr/bin/env bash
# Hostinger MCP lane wrapper — reads HOSTINGER_API_TOKEN from profile .env at runtime (never in config).
# Usage: hostinger-mcp-wrapper.sh <binary-name>  (e.g. hostinger-dns-mcp)
set -euo pipefail
ENV_FILE="/opt/data/profiles/nura/.env"
BIN="${1:?usage: hostinger-mcp-wrapper.sh <binary>}"
if [ -f "$ENV_FILE" ]; then
  export HOSTINGER_API_TOKEN="$(grep -E '^HOSTINGER_API_TOKEN=' "$ENV_FILE" | head -1 | cut -d= -f2- | tr -d '"'"'"'')"
fi
if [ -z "${HOSTINGER_API_TOKEN:-}" ]; then
  echo "HOSTINGER_API_TOKEN missing from $ENV_FILE" >&2
  exit 1
fi
exec npx --package=hostinger-api-mcp@latest "$BIN"
