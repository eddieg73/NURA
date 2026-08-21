#!/usr/bin/env bash
# MSO Coder Workspace API — Phase 1 launcher
# Usage: ./run.sh [port]   (default 8643 — 8642 is the Hermes gateway)
set -euo pipefail
HERE="$(cd "$(dirname "$0")" && pwd)"
PORT="${1:-${MSO_CODER_PORT:-8643}}"
exec "$HERE/.venv/bin/python" -m uvicorn mso-coder-api:app \
  --app-dir "$HERE" --host 127.0.0.1 --port "$PORT"
