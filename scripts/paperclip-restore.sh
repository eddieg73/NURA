#!/bin/bash
# Restore kaqe + phantom paperclip backups into the Lab postgres as separate DBs (read-only merge prep)
set -e
# creds from the paperclip-db compose (sealed on host, never echoed)
U=$(docker inspect paperclip-db --format '{{range .Config.Env}}{{println .}}{{end}}' | grep '^POSTGRES_USER=' | cut -d= -f2-)
P=$(docker inspect paperclip-db --format '{{range .Config.Env}}{{println .}}{{end}}' | grep '^POSTGRES_PASSWORD=' | cut -d= -f2-)
DB=$(docker inspect paperclip-db --format '{{range .Config.Env}}{{println .}}{{end}}' | grep '^POSTGRES_DB=' | cut -d= -f2-)
echo "creds: user=${#U} pass=${#P} db=$DB"
export PGPASSWORD="$P"
# 1) kaqe (original board, Clinic) -> paperclip_kaqe
gunzip -c /tmp/kaqe-latest.sql.gz > /tmp/kaqe.sql 2>/dev/null || cp /tmp/kaqe-latest.sql.gz /tmp/kaqe.sql
docker exec -i paperclip-db psql -U "$U" -d "$DB" -c "CREATE DATABASE IF NOT EXISTS paperclip_kaqe" 2>/dev/null || docker exec -i paperclip-db psql -U "$U" -d postgres -c "CREATE DATABASE paperclip_kaqe" 2>&1 | head -1
docker exec -i paperclip-db psql -U "$U" -d paperclip_kaqe < /tmp/kaqe.sql 2>&1 | tail -2
echo "kaqe companies:"
docker exec paperclip-db psql -U "$U" -d paperclip_kaqe -t -c "SELECT id, name FROM companies" 2>/dev/null | head -5
# 2) phantom (my directives) -> paperclip_phantom
gunzip -c /tmp/phantom-latest.sql.gz > /tmp/phantom.sql 2>/dev/null || cp /tmp/phantom-latest.sql.gz /tmp/phantom.sql
docker exec -i paperclip-db psql -U "$U" -d postgres -c "CREATE DATABASE paperclip_phantom" 2>&1 | head -1
docker exec -i paperclip-db psql -U "$U" -d paperclip_phantom < /tmp/phantom.sql 2>&1 | tail -2
echo "phantom companies:"
docker exec paperclip-db psql -U "$U" -d paperclip_phantom -t -c "SELECT id, name FROM companies" 2>/dev/null | head -5
