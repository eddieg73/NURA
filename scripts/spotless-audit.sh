#!/bin/bash
# SPOTLESS ASSESSMENT — the founder's one-command audit (run from Hermes box or any node with the key)
# Usage: bash spotless-audit.sh [clinic|lab|edge|all]
NODES="CLINIC:72.61.71.211 LAB:72.60.163.140 EDGE:195.35.32.113"
[ "$1" = "clinic" ] && NODES="CLINIC:72.61.71.211"
[ "$1" = "lab" ] && NODES="LAB:72.60.163.140"
[ "$1" = "edge" ] && NODES="EDGE:195.35.32.113"
for H in $NODES; do
  NAME=${H%%:*}; IP=${H##*:}
  echo "══════════════════════════════════════════"
  echo " $NAME ($IP)"
  echo "══════════════════════════════════════════"
  ssh -o BatchMode=yes -o ConnectTimeout=8 -i ~/.ssh/id_nura_clean root@$IP "
    echo '── ROOT/SSH ──'
    echo \"key-auth: \$(grep -c '^ssh-ed25519' /root/.ssh/authorized_keys 2>/dev/null || echo 0) key(s) · root shell: \$(grep -c root /etc/passwd)\"
    echo '── RESOURCES ──'
    free -m | awk '/Mem/{print \"RAM: \"\$2\"MB total \"\$3\"MB used (\"\$5\" free)\"} /Swap/{print \"SWAP: \"\$2\"MB total \"\$3\"MB used\"}'
    df -h / | awk 'NR==2{print \"DISK: \"\$3\" used of \"\$2\" (\"\$5\" full)\"}'
    echo \"LOAD: \$(cat /proc/loadavg | cut -d' ' -f1-3)\"
    echo '── DOCKER STATE ──'
    echo \"running: \$(docker ps -q | wc -l) · stopped: \$(docker ps -aq --filter status=exited | wc -l) · images: \$(docker images -q | wc -l)\"
    echo '── RANDOM PORTS (the messy pattern) ──'
    docker ps --format '{{.Names}} {{.Ports}}' | grep -E '327[0-9]{2}|588[0-9]{2}' | head -6 || echo 'none'
    echo '── LISTENING PORTS (host) ──'
    ss -tln | awk 'NR>1{print \$4}' | grep -oE ':[0-9]+$' | sort -u | tr '\n' ' ' | head -c 300; echo
    echo '── FIREWALL ──'
    (iptables -L INPUT -n 2>/dev/null | head -3 | tail -1) || echo 'n/a'
    echo '── UPTIME ──'
    uptime -p
  " 2>&1 | head -30
done
echo "══════════════════════════════════════════"
echo " DONE — every node assessed. Any node failing key-auth or showing random ports needs cleanup."
