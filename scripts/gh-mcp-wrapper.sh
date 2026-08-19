#!/bin/bash
# GitHub MCP wrapper — the sealed token from the profile .env, the npx stdio server
export GITHUB_PERSONAL_ACCESS_TOKEN="$(grep '^GITHUB_FINE_GRAIN_TOKEN=' /opt/data/profiles/nura/.env | cut -d= -f2)"
export PATH="/opt/data/profiles/nura/bin:/opt/data/profiles/nura/.local/bin:/opt/hermes/bin:/opt/hermes/.venv/bin:$PATH"
exec npx -y @modelcontextprotocol/server-github 2>/dev/null
