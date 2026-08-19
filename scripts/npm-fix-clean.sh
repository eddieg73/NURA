#!/bin/bash
# NPM FIX — the clean file-based execution: DB update + conf edit + reload + verify
echo "=== DB update ==="
docker exec nginx-proxy-manager-app-1 sqlite3 /data/database.sqlite "UPDATE proxy_host SET forward_host='72.61.71.211' WHERE id=5; SELECT id, forward_host, forward_port, enabled FROM proxy_host WHERE id=5;"
echo "=== conf files ==="
docker exec nginx-proxy-manager-app-1 sh -c 'ls /data/nginx/proxy_host/ 2>/dev/null | head -5'
echo "=== conf proxy_pass lines ==="
docker exec nginx-proxy-manager-app-1 sh -c 'grep -n "proxy_pass" /data/nginx/proxy_host/5.conf 2>/dev/null | head -3 || echo "no 5.conf proxy_pass"'
echo "=== conf fix ==="
docker exec nginx-proxy-manager-app-1 sh -c 'if grep -q "proxy_pass http://hermes-gateway:8642" /data/nginx/proxy_host/5.conf 2>/dev/null; then sed -i "s|proxy_pass http://hermes-gateway:8642|proxy_pass http://72.61.71.211:8642|" /data/nginx/proxy_host/5.conf && echo "conf patched"; else echo "pattern not found - showing conf head"; head -30 /data/nginx/proxy_host/5.conf 2>/dev/null; fi'
echo "=== reload ==="
docker exec nginx-proxy-manager-app-1 nginx -s reload 2>&1 | head -2
echo reloaded
sleep 3
echo "=== public chain ==="
curl -s -m 8 -o /dev/null -w "http://api.nuratech.ai -> %{http_code}\n" http://api.nuratech.ai
curl -s -m 8 http://api.nuratech.ai/health 2>&1 | head -c 120
echo
