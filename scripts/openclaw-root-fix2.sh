#!/bin/bash
# OpenClaw root fix v2 — stop the loop, fix, restart, verify
echo "=== stop (break the loop) ==="
docker stop openclaw 2>&1 | head -1
sleep 3
echo "=== inspect the config + .bak ==="
docker exec openclaw sh -c 'ls -la /home/node/.openclaw/ | grep -E "openclaw.json|\.bak" | tail -4' 2>&1 | head -5
echo "=== config head ==="
docker exec openclaw sh -c 'head -c 400 /home/node/.openclaw/openclaw.json 2>/dev/null; echo' 2>&1 | head -4
echo "=== json validity (python) ==="
docker exec openclaw sh -c 'python3 -c "import json; json.load(open(\"/home/node/.openclaw/openclaw.json\")); print(\"VALID\")" 2>/dev/null || node -e "JSON.parse(require(\"fs\").readFileSync(\"/home/node/.openclaw/openclaw.json\")); console.log(\"VALID\")" 2>/dev/null || echo INVALID' 2>&1 | head -2
