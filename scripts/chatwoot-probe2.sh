#!/bin/bash
# Chatwoot users + account probe v2
CWU=$(docker inspect chatwoot-postgres-1 --format '{{range .Config.Env}}{{println .}}{{end}}' 2>/dev/null | grep '^POSTGRES_USER=' | cut -d= -f2-)
CWP=$(docker inspect chatwoot-postgres-1 --format '{{range .Config.Env}}{{println .}}{{end}}' 2>/dev/null | grep '^POSTGRES_PASSWORD=' | cut -d= -f2-)
echo "pg user len=${#CWU} pass len=${#CWP}"
docker exec chatwoot-postgres-1 psql -U "$CWU" -d chatwoot_production -t -c "SELECT id, email, name, type FROM users ORDER BY id LIMIT 6" 2>&1 | head -8
echo "=== accounts ==="
docker exec chatwoot-postgres-1 psql -U "$CWU" -d chatwoot_production -t -c "SELECT id, name FROM accounts LIMIT 4" 2>&1 | head -5
echo "=== channels ==="
docker exec chatwoot-postgres-1 psql -U "$CWU" -d chatwoot_production -t -c "SELECT id, type FROM channels ORDER BY id LIMIT 6" 2>&1 | head -7
