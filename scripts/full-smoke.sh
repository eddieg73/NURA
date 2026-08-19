#!/bin/bash
export PATH="/opt/data/profiles/nura/bin:/opt/data/profiles/nura/.local/bin:/opt/hermes/bin:/opt/hermes/.venv/bin:$PATH"
echo "=== MCP SMOKE (all enabled) ==="
for M in qdrant redis openemr gemini behive legal-case-law hostinger-vps hostinger-api twilio-docs firebase firecrawl notion hostinger-hosting hostinger-domains hostinger-dns hostinger-billing hostinger-reach chatwoot perfex paperclip elevenlabs homeassistant filesystem playwright; do
  R=$(timeout 18 hermes mcp test $M 2>&1 | grep -E "✓|✗|Error" | tail -1 | head -c 60)
  echo "$M -> ${R:-NO-OUTPUT}"
done
echo "=== ENDPOINT SMOKE ==="
echo -n "qdrant:6333 "; curl -s -m 5 -o /dev/null -w "%{http_code}\n" http://127.0.0.1:6333/collections 2>/dev/null
echo -n "behive:8090 "; curl -s -m 5 -o /dev/null -w "%{http_code}\n" http://127.0.0.1:8090/mcp 2>/dev/null
echo -n "filesystem:8101 "; curl -s -m 5 -o /dev/null -w "%{http_code}\n" http://127.0.0.1:8101/mcp 2>/dev/null
for EP in "72.61.71.211:docsgpt:http://127.0.0.1:7091/api/health" "72.60.163.140:langfuse:http://127.0.0.1:3020/" "72.60.163.140:ollama:http://127.0.0.1:11434/" "72.60.163.140:paperclip:http://127.0.0.1:3100/" "72.61.71.211:npm:http://127.0.0.1:81/" "72.61.71.211:openemr:http://127.0.0.1:8080/"; do
  NODE="${EP%%:*}"; REST="${EP#*:}"; NAME="${REST%%:*}"; URL="${REST#*:}"
  C=$(ssh -o BatchMode=yes -o ConnectTimeout=6 -i ~/.ssh/id_nura_clean root@$NODE "curl -s -m 5 -o /dev/null -w '%{http_code}' $URL 2>/dev/null" 2>/dev/null)
  echo "$NAME -> ${C:-UNREACHABLE}"
done
echo -n "nuratech.ai "; curl -s -m 6 -o /dev/null -w "%{http_code}\n" https://nuratech.ai/ 2>/dev/null
echo -n "medisun-emr "; curl -s -m 6 -o /dev/null -w "%{http_code}\n" https://medisun-emr.nuratech.ai/ 2>/dev/null
echo -n "paperclip.nuratech.ai "; curl -s -m 6 -o /dev/null -w "%{http_code}\n" https://paperclip.nuratech.ai/ 2>/dev/null
echo "=== CLI SMOKE ==="
for C in "hermes --version" "gh --version" "xurl --version" "ntn --version" "himalaya --version" "uv --version" "npx --version" "/opt/data/bin/tailscale version"; do
  R=$(timeout 8 $C 2>&1 | head -1 | head -c 50)
  echo "$C -> ${R:-FAIL}"
done
