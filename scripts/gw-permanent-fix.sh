#!/bin/bash
# THE PERMANENT FIX — bind-mounted config with extra.host=0.0.0.0 + recreate + full verify
set -e
COMPOSE=/docker/nura-nuratech-mapping/docker-compose.yml
DIR=/docker/nura-nuratech-mapping
KEY=$(cat /tmp/hermes-api-key.txt 2>/dev/null || echo "")
[ -z "$KEY" ] && { echo "NO KEY"; exit 1; }
echo "=== 1. the persistent config file ==="
cat > $DIR/config.yaml <<EOF
api_server:
  enabled: true
  extra:
    host: 0.0.0.0
    port: 8642
    key: $KEY
EOF
echo "config written:"
head -6 $DIR/config.yaml | sed "s/key: .*/key: ****/"
echo "=== 2. the compose volume mount ==="
if ! grep -q "config.yaml:/home/node/.hermes/config.yaml" $COMPOSE; then
  python3 - <<'EOF'
import re
p = "/docker/nura-nuratech-mapping/docker-compose.yml"
s = open(p).read()
# find the gateway service block and add a volumes line after its environment
if "volumes:" not in s.split("  dashboard:")[0]:
    # insert volumes into the gateway service (the first service block after 'services:')
    s = s.replace("    container_name: hermes-gateway", "    container_name: hermes-gateway\n    volumes:\n      - ./config.yaml:/home/node/.hermes/config.yaml:ro", 1)
    open(p, "w").write(s)
    print("volume mount added")
else:
    print("volume already present")
EOF
fi
grep -n "config.yaml" $COMPOSE | head -3
echo "=== 3. recreate the gateway ==="
cd $DIR
docker compose up -d --force-recreate 2>&1 | tail -1
sleep 22
echo "=== 4. the bind (00000000:21C2 = SUCCESS) ==="
docker exec hermes-gateway sh -c "grep -i ':21C2' /proc/net/tcp | awk '{print \$2}' | head -2"
echo "=== 5. the chain ==="
curl -s -m 8 -o /dev/null -w 'proxy:8642 -> %{http_code}\n' http://127.0.0.1:8642/health
curl -s -m 8 -o /dev/null -w 'relay:18642 -> %{http_code}\n' http://127.0.0.1:18642/health
curl -s -m 8 -o /dev/null -w 'NPM-direct: %{http_code}\n' -H 'Host: api.nuratech.ai' http://127.0.0.1:8080/health
curl -s -m 8 -H 'Host: api.nuratech.ai' http://127.0.0.1:8080/health 2>&1 | head -c 100; echo
