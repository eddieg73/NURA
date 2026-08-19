#!/bin/bash
# Prism32 goal proof — DeepSeek direct lane (fallback when OpenRouter is dry)
set -euo pipefail
export PRISM32_HOME=/opt/data/profiles/nura/home/.prism32
export PYTHONPATH=/opt/data/profiles/nura/python-packages
cd /tmp/prism32-sandbox
rm -f hello.txt

KEY=$(grep -E "^DEEPSEEK_API_KEY=" /opt/data/profiles/nura/.env | head -1 | cut -d= -f2- | tr -d '"' | tr -d "'")
if [ -z "$KEY" ]; then
  echo "No DEEPSEEK_API_KEY in .env — checking OPENROUTER free lane"
  KEY=$(grep -E "^OPENROUTER_API_KEY=" /opt/data/profiles/nura/.env | head -1 | cut -d= -f2- | tr -d '"' | tr -d "'")
  API="https://openrouter.ai/api/v1"; MODEL="google/gemini-2.0-flash-exp:free"
else
  API="https://api.deepseek.com"; MODEL="deepseek-chat"
fi
echo "Lane: $MODEL"

timeout 200 python3 -m prism32 --api "$API" --model "$MODEL" --api-key "$KEY" --no-boot \
  --goal "Working directory is the current dir. Create a file named hello.txt containing the text NURA-PRISM32-DEPLOYED. Then print the byte size of that file. Do not touch anything outside this directory." 2>&1 | tail -18

echo "== Verification =="
ls -la /tmp/prism32-sandbox/hello.txt 2>/dev/null && cat /tmp/prism32-sandbox/hello.txt || echo "FILE NOT CREATED"
