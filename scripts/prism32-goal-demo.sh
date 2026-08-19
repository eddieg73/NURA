#!/bin/bash
# Prism32 goal-mode proof — sandboxed, bounded
set -euo pipefail
export PRISM32_HOME=/opt/data/profiles/nura/home/.prism32
export PYTHONPATH=/opt/data/profiles/nura/python-packages
cd /tmp/prism32-sandbox

KEY=$(grep -E "^OPENROUTER_API_KEY=" /opt/data/profiles/nura/.env | head -1 | cut -d= -f2- | tr -d '"' | tr -d "'")

echo "== Goal mode (bounded): create hello.txt in sandbox, report size =="
timeout 180 python3 -m prism32 --api "https://openrouter.ai/api/v1" --model "deepseek/deepseek-chat" \
  --api-key "$KEY" --no-boot \
  --goal "Working directory is the current dir. Create a file named hello.txt containing the text NURA-PRISM32-DEPLOYED. Then print the byte size of that file. Do not touch anything outside this directory." 2>&1 | tail -25

echo "== Verification =="
ls -la /tmp/prism32-sandbox/hello.txt 2>/dev/null && cat /tmp/prism32-sandbox/hello.txt
