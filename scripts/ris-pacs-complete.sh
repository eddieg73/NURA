#!/bin/bash
# RIS/PACS COMPLETE — ThaiRIS (RIS) + OHIF (viewer) + NPM doors + verify
set -e
cd /docker
echo "=== 1. clone ThaiRIS ==="
[ -d /docker/thairis ] || git clone --depth 1 https://github.com/SoftwareThaiRIS/thairis18free.git /docker/thairis 2>&1 | tail -1
ls /docker/thairis | head -6
echo "=== 2. the ThaiRIS compose ==="
cat > /docker/thairis/docker-compose.yml <<'EOF'
services:
  thairis-db:
    image: mariadb:10.11
    container_name: thairis-db
    environment:
      MYSQL_ROOT_PASSWORD: ThaiRis-DB-2026!!
      MYSQL_DATABASE: thairis
      MYSQL_USER: thairis
      MYSQL_PASSWORD: ThaiRis-2026!!
    volumes:
      - ./dbdata:/var/lib/mysql
    restart: unless-stopped
  thairis-web:
    image: php:8.2-apache
    container_name: thairis-web
    ports:
      - "32790:80"
    volumes:
      - ./:/var/www/html
    depends_on:
      - thairis-db
    restart: unless-stopped
EOF
cd /docker/thairis
echo "=== 3. import the SQL + patch connectdb ==="
docker compose up -d thairis-db 2>&1 | tail -1
sleep 8
SQL=$(ls *.sql 2>/dev/null | head -1 || find . -name "*.sql" | head -1)
echo "sql file: $SQL"
if [ -n "$SQL" ]; then
  docker exec -i thairis-db sh -c 'MYSQL_PWD=ThaiRis-DB-2026!! mysql -uroot thairis' < "$SQL" 2>&1 | head -2 || echo "sql import issue (continuing)"
fi
# patch the DB connection file
CONN=$(find . -iname "connectdb.php" | head -1)
echo "connect file: $CONN"
if [ -n "$CONN" ]; then
  sed -i "s/\$host[^;]*;/\$host = \"thairis-db\";/; s/\$user[^;]*;/\$user = \"thairis\";/; s/\$password[^;]*;/\$password = \"ThaiRis-2026!!\";/; s/\$dbname[^;]*;/\$dbname = \"thairis\";/" "$CONN" && echo "connectdb patched"
fi
docker compose up -d 2>&1 | tail -1
sleep 6
echo "=== 4. thairis verify ==="
curl -s -m 6 -o /dev/null -w "thairis:32790 -> %{http_code}\n" http://127.0.0.1:32790/
echo "=== 5. OHIF viewer compose ==="
mkdir -p /docker/ohif
cat > /docker/ohif/docker-compose.yml <<'EOF'
services:
  ohif:
    image: ohif/viewer:latest
    container_name: ohif-viewer
    ports:
      - "32791:80"
    environment:
      APP_CONFIG: /usr/share/nginx/html/app-config.js
    restart: unless-stopped
EOF
cd /docker/ohif
docker compose up -d 2>&1 | tail -1
sleep 12
echo "=== 6. ohif verify ==="
curl -s -m 6 -o /dev/null -w "ohif:32791 -> %{http_code}\n" http://127.0.0.1:32791/
echo "=== 7. NPM doors (ris + pacs) ==="
TOKEN=$(curl -s -m 8 -X POST http://127.0.0.1:8181/api/tokens -H 'Content-Type: application/json' -d "{\"identity\":\"hermes@nuratech.ai\",\"secret\":\"NPM-rdSjrIjJDZ6rNEgxyM6jzS4F\"}" | python3 -c 'import sys,json;print(json.load(sys.stdin).get("token",""))')
for ENTRY in "ris.nuratech.ai|72.61.71.211|32790" "pacs.nuratech.ai|72.61.71.211|32791"; do
  DOM=$(echo $ENTRY | cut -d'|' -f1); FH=$(echo $ENTRY | cut -d'|' -f2); FP=$(echo $ENTRY | cut -d'|' -f3)
  HID=$(curl -s -m 8 http://127.0.0.1:8181/api/nginx/proxy-hosts -H "Authorization: Bearer $TOKEN" | python3 -c "import sys,json
for h in json.load(sys.stdin):
    if '$DOM' in h.get('domain_names',[]): print(h['id']); break" 2>/dev/null)
  if [ -z "$HID" ]; then
    curl -s -m 8 -X POST http://127.0.0.1:8181/api/nginx/proxy-hosts -H "Authorization: Bearer $TOKEN" -H 'Content-Type: application/json' \
      -d "{\"domain_names\":[\"$DOM\"],\"forward_scheme\":\"http\",\"forward_host\":\"$FH\",\"forward_port\":$FP,\"enabled\":true,\"block_exploits\":false,\"caching_enabled\":false,\"allow_websocket_upgrade\":true,\"access_list_id\":0,\"meta\":{\"letsencrypt_agree\":false,\"dns_challenge\":false},\"certificate_id\":0,\"ssl_forced\":false}" \
      -o /dev/null -w "$DOM created -> %{http_code}\n"
  else
    curl -s -m 8 -X PUT http://127.0.0.1:8181/api/nginx/proxy-hosts/$HID -H "Authorization: Bearer $TOKEN" -H 'Content-Type: application/json' \
      -d "{\"domain_names\":[\"$DOM\"],\"forward_scheme\":\"http\",\"forward_host\":\"$FH\",\"forward_port\":$FP,\"enabled\":true,\"block_exploits\":false,\"caching_enabled\":false,\"allow_websocket_upgrade\":true,\"access_list_id\":0,\"meta\":{\"letsencrypt_agree\":false,\"dns_challenge\":false},\"certificate_id\":0,\"ssl_forced\":false}" \
      -o /dev/null -w "$DOM updated -> %{http_code}\n"
  fi
done
sleep 4
docker exec nginx-proxy-manager-app-1 nginx -s reload 2>&1 | head -1
echo "=== 8. public doors ==="
curl -s -m 8 -o /dev/null -w "ris.nuratech.ai -> %{http_code}\n" http://ris.nuratech.ai/
curl -s -m 8 -o /dev/null -w "pacs.nuratech.ai -> %{http_code}\n" http://pacs.nuratech.ai/
