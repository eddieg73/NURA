#!/usr/bin/env bash
set -euo pipefail

secret_file="/opt/data/paperclip-runtime/mcp.env"
if [[ ! -r "$secret_file" ]]; then
  echo "Paperclip MCP secret file is unavailable" >&2
  exit 1
fi

/opt/data/scripts/paperclip_server_manager.py ensure --quiet

set -a
# shellcheck disable=SC1090
source "$secret_file"
set +a

exec npx --yes @paperclipai/mcp-server@2026.722.0 "$@"
