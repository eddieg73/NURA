#!/bin/bash
export PATH="/opt/data/profiles/nura/.local/bin:/opt/hermes/bin:/opt/hermes/.venv/bin:$PATH"
echo "=== remaining MCP tests ==="
for M in hostinger-vps hostinger-api twilio-docs playwright firebase firecrawl openemr; do
  R=$(timeout 20 hermes mcp test $M 2>&1 | tail -2 | tr '\n' ' ' | head -c 70)
  echo "$M -> ${R:-FAIL}"
done
echo "=== endpoint pings ==="
echo -n "behive 8090: "; curl -s -m 5 -o /dev/null -w "%{http_code}\n" http://127.0.0.1:8090/mcp 2>/dev/null
echo -n "filesystem 8101: "; curl -s -m 5 -o /dev/null -w "%{http_code}\n" http://127.0.0.1:8101/mcp 2>/dev/null
echo -n "qdrant 6333: "; curl -s -m 5 -o /dev/null -w "%{http_code}\n" http://127.0.0.1:6333/collections 2>/dev/null
echo -n "redis 6379: "; timeout 4 bash -c 'echo PING | nc 127.0.0.1 6379 2>/dev/null | head -1' || echo "no nc"
echo -n "clinic openemr: "; ssh -o BatchMode=yes -o ConnectTimeout=6 -i ~/.ssh/id_nura_clean root@72.61.71.211 "curl -s -m 5 -o /dev/null -w '%{http_code}' http://127.0.0.1:80/ 2>/dev/null" 2>/dev/null
echo; echo -n "clinic docsgpt: "; ssh -o BatchMode=yes -o ConnectTimeout=6 -i ~/.ssh/id_nura_clean root@72.61.71.211 "curl -s -m 5 -o /dev/null -w '%{http_code}' http://127.0.0.1:7091/api/health 2>/dev/null" 2>/dev/null
echo; echo -n "clinic langfuse: "; ssh -o BatchMode=yes -o ConnectTimeout=6 -i ~/.ssh/id_nura_clean root@72.60.163.140 "curl -s -m 5 -o /dev/null -w '%{http_code}' http://127.0.0.1:3020/ 2>/dev/null" 2>/dev/null
echo; echo -n "lab ollama: "; ssh -o BatchMode=yes -o ConnectTimeout=6 -i ~/.ssh/id_nura_clean root@72.60.163.140 "curl -s -m 5 -o /dev/null -w '%{http_code}' http://127.0.0.1:11434/ 2>/dev/null" 2>/dev/null
echo; echo -n "lab paperclip: "; ssh -o BatchMode=yes -o ConnectTimeout=6 -i ~/.ssh/id_nura_clean root@72.60.163.140 "curl -s -m 5 -o /dev/null -w '%{http_code}' http://127.0.0.1:3100/ 2>/dev/null" 2>/dev/null
echo
echo "=== CLI versions ==="
for C in "hermes --version" "xurl --version" "ntn --version" "himalaya --version"; do
  R=$(timeout 8 $C 2>&1 | head -1 | head -c 60)
  echo "$C -> ${R:-FAIL}"
done
