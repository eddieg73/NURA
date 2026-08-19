#!/bin/bash
# Root access + sshd hygiene check across the fleet
for N in "72.61.71.211:clinic" "72.60.163.140:lab" "195.35.32.113:edge"; do
  IP="${N%%:*}"; HN="${N##*:}"
  echo "-- $HN ($IP) --"
  ssh -o BatchMode=yes -o ConnectTimeout=8 -i ~/.ssh/id_nura_clean root@$IP "whoami 2>/dev/null; grep -E '^PermitRootLogin|^PasswordAuthentication' /etc/ssh/sshd_config 2>/dev/null | head -2; grep -cE '^ssh-rsa|^ssh-ed25519' /root/.ssh/authorized_keys 2>/dev/null" 2>&1 | head -4
done
