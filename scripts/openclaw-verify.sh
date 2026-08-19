#!/bin/bash
# OpenClaw final verify
docker ps --format '{{.Names}} {{.Status}}' | grep -i openclaw | head -1
TOK=$(grep -E '^OPENCLAW_GATEWAY_TOKEN=' /docker/openclaw/.env | cut -d= -f2-)
curl -s -m 8 -o /dev/null -w "gateway with token -> HTTP %{http_code}\n" -H "Authorization: Bearer $TOK" http://127.0.0.1:18789/ 2>&1 | head -1
docker logs openclaw --tail 3 2>&1 | tail -3
