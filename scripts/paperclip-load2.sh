#!/bin/bash
# Paperclip transfer v2 — pg_dump issues (data-only) + company remap -> live board 58ddc931
set -e
U=$(docker inspect paperclip-db --format '{{range .Config.Env}}{{println .}}{{end}}' | grep '^POSTGRES_USER=' | cut -d= -f2-)
export PGPASSWORD=$(docker inspect paperclip-db --format '{{range .Config.Env}}{{println .}}{{end}}' | grep '^POSTGRES_PASSWORD=' | cut -d= -f2-)
LIVE="58ddc931-7dbb-44c3-ab34-2652571121fc"
KAQE="8e452712-77a3-42fd-8289-cdae7918af12"
PH1="999ff375-6128-41cf-b6c8-06b98673a29b"
PH2="425ddbd7-721a-4e4a-80d9-bb339762c6df"
for SRC in paperclip_kaqe paperclip_phantom; do
  echo "=== dumping $SRC issues ==="
  docker exec paperclip-db pg_dump -U "$U" -d "$SRC" --table=issues --data-only 2>/dev/null \
    | sed -e "s/$KAQE/$LIVE/g" -e "s/$PH1/$LIVE/g" -e "s/$PH2/$LIVE/g" \
    | docker exec -i paperclip-db psql -U "$U" -d paperclip -v ON_ERROR_STOP=0 2>&1 | grep -cE "INSERT 0 1" | head -1
done
echo "=== live board final ==="
docker exec paperclip-db psql -U "$U" -d paperclip -t -c "SELECT count(*) FROM issues" 2>/dev/null | head -1
docker exec paperclip-db psql -U "$U" -d paperclip -c "SELECT identifier, title, status FROM issues WHERE company_id = '$LIVE' ORDER BY created_at DESC LIMIT 12" 2>&1 | head -16
