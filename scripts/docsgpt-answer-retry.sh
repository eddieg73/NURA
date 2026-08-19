#!/bin/bash
# Answer retry with a longer window + log tail
ssh -o BatchMode=yes -o ConnectTimeout=10 -i ~/.ssh/id_nura_clean root@72.61.71.211 'echo "=== answer (120s window) ==="; curl -s -m 120 -X POST http://127.0.0.1:7091/api/answer -H "Content-Type: application/json" -d "{\"question\":\"What is anatomy?\",\"api_key\":\"REDACTED\"}" 2>/dev/null | head -c 600; echo; echo "=== log tail ==="; docker logs docsgpt-oss-backend-1 2>&1 | tail -4'
