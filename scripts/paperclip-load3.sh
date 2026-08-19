#!/bin/bash
# Paperclip transfer v3 — dump to files inside the container, psql -f (deterministic)
set -e
U=$(docker inspect paperclip-db --format '{{range .Config.Env}}{{println .}}{{end}}' | grep '^POSTGRES_USER=' | cut -d= -f2-)
export PGPASSWORD=$(docker inspect paperclip-db --format '{{range .Config.Env}}{{println .}}{{end}}' | grep '^POSTGRES_PASSWORD=' | cut -d= -f2-)
LIVE="58ddc931-7dbb-44c3-ab34-2652571121fc"
for SRC in paperclip_kaqe paperclip_phantom; do
  docker exec paperclip-db pg_dump -U "$U" -d "$SRC" --table=issues --data-only --disable-triggers 2>/dev/null > /tmp/$SRC-issues.sql
  sed -i -e "s/8e452712-77a3-42fd-8289-cdae7918af12/$LIVE/g" -e "s/999ff375-6128-41cf-b6c8-06b98673a29b/$LIVE/g" -e "s/425ddbd7-721a-4e4a-80d9-bb339762c6df/$LIVE/g" /tmp/$SRC-issues.sql
  docker cp /tmp/$SRC-issues.sql paperclip-db:/tmp/$SRC-issues.sql >/dev/null 2>&1
  echo "=== loading $SRC ==="
  docker exec paperclip-db psql -U "$U" -d paperclip -f /tmp/$SRC-issues.sql 2>&1 | grep -E "COPY|ERROR" | tail -3
done
echo "=== live board final ==="
docker exec paperclip-db psql -U "$U" -d paperclip -t -c "SELECT count(*) FROM issues" 2>/dev/null | head -1
docker exec paperclip-db psql -U "$U" -d paperclip -c "SELECT identifier, title, status FROM issues WHERE company_id = '$LIVE' ORDER BY created_at DESC LIMIT 12" 2>&1 | head -16
