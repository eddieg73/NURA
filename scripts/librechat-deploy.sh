#!/bin/bash
# LIBRECHAT-DEPLOY — the Lab-deploy: the compose + the sovereign-lane wiring!
# The pattern: the tar-over-SSH (the proven remote-deploy!) — the compose from its dir!
set -e
LAB=root@72.60.163.140
KEY=~/.ssh/id_nura_clean
SRC=/opt/data/hermes-ecosystem/LibreChat

echo "=== 1. THE PACK ==="
cd $SRC && tar czf /tmp/librechat-pack.tgz --exclude=.git . 2>/dev/null
ls -la /tmp/librechat-pack.tgz | awk '{print $5/1048576 " MB"}'

echo "=== 2. THE TRANSFER ==="
scp -o BatchMode=yes -i $KEY /tmp/librechat-pack.tgz $LAB:/opt/librechat-pack.tgz 2>&1 | tail -1
ssh -o BatchMode=yes -i $KEY $LAB "mkdir -p /docker/librechat && tar xzf /opt/librechat-pack.tgz -C /docker/librechat 2>/dev/null; ls /docker/librechat/docker-compose.yml 2>/dev/null || ls /docker/librechat/deploy-compose.yml 2>/dev/null" 2>&1 | head -2

echo "=== 3. THE COMPOSE-ENV (the sovereign-lane!) ==="
ssh -o BatchMode=yes -i $KEY $LAB "cd /docker/librechat && (grep -q ENDPOINTS /docker/librechat/.env 2>/dev/null || cp .env.example .env 2>/dev/null || true); grep -cE 'ENDPOINTS|OPENAI_REVERSE_PROXY' .env 2>/dev/null || echo 'env-needs-config'" 2>&1 | head -2

echo "=== 4. THE UP ==="
ssh -o BatchMode=yes -i $KEY $LAB "cd /docker/librechat && docker compose up -d 2>&1 | tail -3" 2>&1 | head -4
echo "=== DEPLOY-DONE ==="
