#!/usr/bin/env bash
set -euo pipefail

unset PYTHONHOME
export PYTHONPATH=""

/opt/data/scripts/redis_server_manager.py ensure --quiet

exec /opt/data/mcp-installs/redis/.venv/bin/redis-mcp-server --url redis://127.0.0.1:6379/0 "$@"
