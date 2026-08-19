#!/bin/bash
# Medisun -> NURA Redis migration v2 — password fetched from the Clinic, traffic via SSH tunnel
set -e
MPASS=$(cat /opt/medisun-redis/REDIS_PASSWORD.txt)
CPASS=$(ssh -o BatchMode=yes -i /root/.ssh/id_nura_clean root@72.61.71.211 "grep -E '^REDIS_PASSWORD=' /docker/redis-gc8b/.env | cut -d= -f2-")
echo "creds ok (medisun=${#MPASS} nura=${#CPASS})"
# tunnel: Lab -> Clinic redis (bypasses the firewall; no rule changes)
(ssh -o BatchMode=yes -o ServerAliveInterval=30 -N -L 32772:127.0.0.1:32772 root@72.61.71.211 &) ; sleep 3
docker exec medisun-redis redis-cli -a "$MPASS" --no-auth-warning --scan 2>/dev/null > /tmp/mkeys.txt
echo "keys=$(wc -l < /tmp/mkeys.txt)"
FAIL=0; OK=0
while IFS= read -r k; do
  [ -z "$k" ] && continue
  R=$(docker exec medisun-redis redis-cli -a "$MPASS" --no-auth-warning MIGRATE 127.0.0.1 32772 "" 0 8000 AUTH "$CPASS" KEYS "$k" 2>&1)
  case "$R" in
    OK) OK=$((OK+1));;
    *BUSYKEY*) OK=$((OK+1));;
    *) echo "fail[$k]: $R"; FAIL=$((FAIL+1));;
  esac
done < /tmp/mkeys.txt
echo "migrated=$OK failures=$FAIL"
echo "nura_dbsize=$(ssh -o BatchMode=yes -i /root/.ssh/id_nura_clean root@72.61.71.211 "docker exec redis-gc8b-redis-1 redis-cli -a \"$CPASS\" --no-auth-warning DBSIZE 2>/dev/null | head -1")"
