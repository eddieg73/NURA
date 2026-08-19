#!/bin/bash
# Tailscale status check — the 3 nodes + the local
for N in "72.61.71.211:clinic" "72.60.163.140:lab" "195.35.32.113:edge"; do
  IP="${N%%:*}"; HN="${N##*:}"
  echo "-- $HN --"
  ssh -o BatchMode=yes -o ConnectTimeout=8 -i ~/.ssh/id_nura_clean root@$IP "tailscale status 2>&1 | head -3" 2>&1 | head -3
done
echo "=== local ==="
/opt/data/bin/tailscale --socket=/tmp/tailscaled.sock status 2>&1 | head -3
