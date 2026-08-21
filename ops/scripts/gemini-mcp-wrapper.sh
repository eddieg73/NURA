#!/usr/bin/env bash
set -euo pipefail

# Parse candidate env files without sourcing them, so unrelated syntax in the
# secret store cannot break Gemini activation.
secret_candidates=(
  "/opt/data/home/.hermes/.env"
  "/opt/data/profiles/nura/workspace/full-profile-merge-20260730-082300/default-.env"
)

extract_key() {
  python3 - "$1" <<'PY'
from pathlib import Path
import sys
path = Path(sys.argv[1])
try:
    text = path.read_text(errors='replace')
except Exception:
    raise SystemExit(1)
for raw in text.splitlines():
    line = raw.strip()
    if not line or line.startswith('#') or '=' not in line:
        continue
    key, value = line.split('=', 1)
    key = key.strip()
    if key in ('GEMINI_API_KEY', 'GOOGLE_API_KEY'):
        value = value.strip()
        if (value.startswith('"') and value.endswith('"')) or (value.startswith("'") and value.endswith("'")):
            value = value[1:-1]
        print(value)
        raise SystemExit(0)
raise SystemExit(1)
PY
}

api_key=""
for secret_file in "${secret_candidates[@]}"; do
  if [[ -r "$secret_file" ]]; then
    if api_key="$(extract_key "$secret_file" 2>/dev/null)" && [[ -n "$api_key" ]]; then
      export GEMINI_API_KEY="$api_key"
      export GOOGLE_API_KEY="$api_key"
      break
    fi
  fi
done

if [[ -z "${GEMINI_API_KEY:-}" && -z "${GOOGLE_API_KEY:-}" ]]; then
  echo "Gemini API key is missing from all candidate secret files" >&2
  exit 1
fi

exec npx --yes @houtini/gemini-mcp "$@"
