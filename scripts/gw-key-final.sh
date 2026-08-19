#!/bin/bash
# THE FINAL PIECE — API_SERVER_KEY into the gateway env + config + restart + verify
set -e
KEY=$(cat /tmp/hermes-api-key.txt 2>/dev/null || echo "")
if [ -z "$KEY" ]; then echo "NO KEY PROVIDED"; exit 1; fi
echo "key length: ${#KEY}"
COMPOSE=/docker/nura-nuratech-mapping/docker-compose.yml
echo "=== 1. compose env ==="
if ! grep -q "API_SERVER_KEY" $COMPOSE; then
  sed -i 's|      HERMES_GATEWAY_HOST: 0.0.0.0|      HERMES_GATEWAY_HOST: 0.0.0.0\n      API_SERVER_KEY: '"$KEY"'|' $COMPOSE
  echo "key added to the compose env"
else
  echo "key already in the compose"
fi
grep -n "API_SERVER_KEY" $COMPOSE | sed 's/\(API_SERVER_KEY: ....\).*/\1****/' | head -2
echo "=== 2. config extra.key ==="
docker exec hermes-gateway sh -c "python3 - <<EOF
import re
p = '/home/node/.hermes/config.yaml'
s = open(p).read()
if 'key:' in s:
    s = re.sub(r'(key:).*', r'\1 $KEY', s)
else:
    s = re.sub(r'(host: 0.0.0.0)', r'\1\n    key: $KEY', s)
open(p, 'w').write(s)
print('config key set')
EOF"
echo "=== 3. recreate the gateway ==="
cd /docker/nura-nuratech-mapping
docker compose up -d --force-recreate 2>&1 | tail -1
sleep 20
echo "=== 4. the bind (00000000:21C2 = success) ==="
docker exec hermes-gateway sh -c "grep -i ':21C2' /proc/net/tcp | awk '{print \$2}' | head -2"
echo "=== 5. the chain ==="
curl -s -m 8 -o /dev/null -w 'NPM: %{http_code}\n' -H 'Host: api.nuratech.ai' http://127.0.0.1:8080/health
curl -s -m 8 -H 'Host: api.nuratech.ai' http://127.0.0.1:8080/health 2>&1 | head -c 100; echo
