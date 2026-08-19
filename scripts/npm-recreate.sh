#!/bin/bash
# NPM DIAG + RECREATE — compare confs, delete host 5, re-create clean, verify
echo "=== 1.conf (healthy) size vs 5.conf ==="
docker exec nginx-proxy-manager-app-1 sh -c 'wc -c /data/nginx/proxy_host/1.conf /data/nginx/proxy_host/5.conf 2>/dev/null'
echo "=== 5.conf tail ==="
docker exec nginx-proxy-manager-app-1 sh -c 'tail -20 /data/nginx/proxy_host/5.conf 2>/dev/null'
TOKEN=$(curl -s -m 8 -X POST http://127.0.0.1:8181/api/tokens -H 'Content-Type: application/json' -d "{\"identity\":\"hermes@nuratech.ai\",\"secret\":\"NPM-rdSjrIjJDZ6rNEgxyM6jzS4F\"}" | python3 -c 'import sys,json;print(json.load(sys.stdin).get("token",""))')
echo "=== DELETE host 5 ==="
curl -s -m 10 -X DELETE http://127.0.0.1:8181/api/nginx/proxy-hosts/5 -H "Authorization: Bearer $TOKEN" -o /dev/null -w "DELETE -> %{http_code}\n"
sleep 2
echo "=== POST fresh (minimal schema) ==="
curl -s -m 10 -X POST http://127.0.0.1:8181/api/nginx/proxy-hosts \
  -H "Authorization: Bearer $TOKEN" -H 'Content-Type: application/json' \
  -d '{"domain_names":["api.nuratech.ai"],"forward_scheme":"http","forward_host":"72.61.71.211","forward_port":8642,"enabled":true,"block_exploits":false,"caching_enabled":false,"allow_websocket_upgrade":true,"access_list_id":0,"meta":{"letsencrypt_agree":false,"dns_challenge":false},"certificate_id":0,"ssl_forced":false}' \
  -o /tmp/post.json -w "POST -> %{http_code}\n"
head -c 120 /tmp/post.json; echo
sleep 6
echo "=== conf check ==="
docker exec nginx-proxy-manager-app-1 sh -c 'ls /data/nginx/proxy_host/ | tail -3; grep -n "proxy_pass" /data/nginx/proxy_host/*.conf 2>/dev/null | grep -i api | head -2 || echo "no api conf proxy_pass"'
echo "=== reload + public chain ==="
docker exec nginx-proxy-manager-app-1 nginx -s reload 2>&1 | head -1
sleep 3
curl -s -m 8 -o /dev/null -w "http://api.nuratech.ai -> %{http_code}\n" http://api.nuratech.ai
curl -s -m 8 http://api.nuratech.ai/health 2>&1 | head -c 120
echo
