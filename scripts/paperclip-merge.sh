#!/bin/bash
# Merge kaqe + phantom companies/issues/agents into the LIVE board DB (data-only restore, same schema)
set -e
U=$(docker inspect paperclip-db --format '{{range .Config.Env}}{{println .}}{{end}}' | grep '^POSTGRES_USER=' | cut -d= -f2-)
P=$(docker inspect paperclip-db --format '{{range .Config.Env}}{{println .}}{{end}}' | grep '^POSTGRES_PASSWORD=' | cut -d= -f2-)
export PGPASSWORD="$P"
echo "=== live board companies (before) ==="
docker exec paperclip-db psql -U "$U" -d paperclip -t -c "SELECT id, name FROM companies" 2>/dev/null | head -5
echo "=== merging kaqe ==="
docker exec paperclip-db pg_dump -U "$U" -d paperclip_kaqe --data-only --disable-triggers 2>/dev/null | docker exec -i paperclip-db psql -U "$U" -d paperclip 2>&1 | grep -cE "INSERT|ERROR" | head -1 || echo "merged"
echo "=== merging phantom ==="
docker exec paperclip-db pg_dump -U "$U" -d paperclip_phantom --data-only --disable-triggers 2>/dev/null | docker exec -i paperclip-db psql -U "$U" -d paperclip 2>&1 | grep -cE "INSERT|ERROR" | head -1 || echo "merged"
echo "=== live board companies (after) ==="
docker exec paperclip-db psql -U "$U" -d paperclip -t -c "SELECT id, name FROM companies" 2>/dev/null | head -8
echo "=== issues per company ==="
docker exec paperclip-db psql -U "$U" -d paperclip -t -c "SELECT c.name, count(i.id) FROM companies c LEFT JOIN issues i ON i.company_id = c.id GROUP BY c.name" 2>/dev/null | head -8
