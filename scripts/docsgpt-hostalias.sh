#!/bin/bash
# Add host.docker.internal to backend + point DocsGPT at it + recreate + test
ssh -o BatchMode=yes -o ConnectTimeout=10 -i ~/.ssh/id_nura_clean root@72.61.71.211 'cd /docker/docsgpt/deployment && grep -n "extra_hosts" docker-compose.yaml | head -2 || echo "no extra_hosts"; python3 - <<EOF
import re
p = "docker-compose.yaml"
s = open(p).read()
if "host.docker.internal" not in s:
    # insert extra_hosts into backend service (after its image line)
    s = s.replace("image: arc53/docsgpt-oss-backend", "image: arc53/docsgpt-oss-backend\n    extra_hosts:\n      - \"host.docker.internal:host-gateway\"", 1)
    open(p, "w").write(s)
    print("extra_hosts added")
else:
    print("already present")
EOF
sed -i "s|^OPENAI_BASE_URL=.*|OPENAI_BASE_URL=http://host.docker.internal:11434/v1|" .env && docker compose -f docker-compose.yaml up -d backend 2>&1 | tail -1 && sleep 12 && K=$(grep "^API_KEY=" .env | head -1 | cut -d= -f2) && echo "=== answer test ===" && curl -s -m 40 -X POST http://127.0.0.1:7091/api/answer -H "Content-Type: application/json" -d "{\"question\":\"What is anatomy?\",\"api_key\":\"$K\"}" 2>/dev/null | head -c 350'
