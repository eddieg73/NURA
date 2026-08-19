#!/bin/bash
# Prism32 deploy runner — sandboxed, sealed key (never echoed)
set -euo pipefail
export PRISM32_HOME=/opt/data/profiles/nura/home/.prism32
export PYTHONPATH=/opt/data/profiles/nura/python-packages
mkdir -p "$PRISM32_HOME" /tmp/prism32-sandbox

KEY=$(grep -E "^OPENROUTER_API_KEY=" /opt/data/profiles/nura/.env | head -1 | cut -d= -f2- | tr -d '"' | tr -d "'")
MODEL="deepseek/deepseek-chat"
API="https://openrouter.ai/api/v1"

echo "== Prism32 version =="
python3 -m prism32 --version 2>/dev/null || python3 /opt/data/profiles/nura/python-packages/prism32.py --version

echo "== Harness scan (detecting AI CLIs on this box) =="
cd /tmp/prism32-sandbox
timeout 120 python3 -m prism32 --api "$API" --model "$MODEL" --api-key "$KEY" --harness-scan --no-boot 2>&1 | grep -vE "^\s*$" | head -25 || echo "(harness scan exited via timeout — see output)"
