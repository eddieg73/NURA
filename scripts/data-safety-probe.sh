#!/bin/bash
# Data safety probe: NURA Redis + Qdrant (Clinic) + medisun source (Lab)
echo "=== NURA Redis (Clinic redis-gc8b) ==="
RP=$(grep -E '^REDIS_PASSWORD=' /docker/redis-gc8b/.env | cut -d= -f2-)
docker exec redis-gc8b-redis-1 redis-cli -a "$RP" --no-auth-warning DBSIZE 2>/dev/null | head -1
echo "=== Qdrant (Clinic) ==="
docker exec qdrant-fytk-qdrant-1 sh -c 'curl -s -m 5 http://127.0.0.1:6333/collections' 2>/dev/null | python3 -c "
import sys, json
d = json.load(sys.stdin)
for c in d.get('result', {}).get('collections', []):
    print('collection:', c['name'])
" 2>/dev/null | head -5
docker exec qdrant-fytk-qdrant-1 sh -c 'for c in $(curl -s -m 5 http://127.0.0.1:6333/collections | python3 -c "import sys,json; [print(x[\"name\"]) for x in json.load(sys.stdin)[\"result\"][\"collections\"]]" 2>/dev/null); do echo -n "$c points: "; curl -s -m 5 "http://127.0.0.1:6333/collections/$c" | python3 -c "import sys,json; print(json.load(sys.stdin)[\"result\"][\"points_count\"])" 2>/dev/null; done' 2>/dev/null | head -6
