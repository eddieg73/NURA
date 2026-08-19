#!/bin/bash
# NPM PUT-trigger — the schema-correct PUT regenerates the 5.conf
TOKEN=$(curl -s -m 8 -X POST http://127.0.0.1:8181/api/tokens -H 'Content-Type: application/json' -d "{\"identity\":\"hermes@nuratech.ai\",\"secret\":\"NPM-rdSjrIjJDZ6rNEgxyM6jzS4F\"}" | python3 -c 'import sys,json;print(json.load(sys.stdin).get("token",""))')
echo "token: ${TOKEN:+ok}"
H=$(curl -s -m 8 http://127.0.0.1:8181/api/nginx/proxy-hosts/5 -H "Authorization: Bearer $TOKEN")
echo "GET: $(echo "$H" | head -c 120)"
NEW=$(echo "$H" | python3 -c 'import sys,json
d=json.load(sys.stdin)
d["forward_host"]="72.61.71.211"
d["forward_port"]=8642
print(json.dumps(d))')
echo "=== PUT ==="
curl -s -m 10 -X PUT http://127.0.0.1:8181/api/nginx/proxy-hosts/5 -H "Authorization: Bearer $TOKEN" -H 'Content-Type: application/json' -d "$NEW" -o /tmp/put-resp.json -w "PUT -> %{http_code}\n"
head -c 200 /tmp/put-resp.json; echo
sleep 6
echo "=== conf generation ==="
docker exec nginx-proxy-manager-app-1 sh -c 'ls /data/nginx/proxy_host/ | head -8; grep -n "proxy_pass" /data/nginx/proxy_host/5.conf 2>/dev/null | head -2 || echo "5.conf still missing"'
echo "=== public chain ==="
curl -s -m 8 -o /dev/null -w "http://api.nuratech.ai -> %{http_code}\n" http://api.nuratech.ai
curl -s -m 8 http://api.nuratech.ai/health 2>&1 | head -c 120
echo
