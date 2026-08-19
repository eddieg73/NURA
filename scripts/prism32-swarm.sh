#!/bin/bash
# PRISM32 SWARM — parallel goal workers, one per free-direct lane (2026-08-02)
# Each lane writes its slice into its own sandbox subdir; aggregate + verify.
set -uo pipefail
export PYTHONPATH=/opt/data/profiles/nura/python-packages
export PRISM32_HOME=/opt/data/profiles/nura/home/.prism32
ENV=/opt/data/profiles/nura/.env
ROOT=/tmp/prism32-swarm
mkdir -p "$ROOT"

gkey() { grep -E "^$1=" "$ENV" | head -1 | cut -d= -f2- | tr -d '"' | tr -d "'"; }

declare -A LANES
LANES[deepseek]="https://api.deepseek.com|deepseek-chat|$(gkey DEEPSEEK_API_KEY)"
LANES[hf]="https://router.huggingface.co/v1|meta-llama/Llama-3.3-70B-Instruct-Turbo|$(gkey HF_TOKEN)"

echo "Lanes: ${!LANES[@]}"
PIDS=()
for lane in "${!LANES[@]}"; do
  IFS='|' read -r API MODEL KEY <<< "${LANES[$lane]}"
  [ -z "$KEY" ] && { echo "SKIP $lane (no key)"; continue; }
  (
    mkdir -p "$ROOT/$lane" && cd "$ROOT/$lane"
    timeout 200 python3 -m prism32 --api "$API" --model "$MODEL" --api-key "$KEY" --no-boot \
      --goal "Working directory is the current dir. Create a file named slice.txt containing exactly the text SWARM-$lane. Verify with cat, then stop. Do not touch anything outside this directory." \
      >/dev/null 2>&1
    echo "worker $lane exit=$?" >> "$ROOT/workers.log"
  ) &
  PIDS+=($!)
  echo "spawned $lane (pid $!)"
done

for p in "${PIDS[@]}"; do wait "$p"; done

echo "== SWARM RESULTS =="
for lane in "${!LANES[@]}"; do
  if [ -f "$ROOT/$lane/slice.txt" ]; then
    echo "✅ $lane: $(cat "$ROOT/$lane/slice.txt")"
  else
    echo "❌ $lane: no slice produced"
  fi
done
echo "workers: $(cat "$ROOT/workers.log" 2>/dev/null | tr '\n' ' ')"
