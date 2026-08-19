#!/bin/bash
# Paperclip transfer v4 — dblink cross-DB read with the COMMON columns (deterministic)
set -e
U=$(docker inspect paperclip-db --format '{{range .Config.Env}}{{println .}}{{end}}' | grep '^POSTGRES_USER=' | cut -d= -f2-)
P=$(docker inspect paperclip-db --format '{{range .Config.Env}}{{println .}}{{end}}' | grep '^POSTGRES_PASSWORD=' | cut -d= -f2-)
export PGPASSWORD="$P"
LIVE="58ddc931-7dbb-44c3-ab34-2652571121fc"
docker exec paperclip-db psql -U "$U" -d paperclip -c "CREATE EXTENSION IF NOT EXISTS dblink" 2>&1 | head -1
for SRC in paperclip_kaqe paperclip_phantom; do
  echo "=== dblink load: $SRC ==="
  docker exec paperclip-db psql -U "$U" -d paperclip -v ON_ERROR_STOP=0 -c "
  INSERT INTO issues (id, company_id, title, description, status, priority, assignee_agent_id, created_at, updated_at)
  SELECT id, '$LIVE', title, description, status, priority, assignee_agent_id, COALESCE(created_at, now()), COALESCE(updated_at, now())
  FROM dblink('dbname=$SRC user=$U password=$P', 'SELECT id, title, description, status, priority, assignee_agent_id, created_at, updated_at FROM issues')
  AS t(id uuid, title text, description text, status text, priority text, assignee_agent_id uuid, created_at timestamptz, updated_at timestamptz)
  ON CONFLICT (id) DO NOTHING" 2>&1 | grep -E "INSERT|ERROR" | head -2
done
echo "=== live board final ==="
docker exec paperclip-db psql -U "$U" -d paperclip -t -c "SELECT count(*) FROM issues" 2>/dev/null | head -1
docker exec paperclip-db psql -U "$U" -d paperclip -c "SELECT identifier, title, status FROM issues WHERE company_id = '$LIVE' ORDER BY created_at DESC LIMIT 12" 2>&1 | head -16
