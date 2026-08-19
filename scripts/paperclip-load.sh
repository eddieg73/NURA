#!/bin/bash
# Mapped paperclip transfer: kaqe + phantom issues -> LIVE board company 58ddc931 (root access)
set -e
U=$(docker inspect paperclip-db --format '{{range .Config.Env}}{{println .}}{{end}}' | grep '^POSTGRES_USER=' | cut -d= -f2-)
export PGPASSWORD=$(docker inspect paperclip-db --format '{{range .Config.Env}}{{println .}}{{end}}' | grep '^POSTGRES_PASSWORD=' | cut -d= -f2-)
CID="58ddc931-7dbb-44c3-ab34-2652571121fc"
for SRC in paperclip_kaqe paperclip_phantom; do
  echo "=== source $SRC issues columns ==="
  docker exec paperclip-db psql -U "$U" -d "$SRC" -t -c "SELECT column_name FROM information_schema.columns WHERE table_name='issues' ORDER BY ordinal_position" 2>/dev/null | tr -d ' ' | grep -v '^$' | tr '\n' ',' | head -c 400
  echo
  echo "source issues count:"
  docker exec paperclip-db psql -U "$U" -d "$SRC" -t -c "SELECT count(*) FROM issues" 2>/dev/null | head -1
done
echo "=== mapped inserts ==="
docker exec paperclip-db psql -U "$U" -d paperclip -c "INSERT INTO issues (id, company_id, title, description, status, priority, assignee_agent_id, created_at, updated_at)
SELECT id, '$CID', title, description, status, priority, assignee_agent_id, COALESCE(created_at, now()), COALESCE(updated_at, now())
FROM paperclip_kaqe.issues ON CONFLICT (id) DO NOTHING" 2>&1 | head -2
docker exec paperclip-db psql -U "$U" -d paperclip -c "INSERT INTO issues (id, company_id, title, description, status, priority, assignee_agent_id, created_at, updated_at)
SELECT id, '$CID', title, description, status, priority, assignee_agent_id, COALESCE(created_at, now()), COALESCE(updated_at, now())
FROM paperclip_phantom.issues ON CONFLICT (id) DO NOTHING" 2>&1 | head -2
echo "=== live board after ==="
docker exec paperclip-db psql -U "$U" -d paperclip -t -c "SELECT count(*) FROM issues" 2>/dev/null | head -1
docker exec paperclip-db psql -U "$U" -d paperclip -c "SELECT title, status FROM issues ORDER BY created_at DESC LIMIT 10" 2>&1 | head -14
