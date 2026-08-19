#!/bin/bash
# NPM HOST CREATE — api.nuratech.ai -> HOST-IP:8642 (the docker-proxy path) + verify
set -e
TOKEN=$(curl -s -m 8 -X POST http://127.0.0.1:8181/api/tokens -H 'Content-Type: application/json' \
  -d "{\"identity\":\"${NPM_ADMIN}\",\"secret\":\"${NPM_PASS}\"}" | python3 -c 'import sys,json;print(json.load(sys.stdin).get("token",""))')
[ -z "$TOKEN" ] && { echo "LOGIN FAILED"; exit 1; }
echo "=== existing hosts ==="
curl -s -m 8 http://127.0.0.1:8181/api/nginx/proxy-hosts -H "Authorization: Bearer $TOKEN" | \
  python3 -c 'import sys,json;[print(h["id"], h["domain"], h["forward_host"]+":"+str(h["forward_port"])) for h in json.load(sys.stdin)]' | head -15
echo "=== create api.nuratech.ai ==="
curl -s -m 8 -X POST http://127.0.0.1:8181/api/nginx/proxy-hosts \
  -H "Authorization: Bearer $TOKEN" -H 'Content-Type: application/json' \
  -d '{"domain_names":["api.nuratech.ai"],"forward_scheme":"http","forward_host":"72.61.71.211","forward_port":8642,"enabled":true,"block_exploits":false,"caching_enabled":false,"allow_websocket_upgrade":true,"access_list_id":0,"advanced_config":"","locations":[],"meta":{"letsencrypt_agree":false,"dns_challenge":false},"certificate_id":0,"ssl_forced":false}' \
  | python3 -c 'import sys,json;d=json.load(sys.stdin);print("created id:",d.get("id"),d.get("domain_names"))' 2>&1 | head -2
sleep 3
echo "=== the public chain ==="
curl -s -m 8 -o /dev/null -w "http://api.nuratech.ai -> %{http_code}\n" http://api.nuratech.ai
curl -s -m 8 http://api.nuratech.ai/health 2>&1 | head -c 120; echo
