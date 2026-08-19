#!/bin/sh
# medisun-redis export (read-only) — dump keys with TTLs to JSONL
set -e
PASS=$(printenv REDIS_PASSWORD 2>/dev/null || true)
[ -z "$PASS" ] && PASS=$(grep -oP 'requirepass \K.*' /usr/local/etc/redis/redis.conf 2>/dev/null || true)
echo "pass_found=${#PASS}"
KEYS=$(redis-cli -a "$PASS" --no-auth-warning --scan 2>/dev/null | head -200)
echo "key_count=$(echo "$KEYS" | grep -c . || true)"
echo "--- sample ---"
echo "$KEYS" | head -8
OUT=/tmp/medisun-redis-export.jsonl
: > "$OUT"
echo "$KEYS" | while IFS= read -r k; do
  [ -z "$k" ] && continue
  ttl=$(redis-cli -a "$PASS" --no-auth-warning TTL "$k" 2>/dev/null)
  payload=$(redis-cli -a "$PASS" --no-auth-warning DUMP "$k" 2>/dev/null | base64 | tr -d '\n')
  kjson=$(python3 -c "import json,sys;print(json.dumps(sys.argv[1]))" "$k")
  pjson=$(python3 -c "import json,sys;print(json.dumps(sys.argv[1]))" "$payload")
  printf '{"key":%s,"ttl":%s,"dump":%s}\n' "$kjson" "$ttl" "$pjson" >> "$OUT"
done
echo "exported_lines=$(wc -l < "$OUT")"
