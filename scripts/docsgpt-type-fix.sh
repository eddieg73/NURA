#!/bin/bash
# Fix the agent type + final answer test
ssh -o BatchMode=yes -o ConnectTimeout=10 -i ~/.ssh/id_nura_clean root@72.61.71.211 "docker exec docsgpt-oss-postgres-1 psql -U docsgpt -d docsgpt -c \"UPDATE agents SET agent_type = 'classic' WHERE key = 'REDACTED' RETURNING id, agent_type;\" 2>&1 | head -4; echo '=== answer test ==='; curl -s -m 60 -X POST http://127.0.0.1:7091/api/answer -H 'Content-Type: application/json' -d '{\"question\":\"What is anatomy?\",\"api_key\":\"REDACTED\"}' 2>/dev/null | head -c 500"
