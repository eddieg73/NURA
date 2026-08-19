#!/bin/bash
# WIREGUARD-MESH-BUILDER — the self-built VPN between the 3 servers (no account, no clicks!)
# Subnet: 10.10.0.0/24 — Clinic=10.10.0.1 · Lab=10.10.0.2 · Edge=10.10.0.3
set -e
NODES="72.61.71.211:10.10.0.1 72.60.163.140:10.10.0.2 195.35.32.113:10.10.0.3"
KEYFILE=/tmp/wg-mesh-keys.txt
: > $KEYFILE

echo "=== 1. INSTALL + KEYGEN ON ALL 3 ==="
for N in $NODES; do
  IP="${N%%:*}"; WG="${N##*:}"
  OUT=$(ssh -o BatchMode=yes -o ConnectTimeout=10 -i ~/.ssh/id_nura_clean root@$IP "
    apt-get install -y wireguard >/dev/null 2>&1 || yum install -y wireguard-tools >/dev/null 2>&1 || true
    wg genkey | tee /etc/wireguard/private.key | wg pubkey > /etc/wireguard/public.key
    chmod 600 /etc/wireguard/private.key
    echo 'PRIV:'\$(cat /etc/wireguard/private.key)' PUB:'\$(cat /etc/wireguard/public.key)
  " 2>&1 | grep -E 'PRIV:|PUB:')
  echo "$IP|$WG|$OUT" >> $KEYFILE
  echo "  $IP: keys-generated ✓"
done

echo "=== 2. THE CONFIGS (peer-map!) ==="
declare -A PUBS
while IFS='|' read -r IP WG KV; do
  PUB=$(echo "$KV" | sed -n 's/.*PUB:\([^ ]*\).*/\1/p')
  PUBS[$IP]="$PUB"
done < $KEYFILE

for N in $NODES; do
  IP="${N%%:*}"; MYWG="${N##*:}"
  CONF="/etc/wireguard/wg0.conf"
  { echo "[Interface]"; echo "Address = $MYWG/24"; echo "PrivateKey = $(ssh -o BatchMode=yes -o ConnectTimeout=8 -i ~/.ssh/id_nura_clean root@$IP 'cat /etc/wireguard/private.key')"; echo "ListenPort = 51820"; echo "SaveConfig = false"; echo "";
    for M in $NODES; do
      MIP="${M%%:*}"; MWG="${M##*:}"
      [ "$MIP" = "$IP" ] && continue
      echo "[Peer]"; echo "PublicKey = ${PUBS[$MIP]}"; echo "Endpoint = $MIP:51820"; echo "AllowedIPs = $MWG/32"; echo "PersistentKeepalive = 25"; echo "";
    done
  } | ssh -o BatchMode=yes -o ConnectTimeout=8 -i ~/.ssh/id_nura_clean root@$IP "cat > $CONF && echo 'config-written'"
  echo "  $IP: wg0.conf ✓"
done

echo "=== 3. THE SYSTEMD-ENABLE ==="
for N in $NODES; do
  IP="${N%%:*}"
  ssh -o BatchMode=yes -o ConnectTimeout=8 -i ~/.ssh/id_nura_clean root@$IP "systemctl enable wg-quick@wg0 >/dev/null 2>&1; systemctl restart wg-quick@wg0 2>&1 | head -1; sleep 2; wg show wg0 2>/dev/null | head -2 | tr '\n' ' '" > /tmp/wg-${IP}.txt 2>&1
  echo "  $IP: $(cat /tmp/wg-${IP}.txt | head -c 90)"
done
echo "=== MESH-BUILD-DONE ==="
