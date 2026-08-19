#!/bin/bash
# Phase-1 verification probes (runs on Clinic)
echo "=== CONTAINERS ==="
docker ps --format '{{.Names}} | {{.Status}}' | grep mirth-oie
echo "=== SCHEMA TABLES ==="
docker exec mirth-oie-postgres-db-1 psql -U mirth -d enginedb -tAc "SELECT count(*) FROM pg_tables WHERE schemaname='public'"
echo "=== EXTENSION TABLE ==="
docker exec mirth-oie-postgres-db-1 psql -U mirth -d enginedb -tAc "SELECT count(*) FROM EXTENSION" 2>&1
echo "=== ENGINE LOG (extension/startup) ==="
docker logs mirth-oie-mirth-engine-1 2>&1 | grep -iE "extension|successfully started|error" | tail -8
echo "=== ADMIN API ==="
curl -sk -m 10 -o /dev/null -w "admin-8444:%{http_code}\n" -u admin:admin -H "X-Requested-With: OpenAPI" https://localhost:8444/api/server/version
