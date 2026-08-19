#!/bin/bash
# Mattermost probe v2 — container paths + postgres user discovery
MM=mattermost-r2wm-mattermost-1
PG=mattermost-r2wm-postgres-1
docker exec "$MM" sh -c 'ls /mattermost/bin/ 2>/dev/null | head -4; echo "---"; ls / 2>/dev/null | head -6' 2>&1 | head -10
echo "=== pg env ==="
docker inspect "$PG" --format '{{range .Config.Env}}{{println .}}{{end}}' 2>/dev/null | grep -E '^POSTGRES_(USER|DB)=' | head -2
PGU=$(docker inspect "$PG" --format '{{range .Config.Env}}{{println .}}{{end}}' 2>/dev/null | grep '^POSTGRES_USER=' | cut -d= -f2-)
PGD=$(docker inspect "$PG" --format '{{range .Config.Env}}{{println .}}{{end}}' 2>/dev/null | grep '^POSTGRES_DB=' | cut -d= -f2-)
echo "user=$PGU db=$PGD"
docker exec "$PG" psql -U "$PGU" -d "$PGD" -t -c "SELECT username, email, roles FROM users ORDER BY createat LIMIT 6" 2>&1 | head -8
