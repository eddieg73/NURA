#!/bin/bash
# medisun-redis export — password from REDIS_PASSWORD.txt (host side, never echoed)
set -e
PASS=$(cat /opt/medisun-redis/REDIS_PASSWORD.txt)
echo "pass_len=${#PASS}"
echo "dbsize=$(docker exec medisun-redis redis-cli -a "$PASS" --no-auth-warning DBSIZE 2>/dev/null | head -1)"
echo "--- keys sample ---"
docker exec medisun-redis redis-cli -a "$PASS" --no-auth-warning --scan 2>/dev/null | head -10
docker exec medisun-redis sh -c 'printf "%s" "$0" > /tmp/rp' "$PASS"
docker exec medisun-redis sh /tmp/export2.sh 2>&1 | tail -2
docker cp medisun-redis:/tmp/medisun-redis-export.jsonl /tmp/medisun-redis-export.jsonl >/dev/null 2>&1
echo "host_lines=$(wc -l < /tmp/medisun-redis-export.jsonl 2>/dev/null || echo 0)"
