#!/bin/bash
# OpenClaw root fix v3 — host-side config repair (the volume /docker/openclaw/data)
set -x
echo "=== config files ==="
ls -la /docker/openclaw/data/ | grep -E "openclaw.json|\.bak" | tail -4
echo "=== json validity ==="
python3 -c "import json; json.load(open('/docker/openclaw/data/openclaw.json')); print('VALID')" 2>&1 | tail -1
echo "=== .bak validity ==="
for f in /docker/openclaw/data/openclaw.json.bak*; do [ -f "$f" ] && python3 -c "import json,sys; json.load(open('$f')); print('VALID $f')" 2>/dev/null; done
echo "=== doctor --fix via one-shot container ==="
docker run --rm -v /docker/openclaw/data:/home/node/.openclaw ghcr.io/openclaw/openclaw:latest openclaw doctor --fix 2>&1 | tail -6
echo "=== post-doctor validity ==="
python3 -c "import json; json.load(open('/docker/openclaw/data/openclaw.json')); print('VALID')" 2>&1 | tail -1
