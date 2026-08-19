#!/bin/bash
# Probe free direct LLM lanes (keys sealed from .env, never echoed)
set -uo pipefail
ENV=/opt/data/profiles/nura/.env
gkey() { grep -E "^$1=" "$ENV" | head -1 | cut -d= -f2- | tr -d '"' | tr -d "'"; }

echo "== 1) Gemini (AI Studio OpenAI-compatible) =="
GK=$(gkey GOOGLE_API_KEY)
curl -s -m 20 https://generativelanguage.googleapis.com/v1beta/openai/chat/completions \
  -H "Authorization: Bearer $GK" -H "Content-Type: application/json" \
  -d '{"model":"gemini-2.0-flash","messages":[{"role":"user","content":"reply with exactly: LANE_OK"}],"max_tokens":10}' \
  | head -c 300; echo

echo "== 2) NVIDIA NIM (free tier) =="
NK=$(gkey NVIDIA_API_KEY)
curl -s -m 20 https://integrate.api.nvidia.com/v1/chat/completions \
  -H "Authorization: Bearer $NK" -H "Content-Type: application/json" \
  -d '{"model":"meta/llama-3.3-70b-instruct","messages":[{"role":"user","content":"reply with exactly: LANE_OK"}],"max_tokens":10}' \
  | head -c 300; echo

echo "== 3) HuggingFace Inference (router, OpenAI-compatible) =="
HK=$(gkey HF_TOKEN)
curl -s -m 20 https://router.huggingface.co/v1/chat/completions \
  -H "Authorization: Bearer $HK" -H "Content-Type: application/json" \
  -d '{"model":"meta-llama/Llama-3.3-70B-Instruct","messages":[{"role":"user","content":"reply with exactly: LANE_OK"}],"max_tokens":10}' \
  | head -c 300; echo
