#!/bin/bash
# Proper extra_hosts insert into backend service + recreate + verify + answer test
ssh -o BatchMode=yes -o ConnectTimeout=10 -i ~/.ssh/id_nura_clean root@72.61.71.211 'cd /docker/docsgpt/deployment && python3 - <<PYEOF
p = "docker-compose.yaml"
s = open(p).read()
if "host.docker.internal" not in s:
    marker = "    build: ../application\n"
    if marker in s:
        s = s.replace(marker, marker + "    extra_hosts:\n      - \"host.docker.internal:host-gateway\"\n", 1)
        open(p, "w").write(s)
        print("extra_hosts INSERTED")
    else:
        print("MARKER NOT FOUND")
else:
    print("already present")
PYEOF
grep -n "extra_hosts" docker-compose.yaml | head -2 && docker compose -f docker-compose.yaml up -d --force-recreate backend 2>&1 | tail -1 && sleep 14 && echo "=== resolve ===" && docker exec docsgpt-oss-backend-1 sh -c "getent hosts host.docker.internal 2>/dev/null | head -1" && echo "=== llm probe ===" && docker exec docsgpt-oss-backend-1 sh -c "curl -s -m 6 -o /dev/null -w \"%{http_code}\" http://host.docker.internal:11434/ 2>/dev/null" && echo && K=$(grep "^API_KEY=" .env | head -1 | cut -d= -f2) && echo "=== answer test ===" && curl -s -m 45 -X POST http://127.0.0.1:7091/api/answer -H "Content-Type: application/json" -d "{\"question\":\"What is anatomy?\",\"api_key\":\"$K\"}" 2>/dev/null | head -c 400'
