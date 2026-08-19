#!/bin/bash
# Redis migration v3 — SSH tunnel (detached), MIGRATE all keys, verify, close tunnel
set -e
MPASS=$(cat /opt/medisun-redis/REDIS_PASSWORD.txt)
CPASS=$(ssh -o BatchMode=yes -i /root/.ssh/id_nura_clean root@72.61.71.211 "grep -E '^REDIS_PASSWORD=' /docker/redis-gc8b/.env | cut -d= -f2-")
echo "creds ok (src=${#MPASS} dst=${#CPASS})"
# detached tunnel Lab -> Clinic redis
ssh -o BatchMode=yes -o StrictHostKeyChecking=accept-new -i /root/.ssh/id_nura_clean -f -N -L 0.0.0.0:32772:127.0.0.1:32772 root@72.61.71.211
sleep 3
# the container's 127.0.0.1 = ITSELF — target the HOST (docker bridge gateway) where the tunnel listens
GW=$(docker exec medisun-redis sh -c 'ip route 2>/dev/null | awk "/default/ {print \$3}"' 2>/dev/null | head -1)
[ -z "$GW" ] && GW=172.17.0.1
echo "bridge_gateway=$GW"
docker exec medisun-redis redis-cli -a "$MPASS" --no-auth-warning --scan 2>/dev/null > /tmp/mkeys.txt
echo "keys=$(wc -l < /tmp/mkeys.txt)"
FAIL=0; OK=0
while IFS= read -r k; do
  [ -z "$k" ] && continue
  R=$(docker exec medisun-redis redis-cli -a "$MPASS" --no-auth-warning MIGRATE "$GW" 32772 "" 0 8000 AUTH "$CPASS" KEYS "$k" 2>&1)
  case "$R" in
    OK) OK=$((OK+1));;
    *BUSYKEY*) OK=$((OK+1));;
    *) echo "fail[$k]: $R"; FAIL=$((FAIL+1));;
  esac
done < /tmp/mkeys.txt
echo "migrated=$OK failures=$FAIL"
pkill -f "L 32772" 2>/dev/null || true
echo "dst_dbsize=$(ssh -o BatchMode=yes -i /root/.ssh/id_nura_clean root@72.61.71.211 "docker exec redis-gc8b-redis-1 redis-cli -a \"$CPASS\" --no-auth-warning DBSIZE 2>/dev/null | head -1")"
echo "src_dbsize=$(docker exec medisun-redis redis-cli -a "$MPASS" --no-auth-warning DBSIZE 2>/dev/null | head -1)"
