#!/bin/bash
# Answer without key (auth-disabled mode) + fallback with the env key
ssh -o BatchMode=yes -o ConnectTimeout=10 -i ~/.ssh/id_nura_clean root@72.61.71.211 'echo "=== no key ==="; curl -s -m 50 -X POST http://127.0.0.1:7091/api/answer -H "Content-Type: application/json" -d "{\"question\":\"What is anatomy?\"}" 2>/dev/null | head -c 400; echo; echo "=== auth mode ==="; docker exec docsgpt-oss-backend-1 sh -c "grep -rn \"auth_mode\|AUTH_MODE\|token_generation\" /app/application/core/settings.py 2>/dev/null | head -4"'
