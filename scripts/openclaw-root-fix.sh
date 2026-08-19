#!/bin/bash
# OpenClaw root fix — doctor, fallback to .bak, restart, verify
set -x
echo "=== doctor --fix ==="
docker exec openclaw openclaw doctor --fix 2>&1 | tail -8
echo "=== try gateway start (foreground, 12s) ==="
timeout 12 docker exec openclaw openclaw gateway start 2>&1 | tail -6
echo "=== if still failing, check .bak ==="
docker exec openclaw sh -c 'ls -la /home/node/.openclaw/*.bak 2>/dev/null | tail -3; ls -la /home/node/.openclaw/openclaw.json 2>/dev/null' 2>&1 | head -6
