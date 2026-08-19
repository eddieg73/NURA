#!/bin/bash
# RunPod official MCP transport — reads key from .env at runtime (never embedded in config).
set -e
KEY=$(grep -oP '(?<=^RUNPOD_API_KEY=).*' /opt/data/profiles/nura/.env | head -1 | tr -d '\r\n' | tr -d "'\"")
if [ -z "$KEY" ]; then
  echo "RUNPOD_API_KEY missing in /opt/data/profiles/nura/.env" >&2
  exit 1
fi
export RUNPOD_API_KEY="$KEY"
exec npx -y @runpod/mcp-server@latest "$@"
