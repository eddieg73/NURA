#!/usr/bin/env bash
set -euo pipefail

unset PYTHONPATH PYTHONHOME

# Prefer an already-injected secret. Otherwise read only the expected key from
# the active Hermes secret file, then fall back to the official ElevenLabs CLI
# credential file. Never source .env files as shell code.
if [[ -z "${ELEVENLABS_API_KEY:-}" ]]; then
  for env_file in "${HERMES_HOME:-/opt/data}/.env" "/opt/data/.env"; do
    if [[ -r "$env_file" ]]; then
      candidate="$(python3 - "$env_file" <<'PY'
from pathlib import Path
import sys
p = Path(sys.argv[1])
for raw in p.read_text(errors="replace").splitlines():
    line = raw.strip()
    if not line or line.startswith("#") or "=" not in line:
        continue
    key, value = line.split("=", 1)
    if key.strip() == "ELEVENLABS_API_KEY":
        value = value.strip()
        if len(value) >= 2 and value[0] == value[-1] and value[0] in "\"'":
            value = value[1:-1]
        print(value, end="")
        break
PY
)"
      if [[ -n "$candidate" ]]; then
        export ELEVENLABS_API_KEY="$candidate"
        unset candidate
        break
      fi
    fi
  done
fi

if [[ -z "${ELEVENLABS_API_KEY:-}" && -r "$HOME/.elevenlabs/api_key" ]]; then
  IFS= read -r ELEVENLABS_API_KEY < "$HOME/.elevenlabs/api_key" || true
  export ELEVENLABS_API_KEY
fi

if [[ -z "${ELEVENLABS_API_KEY:-}" ]]; then
  echo "ElevenLabs MCP blocked: authenticate with 'elevenlabs auth login' or set ELEVENLABS_API_KEY in the active Hermes secret file." >&2
  exit 78
fi

export ELEVENLABS_MCP_BASE_PATH="${ELEVENLABS_MCP_BASE_PATH:-/opt/data/home/elevenlabs-output}"
export ELEVENLABS_MCP_OUTPUT_MODE="${ELEVENLABS_MCP_OUTPUT_MODE:-files}"

exec /opt/data/mcp-installs/elevenlabs/.venv/bin/elevenlabs-mcp "$@"
