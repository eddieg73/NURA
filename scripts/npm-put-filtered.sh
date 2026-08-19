#!/bin/bash
# NPM PUT — the read-only fields stripped (the strict schema)
TOKEN=$(curl -s -m 8 -X POST http://127.0.0.1:8181/api/tokens -H 'Content-Type: application/json' -d "{\"identity\":\"hermes@nuratech.ai\",\"secret\":\"NPM-rdSjrIjJDZ6rNEgxyM6jzS4F\"}" | python3 -c 'import sys,json;print(json.load(sys.stdin).get("token",""))')
echo "token: ${TOKEN:+ok}"
H=$(curl -s -m 8 http://127.0.0.1:8181/api/nginx/proxy-hosts/5 -H "Authorization: Bearer $TOKEN")
NEW=$(echo "$H" | python3 -c 'import sys,json
d=json.load(sys.stdin)
for k in ("id","created_on","modified_on","owner_user_id"): d.pop(k,None)
d["forward_host"]="72.61.71.211"
d["forward_port"]=8642
print(json.dumps(d))')
echo "=== PUT (filtered) ==="
curl -s -m 10 -X PUT http://127.0.0.1:8181/api/nginx/proxy-hosts/5 -H "Authorization: Bearer $TOKEN" -H 'Content-Type: application/json' -d "$NEW" -o /tmp/put2.json -w "PUT -> %{http_code}\n"
head -c 150 /tmp/put2.json; echo
sleep 6
echo "=== conf proxy_pass ==="
docker exec nginx-proxy-manager-app-1 sh -c 'grep -n "proxy_pass" /data/nginx/proxy_host/5.conf 2>/dev/null | head -2 || echo missing'
echo "=== reload + public chain ==="
docker exec nginx-proxy-manager-app-1 nginx -s reload 2>&1 | head -1
sleep 3
curl -s -m 8 -o /dev/null -w "http://api.nuratech.ai -> %{http_code}\n" http://api.nuratech.ai
curl -s -m 8 http://api.nuratech.ai/health 2>&1 | head -c 120
echo
