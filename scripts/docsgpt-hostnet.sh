#!/bin/bash
# Backend -> host network (127.0.0.1 lanes) + recreate + answer test
ssh -o BatchMode=yes -o ConnectTimeout=10 -i ~/.ssh/id_nura_clean root@72.61.71.211 'cd /docker/docsgpt/deployment && python3 - <<PYEOF
p = "docker-compose.yaml"
s = open(p).read()
if "network_mode: host" not in s:
    marker = "  backend:\n    user: root\n"
    if marker in s:
        s = s.replace(marker, marker + "    network_mode: host\n", 1)
        open(p, "w").write(s)
        print("network_mode host INSERTED")
    else:
        print("MARKER NOT FOUND")
else:
    print("already host")
PYEOF
sed -i "s|http://host.docker.internal:11434|http://127.0.0.1:11434|g" .env && sed -i "s|@docsgpt-oss-redis-1:|@127.0.0.1:|g; s|@redis:|@127.0.0.1:|g; s|@docsgpt-oss-postgres-1:|@127.0.0.1:|g; s|@postgres:|@127.0.0.1:|g" .env && grep -E "OPENAI_BASE_URL|DATABASE_URL|REDIS_URL" .env | sed "s|://[^@]*@|://***@|" | head -3 && docker compose -f docker-compose.yaml up -d --force-recreate backend 2>&1 | tail -1 && sleep 15 && K=$(grep "^API_KEY=" .env | head -1 | cut -d= -f2) && echo "=== answer test ===" && curl -s -m 50 -X POST http://127.0.0.1:7091/api/answer -H "Content-Type: application/json" -d "{\"question\":\"What is anatomy?\",\"api_key\":\"$K\"}" 2>/dev/null | head -c 500'
