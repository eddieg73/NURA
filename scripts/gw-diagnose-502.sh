#!/bin/bash
# THE 502 CHAIN DIAGNOSTIC — every hop, one shot
echo "=== 1. the container bind (00000000:21C2 = good, 0100007F = loopback) ==="
docker exec hermes-gateway sh -c "grep -i ':21C2' /proc/net/tcp | awk '{print \$2}' | head -2" 2>/dev/null || echo "no 21C2 listener"
echo "=== 2. the container env (key present?) ==="
docker inspect hermes-gateway --format '{{range .Config.Env}}{{println .}}{{end}}' | grep -cE '^API_SERVER_KEY='
echo "=== 3. the host relay (systemd) ==="
systemctl is-active gw-relay 2>/dev/null
ss -tln | grep 18642 | head -1
echo "=== 4. the relay -> docker-proxy probe ==="
curl -s -m 6 -o /dev/null -w 'relay:8642 path -> %{http_code}\n' http://127.0.0.1:18642/health
curl -s -m 6 -o /dev/null -w 'proxy:8642 path -> %{http_code}\n' http://127.0.0.1:8642/health
echo "=== 5. the NPM forward (the DB truth) ==="
docker exec nginx-proxy-manager-db-1 sh -c "MYSQL_PWD=\$MYSQL_ROOT_PASSWORD mysql -uroot npm -e 'SELECT id, forward_host, forward_port, enabled FROM proxy_host WHERE id=5'" 2>&1 | head -3
echo "=== 6. the NPM direct ==="
curl -s -m 8 -o /dev/null -w 'NPM: %{http_code}\n' -H 'Host: api.nuratech.ai' http://127.0.0.1:8080/health
curl -s -m 8 -H 'Host: api.nuratech.ai' http://127.0.0.1:8080/health 2>&1 | head -c 100; echo
echo "=== 7. the public ==="
curl -s -m 8 -o /dev/null -w 'public: %{http_code}\n' http://api.nuratech.ai/health
