#!/bin/bash
# REMOTE GATEWAY — CORRECTED: one-shot container patch + full recreate + verify
echo "=== 1. patch the api_server bind inside the container (single exec) ==="
docker exec hermes-gateway sh -c '
  for CFG in /home/node/.hermes/profiles/nura/config.yaml /home/node/.hermes/config.yaml; do
    [ -f "$CFG" ] && echo "using: $CFG" && break
  done
  if grep -q "api_server:" "$CFG" 2>/dev/null; then
    python3 -c "
import re
p = \"$CFG\"
s = open(p).read()
if re.search(r\"api_server:\\s*\\n\\s*host:\", s):
    s = re.sub(r\"(api_server:\\s*\\n\\s*host:).*\", r\"\\1 0.0.0.0\", s)
else:
    s = re.sub(r\"(api_server:\\s*\\n)\", r\"\\1  host: 0.0.0.0\\n\", s)
open(p, \"w\").write(s)
print(\"patched\")
"
  else
    printf "\napi_server:\n  host: 0.0.0.0\n" >> "$CFG"
    echo "appended to $CFG"
  fi
  grep -A2 "api_server:" "$CFG" | head -4
'
echo "=== 2. controlled full recreate ==="
cd /docker/nura-nuratech-mapping
docker compose up -d --force-recreate 2>&1 | tail -2
sleep 20
echo "=== 3. verify the bind (00000000:21C2 = 0.0.0.0:8642 = SUCCESS) ==="
docker exec hermes-gateway sh -c "grep -i ':21C2' /proc/net/tcp | awk '{print \$2}' | head -2"
echo "=== 4. the public chain ==="
curl -s -m 8 -o /dev/null -w "http://api.nuratech.ai -> %{http_code}\n" http://api.nuratech.ai 2>&1 | head -1
curl -s -m 8 http://api.nuratech.ai/health 2>&1 | head -c 90; echo
