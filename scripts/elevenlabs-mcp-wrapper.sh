#!/bin/bash
# ElevenLabs MCP wrapper — exports the sealed key to the child process ONLY (0700)
KEY=$(grep -E "^ELEVENLABS_API_KEY=" /opt/data/profiles/nura/.env | head -1 | cut -d= -f2- | tr -d '"' | tr -d "'")
if [ -z "$KEY" ]; then echo "NO ELEVENLABS_API_KEY" >&2; exit 1; fi
export ELEVENLABS_API_KEY="$KEY"
exec npx -y @mindstone/mcp-server-elevenlabs "$@"
