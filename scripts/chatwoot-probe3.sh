#!/bin/bash
# Chatwoot probe v3 — list databases first
CWU=$(docker inspect chatwoot-postgres-1 --format '{{range .Config.Env}}{{println .}}{{end}}' 2>/dev/null | grep '^POSTGRES_USER=' | cut -d= -f2-)
echo "=== databases ==="
docker exec chatwoot-postgres-1 psql -U "$CWU" -d postgres -t -c "SELECT datname FROM pg_database WHERE datistemplate = false" 2>&1 | head -8
DB=$(docker exec chatwoot-postgres-1 psql -U "$CWU" -d postgres -t -c "SELECT datname FROM pg_database WHERE datistemplate = false" 2>/dev/null | grep -v '^$' | head -1)
echo "db=$DB"
echo "=== users ==="
docker exec chatwoot-postgres-1 psql -U "$CWU" -d "$DB" -t -c "SELECT id, email, name, type FROM users ORDER BY id LIMIT 6" 2>&1 | head -8
echo "=== accounts ==="
docker exec chatwoot-postgres-1 psql -U "$CWU" -d "$DB" -t -c "SELECT id, name FROM accounts LIMIT 4" 2>&1 | head -5
echo "=== channels ==="
docker exec chatwoot-postgres-1 psql -U "$CWU" -d "$DB" -t -c "SELECT id, type FROM channels ORDER BY id LIMIT 6" 2>&1 | head -7
