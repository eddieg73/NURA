#!/bin/bash
# NPM REAL-FIX — MariaDB update + app restart (regenerates the conf) + verify
echo "=== mariadb env ==="
docker exec nginx-proxy-manager-db-1 sh -c 'env | grep -E "MYSQL_(ROOT|DATABASE|USER)" | sed "s/=.*/=<set>/"' 2>/dev/null | head -4
echo "=== DB update via mariadb ==="
docker exec nginx-proxy-manager-db-1 sh -c 'MYSQL_PWD=$MYSQL_ROOT_PASSWORD mysql -uroot nginxproxymanager -e "UPDATE proxy_host SET forward_host=\"72.61.71.211\" WHERE id=5; SELECT id, domain_names, forward_host, forward_port, enabled FROM proxy_host WHERE id=5\G"' 2>&1 | head -8
echo "=== restart the NPM app (regenerates the confs) ==="
docker restart nginx-proxy-manager-app-1 2>&1 | head -1
sleep 12
echo "=== conf check ==="
docker exec nginx-proxy-manager-app-1 sh -c 'grep -n "proxy_pass" /data/nginx/proxy_host/5.conf 2>/dev/null | head -2 || echo "still no proxy_pass"'
echo "=== public chain ==="
curl -s -m 8 -o /dev/null -w "http://api.nuratech.ai -> %{http_code}\n" http://api.nuratech.ai
curl -s -m 8 http://api.nuratech.ai/health 2>&1 | head -c 120
echo
