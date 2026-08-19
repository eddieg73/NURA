#!/bin/bash
# SPOTLESS CLEANUP — the dead weight removal (data preserved, reversible)
echo "=== CLINIC: remove the stopped kaqe container (data preserved at /docker/paperclip-kaqe/data) ==="
ssh -o BatchMode=yes -o ConnectTimeout=10 -i ~/.ssh/id_nura_clean root@72.61.71.211 "
  docker rm paperclip-kaqe-paperclip-1 2>&1 | head -1
  echo 'stopped after: ' \$(docker ps -aq --filter status=exited | wc -l)
  echo 'dangling images before: ' \$(docker images -f dangling=true -q | wc -l)
  docker image prune -f 2>&1 | tail -1
  journalctl --vacuum-time=3d 2>/dev/null | tail -1
  df -h / | awk 'NR==2{print \"DISK now: \"\$3\" used of \"\$2\" (\"\$5\")\"}'
" 2>&1 | head -8
echo "=== LAB: stopped containers ==="
ssh -o BatchMode=yes -o ConnectTimeout=10 -i ~/.ssh/id_nura_clean root@72.60.163.140 "
  docker ps -a --format '{{.Names}} {{.Status}}' | grep -i exited | head -4
  docker image prune -f 2>&1 | tail -1
" 2>&1 | head -6
echo "=== EDGE: stopped containers ==="
ssh -o BatchMode=yes -o ConnectTimeout=10 -i ~/.ssh/id_nura_clean root@195.35.32.113 "
  docker ps -a --format '{{.Names}} {{.Status}}' | grep -i exited | head -5
  docker image prune -f 2>&1 | tail -1
" 2>&1 | head -7
echo "=== local /tmp cleanup ==="
rm -f /tmp/mkeys.txt /tmp/kaqe-latest.sql.gz /tmp/mm*.json /tmp/login*.json /tmp/c*.json /tmp/g*.json /tmp/m.json /tmp/o.json /tmp/ds-probe.json /tmp/pv.json /tmp/edgar.json /tmp/n8n-create*.json /tmp/n8n-wf.json 2>/dev/null
echo "tmp cleaned"
