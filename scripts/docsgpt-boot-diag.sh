#!/bin/bash
# DocsGPT backend boot diagnosis + fix
ssh -o BatchMode=yes -o ConnectTimeout=10 -i ~/.ssh/id_nura_clean root@72.61.71.211 'echo "=== boot logs ==="; docker logs docsgpt-oss-backend-1 2>&1 | grep -iE "error|refused|connect|failed|exception" | tail -6; echo "=== postgres host port ==="; docker port docsgpt-oss-postgres-1 2>/dev/null | head -2; echo "=== redis host port ==="; docker port docsgpt-oss-redis-1 2>/dev/null | head -2; echo "=== env urls ==="; grep -E "DATABASE_URL|REDIS_URL|CELERY_BROKER" /docker/docsgpt/deployment/.env | sed "s|://[^@]*@|://***@|" | head -3'
