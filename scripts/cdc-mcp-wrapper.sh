#!/usr/bin/env bash
# CDC MCP lane wrapper (no creds needed — public Socrata API).
set -euo pipefail
exec python3 /opt/data/mcp-installs/cdc/server.py
