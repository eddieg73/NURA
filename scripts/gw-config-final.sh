#!/bin/bash
# THE CORRECT CONFIG FIX — api_server.extra.host + key check + restart + verify
echo "=== container API env ==="
docker inspect hermes-gateway --format '{{range .Config.Env}}{{println .}}{{end}}' | grep -E 'API_SERVER_(KEY|ENABLED)' | sed 's/\(KEY=\).\{4\}.*/\1****/' | head -3
echo "=== current config api_server ==="
docker exec hermes-gateway sh -c 'grep -n -A4 "api_server" /home/node/.hermes/config.yaml 2>/dev/null | head -8'
echo "=== rewrite with the correct schema ==="
docker exec hermes-gateway sh -c 'python3 - <<EOF
import re, os
p = "/home/node/.hermes/config.yaml"
s = open(p).read()
key = os.environ.get("API_SERVER_KEY", "")
# strip any existing api_server section
s = re.sub(r"api_server:.*?(?=\n\w)", "", s, flags=re.S)
block = "api_server:\n  enabled: true\n  extra:\n    host: 0.0.0.0\n    port: 8642\n"
if key:
    block += f"    key: {key}\n"
s = s.rstrip() + "\n\n" + block
open(p, "w").write(s)
print("rewritten")
EOF'
docker exec hermes-gateway sh -c 'grep -n -A5 "api_server" /home/node/.hermes/config.yaml | head -8'
echo "=== restart the gateway ==="
docker restart hermes-gateway 2>&1 | head -1
sleep 18
echo "=== the bind (must be 00000000:21C2) ==="
docker exec hermes-gateway sh -c "grep -i ':21C2' /proc/net/tcp | awk '{print \$2}' | head -2"
echo "=== NPM direct ==="
curl -s -m 8 -o /dev/null -w 'NPM-direct: %{http_code}\n' -H 'Host: api.nuratech.ai' http://127.0.0.1:8080/health
curl -s -m 8 -H 'Host: api.nuratech.ai' http://127.0.0.1:8080/health 2>&1 | head -c 100; echo
