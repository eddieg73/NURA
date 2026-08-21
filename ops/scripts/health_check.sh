#!/bin/bash
# E2E health audit (17:00 daily) — silent when everything's healthy.
# Prints FAIL lines only.
SERVICES="127.0.0.1:8787 127.0.0.1:8092 127.0.0.1:8095 127.0.0.1:5000 127.0.0.1:11434 127.0.0.1:8642"
for s in $SERVICES; do
  code=$(curl -s -m 5 -o /dev/null -w '%{http_code}' "http://$s/health" 2>/dev/null)
  [ "$code" != "200" ] && echo "FAIL: $s/health -> $code"
done
# the fleet
for h in 72.61.71.211 72.60.163.140 195.35.32.113; do
  ssh -o BatchMode=yes -o ConnectTimeout=8 -i /opt/data/profiles/nura/home/.ssh/id_nura_clean root@$h 'uptime -p' >/dev/null 2>&1 \
    || echo "FAIL: fleet node $h unreachable"
done
exit 0
