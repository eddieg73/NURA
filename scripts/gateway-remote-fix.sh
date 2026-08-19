#!/bin/bash
# REMOTE GATEWAY — the A-path: bind the API to 0.0.0.0 + controlled recreate + verify
set -e
COMPOSE=/docker/nura-nuratech-mapping/docker-compose.yml
echo "=== current bind ==="
grep -n "API_SERVER_HOST" $COMPOSE | head -2
echo "=== config change: 127.0.0.1 -> 0.0.0.0 ==="
sed -i 's/API_SERVER_HOST=127.0.0.1/API_SERVER_HOST=0.0.0.0/g' $COMPOSE
grep -n "API_SERVER_HOST" $COMPOSE | head -2
echo "=== controlled recreate (the gateway container only) ==="
cd /docker/nura-nuratech-mapping
docker compose up -d --force-recreate hermes-gateway 2>&1 | tail -2
echo "=== wait + verify ==="
sleep 12
docker ps --format '{{.Names}} {{.Status}}' | grep hermes-gateway | head -1
curl -s -m 6 http://127.0.0.1:8642/health 2>&1 | head -c 80; echo
echo "=== the public chain ==="
curl -s -m 8 -o /dev/null -w "http://api.nuratech.ai -> %{http_code}\n" http://api.nuratech.ai 2>&1 | head -1
