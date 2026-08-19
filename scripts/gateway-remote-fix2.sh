#!/bin/bash
# REMOTE GATEWAY v2 — add API_SERVER_HOST=0.0.0.0 to the gateway service env + recreate + verify
COMPOSE=/docker/nura-nuratech-mapping/docker-compose.yml
cd /docker/nura-nuratech-mapping
echo "=== services ==="
docker compose config --services 2>/dev/null | head -5
echo "=== patch the env ==="
if ! grep -q "API_SERVER_HOST" $COMPOSE; then
  sed -i 's/      HERMES_GATEWAY_HOST: 0.0.0.0/      HERMES_GATEWAY_HOST: 0.0.0.0\n      API_SERVER_HOST: 0.0.0.0/' $COMPOSE
  echo "added API_SERVER_HOST=0.0.0.0"
else
  sed -i 's/API_SERVER_HOST: 127.0.0.1/API_SERVER_HOST: 0.0.0.0/g' $COMPOSE
  echo "updated existing"
fi
grep -n "API_SERVER_HOST" $COMPOSE | head -2
echo "=== recreate the main service ==="
docker compose up -d --force-recreate 2>&1 | tail -2
sleep 15
echo "=== verify ==="
docker ps --format '{{.Names}} {{.Status}}' | grep hermes-gateway | head -1
curl -s -m 6 http://127.0.0.1:8642/health 2>&1 | head -c 80; echo
curl -s -m 8 -o /dev/null -w "http://api.nuratech.ai -> %{http_code}\n" http://api.nuratech.ai 2>&1 | head -1
