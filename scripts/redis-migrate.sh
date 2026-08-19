#!/bin/bash
# Medisun -> NURA Redis migration (one memory doctrine). Passwords read host-side, never echoed.
set -e
MPASS=$(cat /opt/medisun-redis/REDIS_PASSWORD.txt)
CPASS=$(grep -E '^REDIS_PASSWORD=' /docker/redis-gc8b/.env | cut -d= -f2-)
echo "before: medisun=$(docker exec medisun-redis redis-cli -a "$MPASS" --no-auth-warning DBSIZE 2>/dev/null | head -1) nura=$(docker exec redis-gc8b-redis-1 redis-cli -a "$CPASS" --no-auth-warning DBSIZE 2>/dev/null | head -1)"
# Migrate ALL keys (the memory envelopes) to the NURA Redis on the Clinic
docker exec medisun-redis redis-cli -a "$MPASS" --no-auth-warning --scan 2>/dev/null > /tmp/mkeys.txt
echo "keys_to_migrate=$(wc -l < /tmp/mkeys.txt)"
docker cp /tmp/mkeys.txt medisun-redis:/tmp/mkeys.txt >/dev/null 2>&1
docker exec medisun-redis sh -c 'cat /tmp/mkeys.txt' >/dev/null 2>&1 || true
FAIL=0
while IFS= read -r k; do
  [ -z "$k" ] && continue
  R=$(docker exec medisun-redis redis-cli -a "$MPASS" --no-auth-warning MIGRATE 72.61.71.211 32772 "" 0 8000 AUTH "$CPASS" KEYS "$k" 2>&1)
  case "$R" in
    OK) ;;
    *NOSCRIPT*|*BUSYKEY*) ;;
    *) echo "fail[$k]: $R"; FAIL=$((FAIL+1));;
  esac
done < /tmp/mkeys.txt
echo "migrate_failures=$FAIL"
echo "after: medisun=$(docker exec medisun-redis redis-cli -a "$MPASS" --no-auth-warning DBSIZE 2>/dev/null | head -1) nura=$(docker exec redis-gc8b-redis-1 redis-cli -a "$CPASS" --no-auth-warning DBSIZE 2>/dev/null | head -1)"
