#!/bin/bash
# HOST-RELAY: systemd socat (host 127.0.0.1:8642 -> the docker-proxy) + NPM -> host:18642
set -e
echo "=== 1. systemd socat unit ==="
cat > /etc/systemd/system/gw-relay.service <<'EOF'
[Unit]
Description=NURA gateway relay (18642 -> 127.0.0.1:8642)
After=docker.service
[Service]
ExecStart=/usr/bin/socat TCP-LISTEN:18642,fork,reuseaddr TCP:127.0.0.1:8642
Restart=always
RestartSec=5
[Install]
WantedBy=multi-user.target
EOF
systemctl daemon-reload
systemctl enable gw-relay 2>&1 | tail -1
systemctl restart gw-relay
sleep 2
systemctl is-active gw-relay
ss -tln | grep 18642 | head -1
echo "=== 2. NPM forward -> 72.61.71.211:18642 ==="
docker exec nginx-proxy-manager-db-1 sh -c "MYSQL_PWD=\$MYSQL_ROOT_PASSWORD mysql -uroot npm -e \"UPDATE proxy_host SET forward_host='72.61.71.211', forward_port=18642 WHERE id=5; SELECT id, forward_host, forward_port FROM proxy_host WHERE id=5;\"" 2>&1 | head -3
docker restart nginx-proxy-manager-app-1 >/dev/null 2>&1
sleep 12
docker exec nginx-proxy-manager-app-1 nginx -s reload 2>&1 | head -1
sleep 2
echo "=== 3. NPM direct + host relay probe ==="
curl -s -m 8 -o /dev/null -w 'NPM-direct: %{http_code}\n' -H 'Host: api.nuratech.ai' http://127.0.0.1:8080/health
curl -s -m 8 -o /dev/null -w 'relay-direct: %{http_code}\n' http://127.0.0.1:18642/health
curl -s -m 8 http://127.0.0.1:18642/health 2>&1 | head -c 120; echo
