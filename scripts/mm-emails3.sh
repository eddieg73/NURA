#!/bin/bash
# Mattermost real-email correction v3 — direct DB (founder 08-04 explicit)
set -e
PG=mattermost-r2wm-postgres-1
PGU=$(docker inspect "$PG" --format '{{range .Config.Env}}{{println .}}{{end}}' 2>/dev/null | grep '^POSTGRES_USER=' | cut -d= -f2-)
docker exec "$PG" psql -U "$PGU" -d mattermost -c "UPDATE users SET email = 'eg@nuratech.ai' WHERE username = 'eddie'" 2>&1 | head -1
docker exec "$PG" psql -U "$PGU" -d mattermost -c "UPDATE users SET email = 'Nura@nuratech.ai' WHERE username = 'hermes'" 2>&1 | head -1
docker exec "$PG" psql -U "$PGU" -d mattermost -c "UPDATE users SET email = 'araj@nuratech.ai' WHERE username = 'amrit'" 2>&1 | head -1
docker exec "$PG" psql -U "$PGU" -d mattermost -c "UPDATE users SET email = 'Oussama@nuratech.ai' WHERE username = 'oussama'" 2>&1 | head -1
docker exec "$PG" psql -U "$PGU" -d mattermost -c "UPDATE users SET email = 'Jade@nuratech.ai' WHERE username = 'jade'" 2>&1 | head -1
echo "=== verify ==="
docker exec "$PG" psql -U "$PGU" -d mattermost -t -c "SELECT username, email FROM users WHERE username IN ('eddie','hermes','amrit','oussama','jade','atlas') ORDER BY username" 2>&1 | head -8
