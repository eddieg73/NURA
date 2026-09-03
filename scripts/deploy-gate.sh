#!/bin/bash
# NURA deploy gate — refuses to promote a lane that is NOT in the AI product registry.
# Best-practice rule 10 (every AI lane registered) enforced mechanically.
# Usage: deploy-gate.sh <lane-key>
#   lane-key examples: "mem0", "nura-docs", "deepseek-v4-flash-0731",
#                      "gpt-5.4-mini", "med42", "nomic-embed-text", "<any new lane>"
# Exit 0 = gate OPEN (lane registered) · Exit 1 = gate CLOSED (lane NOT registered)
set -uo pipefail

REG="/opt/data/nura_medical/docs/AI-Product-Registry.md"
LANE="${1:-}"
if [ -z "$LANE" ]; then
  echo "GATE: no lane-key given. Usage: deploy-gate.sh <lane-key>"; exit 2
fi
if [ ! -f "$REG" ]; then
  echo "GATE: registry not found at $REG — BLOCKING (no registry = no deploy)."; exit 1
fi

# Is the lane present in the registry? (match the token anywhere in the file)
if grep -qiE "[_\`]*${LANE}[_\`]*" "$REG"; then
  echo "GATE OPEN: '${LANE}' is registered in the AI product registry."
  exit 0
else
  echo "GATE CLOSED: '${LANE}' is NOT in the AI product registry ($REG)."
  echo "  → Register it first (docs/AI-Product-Registry.md) or the deploy is refused."
  exit 1
fi
