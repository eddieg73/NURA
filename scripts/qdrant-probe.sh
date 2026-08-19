#!/bin/bash
# Qdrant host-side probe (Clinic)
Q=http://127.0.0.1:32769
COLS=$(curl -s -m 5 "$Q/collections" 2>/dev/null | python3 -c 'import sys,json; [print(x["name"]) for x in json.load(sys.stdin)["result"]["collections"]]' 2>/dev/null)
echo "collections:"
echo "$COLS" | head -8
echo "--- points ---"
for c in $COLS; do
  echo -n "$c: "
  curl -s -m 5 "$Q/collections/$c" 2>/dev/null | python3 -c 'import sys,json; print(json.load(sys.stdin)["result"]["points_count"])' 2>/dev/null
done
