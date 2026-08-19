#!/bin/bash
# THE DEFINITIVE FIX — patch the PERSISTENT host config (extra.host + key) + recreate + verify
set -e
CFG=/root/.hermes/profiles/nura/config.yaml
KEY=$(cat /tmp/hermes-api-key.txt 2>/dev/null || echo "")
[ -z "$KEY" ] && { echo "NO KEY"; exit 1; }
echo "=== 1. before ==="
grep -n -A3 "api_server:" $CFG | head -6
echo "=== 2. patch extra.host + add the key ==="
python3 - <<EOF
import re
p = "$CFG"
s = open(p).read()
s = re.sub(r"(api_server:\s*\n\s*enabled: true\s*\n\s*extra:\s*\n\s*host:).*", r"\1 0.0.0.0", s)
if re.search(r"extra:\s*\n\s*host: 0.0.0.0\s*\n\s*port: 8642\s*\n\s*key:", s):
    s = re.sub(r"(extra:\s*\n\s*host: 0.0.0.0\s*\n\s*port: 8642\s*\n\s*key:).*", r"\1 $KEY", s)
else:
    s = re.sub(r"(extra:\s*\n\s*host: 0.0.0.0\s*\n\s*port: 8642)", r"\1\n      key: $KEY", s)
open(p, "w").write(s)
print("patched")
EOF
echo "=== 3. after ==="
grep -n -A5 "api_server:" $CFG | head -8 | sed "s/key: .*/key: ****/"
echo "=== 4. recreate the gateway ==="
cd /docker/nura-nuratech-mapping
docker compose up -d --force-recreate 2>&1 | tail -1
sleep 25
echo "=== 5. the bind (00000000:21C2 = SUCCESS) ==="
docker exec hermes-gateway sh -c "grep -i ':21C2' /proc/net/tcp | awk '{print \$2}' | head -2"
echo "=== 6. the full chain ==="
curl -s -m 8 -o /dev/null -w 'proxy:8642 -> %{http_code}\n' http://127.0.0.1:8642/health
curl -s -m 8 -o /dev/null -w 'relay:18642 -> %{http_code}\n' http://127.0.0.1:18642/health
curl -s -m 8 -o /dev/null -w 'NPM: %{http_code}\n' -H 'Host: api.nuratech.ai' http://127.0.0.1:8080/health
curl -s -m 8 -H 'Host: api.nuratech.ai' http://127.0.0.1:8080/health 2>&1 | head -c 120; echo
echo "=== 7. the public ==="
curl -s -m 8 -o /dev/null -w 'public: %{http_code}\n' http://api.nuratech.ai/health
