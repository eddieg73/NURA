#!/bin/bash
# Inspect the agents table schema + register an agent key + answer test
ssh -o BatchMode=yes -o ConnectTimeout=10 -i ~/.ssh/id_nura_clean root@72.61.71.211 'echo "=== agents schema ==="; docker exec docsgpt-oss-postgres-1 psql -U docsgpt -d docsgpt -c "\d agents" 2>/dev/null | head -20; echo "=== existing agents ==="; docker exec docsgpt-oss-postgres-1 psql -U docsgpt -d docsgpt -c "SELECT id, name, api_key FROM agents LIMIT 3;" 2>/dev/null | head -6'
