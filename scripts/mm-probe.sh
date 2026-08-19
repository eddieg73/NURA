#!/bin/bash
# Mattermost state probe
MM=$(docker ps --format '{{.Names}}' | grep -i mattermost | grep -v postgres | head -1)
echo "container=$MM"
docker exec "$MM" ls /mattermost/bin/mmctl 2>/dev/null | head -1 || echo "no mmctl"
echo "=== users ==="
PG=$(docker ps --format '{{.Names}}' | grep -i mattermost | grep -i postgres | head -1)
echo "pg=$PG"
PASS=$(grep -E '^POSTGRES_PASSWORD=' /docker/mattermost-r2wm/.env | cut -d= -f2-)
if [ -n "$PG" ] && [ -n "$PASS" ]; then
  docker exec "$PG" psql -U mmuser -d mattermost -t -c "SELECT username, email, roles FROM users ORDER BY createat LIMIT 6" 2>&1 | head -8
fi
