#!/usr/bin/env bash
set -euo pipefail

/opt/hermes/.venv/bin/python - <<'PY'
from pathlib import Path
import json
import sys

try:
    import yaml
except Exception as exc:
    print(f"sync-default-json: missing PyYAML: {exc}", file=sys.stderr)
    raise SystemExit(1)

source = Path('/opt/data/profile.yaml')
dest = Path('/opt/data/default.json')

if not source.is_file():
    raise SystemExit(0)

with source.open('r', encoding='utf-8') as f:
    yaml_data = yaml.safe_load(f) or {}
if not isinstance(yaml_data, dict):
    yaml_data = {}

payload = {
    'description': str(yaml_data.get('description') or '').strip(),
    'description_auto': bool(yaml_data.get('description_auto', False)),
}

current = None
if dest.is_file():
    try:
        with dest.open('r', encoding='utf-8') as f:
            current = json.load(f)
    except Exception:
        current = None

if current == payload:
    raise SystemExit(0)

tmp = dest.with_suffix('.json.tmp')
with tmp.open('w', encoding='utf-8') as f:
    json.dump(payload, f, indent=2, ensure_ascii=False)
    f.write('\n')
tmp.replace(dest)
print('synced default.json')
PY
