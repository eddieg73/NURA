#!/bin/bash
# FIX the compose: move gw-relay under services, remove the networks garbage
COMPOSE=/docker/nura-nuratech-mapping/docker-compose.yml
echo "=== before ==="
grep -n "gw-relay\|^services:\|^networks:" $COMPOSE | head -8
python3 - <<'EOF'
import re
p = "/docker/nura-nuratech-mapping/docker-compose.yml"
s = open(p).read()
# remove the bad top-level/networks append
s = re.sub(r"\n  gw-relay:.*?depends_on:\n      - hermes-gateway\n", "\n", s, flags=re.S)
# remove the blank trailing
s = s.rstrip() + "\n"
# build the proper block
block = "\n  gw-relay:\n    image: alpine/socat:latest\n    network_mode: \"service:hermes-gateway\"\n    command: [\"TCP-LISTEN:18642,fork,reuseaddr\", \"TCP:127.0.0.1:8642\"]\n    restart: unless-stopped\n"
# insert after the services: line
s = re.sub(r"(^services:\n)", r"\1" + block, s, count=1, flags=re.M)
open(p, "w").write(s)
print("compose rewritten")
EOF
echo "=== after ==="
grep -n "gw-relay\|^services:\|^networks:" $COMPOSE | head -8
cd /docker/nura-nuratech-mapping
docker compose config --services 2>&1 | head -6
echo "=== up the relay ==="
docker compose up -d gw-relay 2>&1 | tail -1
sleep 10
docker ps --format '{{.Names}} {{.Status}}' | grep gw-relay | head -1
echo "=== relay listen check ==="
docker exec hermes-gateway sh -c "grep -i ':48E2' /proc/net/tcp | awk '{print \$2}' | head -2" 2>/dev/null || echo "no 18642 yet"
echo "=== NPM direct ==="
curl -s -m 8 -o /dev/null -w '%{http_code}\n' -H 'Host: api.nuratech.ai' http://127.0.0.1:8080/health 2>&1 | head -1
