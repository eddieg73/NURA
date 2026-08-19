#!/bin/bash
set -uo pipefail
ENV=/opt/data/profiles/nura/.env
NK=$(grep -E "^NVIDIA_API_KEY=" "$ENV" | head -1 | cut -d= -f2- | tr -d '"' | tr -d "'")
echo "== NVIDIA NIM retest =="
curl -s -m 30 -w "\nHTTP:%{http_code}\n" https://integrate.api.nvidia.com/v1/chat/completions \
  -H "Authorization: Bearer $NK" -H "Content-Type: application/json" \
  -d '{"model":"meta/llama-3.3-70b-instruct","messages":[{"role":"user","content":"reply with exactly: LANE_OK"}],"max_tokens":10}' | tail -c 400
