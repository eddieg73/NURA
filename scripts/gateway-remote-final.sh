#!/bin/bash
# REMOTE GATEWAY — FINAL: patch the api_server bind + controlled recreate + full verify
set -e
CFG=$(docker exec hermes-gateway sh -c 'ls /home/node/.hermes/profiles/nura/config.yaml 2>/dev/null || echo /home/node/.hermes/config.yaml')
echo "=== patch api_server.host -> 0.0.0.0 ==="
docker exec hermes-gateway sh -c "
  if grep -q 'api_server' $CFG 2>/dev/null; then
    python3 - <<'EOF'
import re
p = '$CFG'
s = open(p).read()
if re.search(r'api_server:\s*\n\s*host:', s):
    s = re.sub(r'(api_server:\s*\n\s*host:).*', r'\1 0.0.0.0', s)
else:
    s = re.sub(r'(api_server:\s*\n)', r'\1  host: 0.0.0.0\n', s)
open(p, 'w').write(s)
print('patched')
EOF
  else
    printf '\napi_server:\n  host: 0.0.0.0\n' >> $CFG
    echo 'appended'
  fi
" 2>&1 | tail -1
docker exec hermes-gateway sh -c "grep -A2 'api_server' $CFG | head -4"
echo "=== recreate via compose (the controlled path) ==="
cd /docker/nura-nuratech-mapping
docker compose up -d --force-recreate hermes-gateway 2>&1 | tail -1 || docker compose up -d --force-recreate 2>&1 | tail -1
sleep 18
echo "=== verify the bind (must show 00000000:21C2 = 0.0.0.0:8642) ==="
docker exec hermes-gateway sh -c "cat /proc/net/tcp | awk 'NR>1{print \\\$2}' | grep -i ':21C2' | head -2"
echo "=== the public chain ==="
curl -s -m 8 -o /dev/null -w "http://api.nuratech.ai -> %{http_code}\n" http://api.nuratech.ai 2>&1 | head -1
curl -s -m 8 http://api.nuratech.ai/health 2>&1 | head -c 90; echo
