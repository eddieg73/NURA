#!/bin/bash
# THE COMPLETE REMOTE-GATEWAY FIX — socat sidecar (same netns) + NPM port + verify
set -e
COMPOSE=/docker/nura-nuratech-mapping/docker-compose.yml
cd /docker/nura-nuratech-mapping
echo "=== 1. add the socat sidecar ==="
if ! grep -q "gw-relay" $COMPOSE; then
cat >> $COMPOSE <<'EOF'

  gw-relay:
    image: alpine/socat:latest
    network_mode: "service:hermes-gateway"
    command: ["TCP-LISTEN:18642,fork,reuseaddr", "TCP:127.0.0.1:8642"]
    restart: unless-stopped
    depends_on:
      - hermes-gateway
EOF
echo "sidecar added"
else
echo "sidecar present"
fi
docker compose up -d gw-relay 2>&1 | tail -1
sleep 8
echo "=== 2. verify the relay listen ==="
docker exec hermes-gateway sh -c "grep -i ':48E2' /proc/net/tcp | awk '{print \$2}' | head -2"
echo "=== 3. NPM forward -> hermes-gateway:18642 ==="
docker exec nginx-proxy-manager-db-1 sh -c "MYSQL_PWD=\$MYSQL_ROOT_PASSWORD mysql -uroot npm -e \"UPDATE proxy_host SET forward_host='hermes-gateway', forward_port=18642 WHERE id=5; SELECT id, forward_host, forward_port FROM proxy_host WHERE id=5;\"" 2>&1 | head -4
docker restart nginx-proxy-manager-app-1 >/dev/null 2>&1
sleep 12
docker exec nginx-proxy-manager-app-1 nginx -s reload 2>&1 | head -1
sleep 2
echo "=== 4. NPM direct (127.0.0.1:8080 + Host) ==="
curl -s -m 8 -o /dev/null -w '%{http_code}\n' -H 'Host: api.nuratech.ai' http://127.0.0.1:8080/health 2>&1 | head -1
curl -s -m 8 -H 'Host: api.nuratech.ai' http://127.0.0.1:8080/health 2>&1 | head -c 120; echo
