#!/usr/bin/env bash
set -euo pipefail

if [[ ! -s "$HOME/.elevenlabs/api_key" ]] && ! grep -Eq '^[[:space:]]*ELEVENLABS_API_KEY[[:space:]]*=[[:space:]]*[^[:space:]#]+' "${HERMES_HOME:-/opt/data}/.env" 2>/dev/null; then
  echo "ElevenLabs activation blocked: run 'elevenlabs auth login' in this terminal first." >&2
  exit 78
fi

if [[ -s "$HOME/.elevenlabs/api_key" ]]; then
  chmod 0600 "$HOME/.elevenlabs/api_key"
  chmod 0700 "$HOME/.elevenlabs"
fi

hermes config set --force mcp_servers.elevenlabs.enabled true

if ! hermes mcp test elevenlabs; then
  hermes config set --force mcp_servers.elevenlabs.enabled false
  echo "ElevenLabs MCP test failed; connector returned to disabled state." >&2
  exit 1
fi

echo "ElevenLabs MCP transport and tool discovery verified. Start a fresh Hermes session to load its tools."
