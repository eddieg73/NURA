#!/bin/bash
# NPM FORWARD FIX — point the api.nuratech.ai host at the HOST-IP:8642 (the docker-proxy path)
set -e
cd /docker/nginx-proxy-manager
# 1. login for the token
TOKEN=$(curl -s -m 8 -X POST http://127.0.0.1:8181/api/tokens \
  -H 'Content-Type: application/json' \
  -d "{\"identity\":\"${NPM_ADMIN}\",\"secret\":\"${NPM_PASS}\"}" | python3 -c 'import sys,json;print(json.load(sys.stdin).get("token",""))')
if [ -z "$TOKEN" ]; then echo "LOGIN FAILED"; exit 1; fi
echo "token: ok"
# 2. find the api.nuratech.ai host
HOSTS=$(curl -s -m 8 http://127.0.0.1:8181/api/nginx/proxy-hosts -H "Authorization: Bearer $TOKEN")
HID=$(echo "$HOSTS" | python3 -c 'import sys,json
for h in json.load(sys.stdin):
    if "api.nuratech" in h.get("domain",""): print(h["id"]); break')
echo "host id: $HID"
if [ -z "$HID" ]; then echo "HOST NOT FOUND"; exit 1; fi
# 3. patch the forward_host to the HOST-IP (the docker-proxy listens on 0.0.0.0:8642)
curl -s -m 8 -X PUT http://127.0.0.1:8181/api/nginx/proxy-hosts/$HID \
  -H "Authorization: Bearer $TOKEN" -H 'Content-Type: application/json' \
  -d "{\"forward_host\":\"72.61.71.211\",\"forward_port\":8642,\"forward_scheme\":\"http\",\"enabled\":true,\"certificate_id\":0,\"ssl_forced\":false,\"block_exploits\":false,\"caching_enabled\":false,\"allow_websocket_upgrade\":true,\"access_list_id\":0,\"advanced_config\":\"\",\"locations\":[],\"meta\":{\"letsencrypt_agree\":false,\"dns_challenge\":false}}}" \
  -o /dev/null -w "PUT -> %{http_code}\n" | tail -1
sleep 3
echo "=== verify the public chain ==="
curl -s -m 8 -o /dev/null -w "http://api.nuratech.ai -> %{http_code}\n" http://api.nuratech.ai
curl -s -m 8 http://api.nuratech.ai/health 2>&1 | head -c 100; echo
