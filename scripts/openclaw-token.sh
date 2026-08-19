#!/bin/bash
# OpenClaw control — set the gateway token + recreate + verify
set -e
TOK=$(openssl rand -hex 32)
if ! grep -q "OPENCLAW_GATEWAY_TOKEN" /docker/openclaw/.env 2>/dev/null; then
  printf '\nOPENCLAW_GATEWAY_TOKEN=%s\n' "$TOK" >> /docker/openclaw/.env
else
  sed -i "s/^OPENCLAW_GATEWAY_TOKEN=.*/OPENCLAW_GATEWAY_TOKEN=$TOK/" /docker/openclaw/.env
fi
chmod 600 /docker/openclaw/.env
echo "token set (${#TOK} chars)"
cd /docker/openclaw && docker compose up -d 2>&1 | tail -2
sleep 15
docker ps --format '{{.Names}} {{.Status}}' | grep -i openclaw | head -1
docker logs openclaw --tail 3 2>&1 | tail -3
echo "=== token for the control lane ==="
echo "$TOK" > /tmp/openclaw-token.txt
