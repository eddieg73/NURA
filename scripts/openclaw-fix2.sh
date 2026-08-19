#!/bin/bash
# OpenClaw fix v2 — wire the .env into the compose + recreate + verify
set -e
cd /docker/openclaw
if ! grep -q "env_file" docker-compose.yml; then
  sed -i '/OPENCLAW_WORKSPACE_DIR/a\    env_file:\n      - .env' docker-compose.yml
  echo "env_file added"
fi
docker compose up -d --force-recreate 2>&1 | tail -2
sleep 20
echo "=== container state ==="
docker ps --format '{{.Names}} {{.Status}}' | grep -i openclaw | head -1
echo "=== env inside ==="
docker inspect openclaw --format '{{range .Config.Env}}{{println .}}{{end}}' 2>/dev/null | grep -c GATEWAY_TOKEN | head -1
echo "=== gateway probe ==="
TOK=$(grep -E '^OPENCLAW_GATEWAY_TOKEN=' .env | cut -d= -f2-)
curl -s -m 8 -o /dev/null -w "gateway 18789 (no auth) -> %{http_code}\n" http://127.0.0.1:18789/ 2>&1 | head -1
curl -s -m 8 -o /dev/null -w "gateway 18789 (with token) -> %{http_code}\n" -H "Authorization: Bearer $TOK" http://127.0.0.1:18789/ 2>&1 | head -1
