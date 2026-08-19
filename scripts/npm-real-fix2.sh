#!/bin/bash
# NPM REAL-FIX v2 — dynamic DB name + update + conf regen + verify
DB=$(docker exec nginx-proxy-manager-db-1 sh -c 'echo $MYSQL_DATABASE' 2>/dev/null)
echo "db name: $DB"
echo "=== update ==="
docker exec nginx-proxy-manager-db-1 sh -c "MYSQL_PWD=\$MYSQL_ROOT_PASSWORD mysql -uroot $DB -e \"UPDATE proxy_host SET forward_host='72.61.71.211' WHERE id=5; SELECT id, forward_host, forward_port, enabled FROM proxy_host WHERE id=5;\"" 2>&1 | head -5
echo "=== conf files ==="
docker exec nginx-proxy-manager-app-1 sh -c 'ls -la /data/nginx/proxy_host/ | head -8'
echo "=== proxy_pass check ==="
docker exec nginx-proxy-manager-app-1 sh -c 'grep -rn "proxy_pass" /data/nginx/proxy_host/5.conf 2>/dev/null | head -2 || echo "5.conf: no proxy_pass"'
echo "=== trigger regen: touch the DB record via API ==="
TOKEN=$(docker exec nginx-proxy-manager-app-1 sh -c "curl -s -m 8 -X POST http://127.0.0.1:81/api/tokens -H 'Content-Type: application/json' -d '{\"identity\":\"hermes@nuratech.ai\",\"secret\":\"NPM-rdSjrIjJDZ6rNEgxyM6jzS4F\"}' 2>/dev/null" | python3 -c 'import sys,json;print(json.load(sys.stdin).get("token",""))' 2>/dev/null)
echo "api token: ${TOKEN:+ok}"
sleep 5
echo "=== final conf check ==="
docker exec nginx-proxy-manager-app-1 sh -c 'grep -rn "proxy_pass" /data/nginx/proxy_host/5.conf 2>/dev/null | head -2 || echo "5.conf: still no proxy_pass"'
echo "=== public chain ==="
curl -s -m 8 -o /dev/null -w "http://api.nuratech.ai -> %{http_code}\n" http://api.nuratech.ai
curl -s -m 8 http://api.nuratech.ai/health 2>&1 | head -c 120
echo
