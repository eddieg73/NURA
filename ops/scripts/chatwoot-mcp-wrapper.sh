#!/usr/bin/env bash
set -euo pipefail
umask 077

# Chatwoot MCP wrapper: isolates dotenv loading from the main Hermes home.
# Required secrets must be supplied by Hermes' active secret scope / environment:
#   CHATWOOT_BASE_URL, CHATWOOT_API_TOKEN, optional CHATWOOT_ACCOUNT_ID
install_dir="/opt/data/mcp-installs/chatwoot"
bin="$install_dir/node_modules/.bin/chatwoot-mcp-server"

if [[ ! -x "$bin" ]]; then
  echo "chatwoot-mcp-server is not installed at $bin" >&2
  exit 127
fi
if [[ -z "${CHATWOOT_BASE_URL:-}" || -z "${CHATWOOT_API_TOKEN:-}" ]]; then
  echo "CHATWOOT_BASE_URL and CHATWOOT_API_TOKEN are required for Chatwoot MCP" >&2
  exit 2
fi

cd "$install_dir"
exec env -i \
  PATH="/usr/local/bin:/usr/bin:/bin" \
  HOME="/opt/data" \
  CHATWOOT_BASE_URL="$CHATWOOT_BASE_URL" \
  CHATWOOT_API_TOKEN="$CHATWOOT_API_TOKEN" \
  CHATWOOT_ACCOUNT_ID="${CHATWOOT_ACCOUNT_ID:-}" \
  "$bin"
