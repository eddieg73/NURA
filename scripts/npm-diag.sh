#!/bin/bash
# NPM internal diagnostic — the TLS chain
echo "=== container listeners ==="
docker exec nginx-proxy-manager-app-1 sh -c 'netstat -tln 2>/dev/null | grep -E ":80|:443|:81" | head -6; echo "---processes---"; ps aux 2>/dev/null | grep -iE "nginx|openresty" | grep -v grep | head -4' 2>&1 | head -10
echo "=== host -> container 8443 test ==="
curl -s -m 6 -o /dev/null -w "http 8080: %{http_code}\n" http://127.0.0.1:8080/ 2>&1 | head -1
echo "=== nginx config test ==="
docker exec nginx-proxy-manager-app-1 sh -c 'nginx -t 2>&1 | tail -3' 2>&1 | head -4
echo "=== default site (the proxy hosts) ==="
docker exec nginx-proxy-manager-app-1 sh -c 'grep -l "chat.nuratech\|chatwoot" /etc/nginx/conf.d/*.conf 2>/dev/null | head -3; ls /data/nginx/proxy_host/*.conf 2>/dev/null | head -4' 2>&1 | head -6
