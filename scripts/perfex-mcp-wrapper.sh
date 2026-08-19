#!/usr/bin/env bash
set -euo pipefail
umask 077

# Perfex CRM MCP wrapper: uses PERFEX_BASE_URL and PERFEX_API_TOKEN from env
# Secrets must be supplied by Hermes' active secret scope / environment.

install_dir="/opt/data/mcp-installs/perfex"
venv_python="$install_dir/.venv/bin/python"
server="$install_dir/server.py"

if [[ ! -f "$server" ]]; then
  echo "ERROR: Perfex MCP server not found at $server" >&2
  exit 127
fi

if [[ -z "${PERFEX_BASE_URL:-}" ]]; then
  PERFEX_BASE_URL="https://195.35.32.113/api"
fi

if [[ -z "${PERFEX_API_TOKEN:-}" ]]; then
  echo "ERROR: PERFEX_API_TOKEN is required for Perfex MCP" >&2
  exit 2
fi

exec "$venv_python" "$server"
