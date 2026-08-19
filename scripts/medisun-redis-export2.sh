#!/bin/bash
# medisun-redis export — host-side orchestrator (password from compose .env, never echoed)
set -e
PASS=$(grep -E '^REDIS_PASSWORD=' /opt/medisun-redis/.env | cut -d= -f2-)
echo "pass_len=${#PASS}"
echo "dbsize=$(docker exec medisun-redis redis-cli -a "$PASS" --no-auth-warning DBSIZE 2>/dev/null | head -1)"
echo "--- keys sample ---"
docker exec medisun-redis redis-cli -a "$PASS" --no-auth-warning --scan 2>/dev/null | head -10
docker exec medisun-redis sh -c 'echo "$0" > /tmp/rp' "$PASS"
docker exec medisun-redis sh /tmp/export2.sh 2>/dev/null | tail -2 || echo "export script missing"
