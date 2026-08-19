#!/usr/bin/env bash
# NURATECH.AI E2E HEALTH & INTEGRITY AUDITOR (the NURA-adapted — the fleet-names!)
set -uo pipefail
GREEN="\033[0;32m"; RED="\033[0;31m"; YELLOW="\033[1;33m"; CYAN="\033[0;36m"; BOLD="\033[1m"; NC="\033[0m"
TOTAL=0; PASSED=0; FAILED=0; WARNINGS=0
report() {
  local cat="$1" tgt="$2" st="$3" det="$4"
  TOTAL=$((TOTAL+1))
  if [[ "$st" == "PASS" ]]; then PASSED=$((PASSED+1)); printf "  ${GREEN}[✓]${NC} %-16s : %-24s (%s)\n" "$cat" "$tgt" "$det";
  elif [[ "$st" == "WARN" ]]; then WARNINGS=$((WARNINGS+1)); printf "  ${YELLOW}[!]${NC} %-16s : %-24s (%s)\n" "$cat" "$tgt" "$det";
  else FAILED=$((FAILED+1)); printf "  ${RED}[✗]${NC} %-16s : %-24s (%s)\n" "$cat" "$tgt" "$det"; fi
}
echo -e "${BOLD}${CYAN}=== NURA E2E HEALTH ===${NC}"

# 1. THE CONTAINERS (the NURA-fleet — the right hosts!)
for c in docsgpt-oss-backend-1 chatwoot-rails-1 mirth-connect-mirth-connect-1 orthanc-pacs thairis-web ohif-viewer; do
  st=$(ssh -o BatchMode=yes -o ConnectTimeout=5 -i ~/.ssh/id_nura_clean root@72.61.71.211 "docker inspect --format='{{.State.Status}}' $c 2>/dev/null || echo not_found" 2>/dev/null)
  [[ "$st" == "running" ]] && report "Container" "$c" "PASS" "running" || report "Container" "$c" "FAIL" "${st:-unreachable}"
done
n8nst=$(ssh -o BatchMode=yes -o ConnectTimeout=5 -i ~/.ssh/id_nura_clean root@195.35.32.113 "docker inspect --format='{{.State.Status}}' n8n-n8n-6tp2rd-n8n-1 2>/dev/null || echo not_found" 2>/dev/null)
[[ "$n8nst" == "running" ]] && report "Container" "n8n" "PASS" "running" || report "Container" "n8n" "FAIL" "${n8nst:-unreachable}"
lcst=$(ssh -o BatchMode=yes -o ConnectTimeout=5 -i ~/.ssh/id_nura_clean root@72.60.163.140 "docker inspect --format='{{.State.Status}}' LibreChat 2>/dev/null || echo not_found" 2>/dev/null)
[[ "$lcst" == "running" ]] && report "Container" "LibreChat" "PASS" "running" || report "Container" "LibreChat" "FAIL" "${lcst:-unreachable}"

# 2. THE DB + THE CACHE
pg=$(ssh -o BatchMode=yes -o ConnectTimeout=5 -i ~/.ssh/id_nura_clean root@72.60.163.140 "docker exec paperclip-db psql -U paperclip -d paperclip -t -c 'SELECT count(*) FROM nppes_registry' 2>/dev/null | tr -d ' '" 2>/dev/null)
[[ "$pg" =~ ^[0-9]+$ ]] && report "PostgreSQL" "paperclip-db" "PASS" "NPI-records: $pg" || report "PostgreSQL" "paperclip-db" "FAIL" "query-error"
rd=$(ssh -o BatchMode=yes -o ConnectTimeout=5 -i ~/.ssh/id_nura_clean root@72.61.71.211 "docker exec docsgpt-oss-redis-1 redis-cli ping 2>/dev/null" 2>/dev/null)
[[ "$rd" == "PONG" ]] && report "Redis" "docsgpt-redis" "PASS" "PONG" || report "Redis" "docsgpt-redis" "WARN" "no-pong"

# 3. THE SERVICES
for probe in "brain:http://72.61.71.211:7091/api/health:200" "ollama:http://72.60.163.140:11434/api/tags:200" "thairis:http://72.61.71.211:32790/:200" "ohif:http://72.61.71.211:32791/:200" "librechat:http://72.60.163.140:3080/:200"; do
  IFS=':' read -r name url expect <<< "$probe"
  code=$(curl -s -m 5 -o /dev/null -w "%{http_code}" "$url" 2>/dev/null)
  [[ "$code" == "$expect" ]] && report "Service" "$name" "PASS" "HTTP $code" || report "Service" "$name" "WARN" "HTTP ${code:-000}"
done

# 4. THE MODELS
models=$(ssh -o BatchMode=yes -o ConnectTimeout=5 -i ~/.ssh/id_nura_clean root@72.60.163.140 "curl -s -m 5 http://127.0.0.1:11434/api/tags 2>/dev/null | grep -oE 'gemma4:e4b|glm4:9b|qwen2.5:3b' | sort -u | tr '\n' ' '" 2>/dev/null)
report "Models" "sovereign" "$([[ -n "$models" ]] && echo PASS || echo WARN)" "${models:-none-found}"

# 5. THE DISK + MEM
du=$(ssh -o BatchMode=yes -o ConnectTimeout=5 -i ~/.ssh/id_nura_clean root@72.61.71.211 "df -h / | awk 'NR==2 {print \$5}' | tr -d '%'" 2>/dev/null)
[[ "${du:-100}" -lt 80 ]] && report "Disk" "Clinic" "PASS" "${du}%" || report "Disk" "Clinic" "WARN" "${du}%"

echo -e "${BOLD}=== SUMMARY: $PASSED/$TOTAL passed · $WARNINGS warn · $FAILED fail ===${NC}"
[[ "$FAILED" -eq 0 ]] && echo -e "${GREEN}[✓] OPERATIONAL${NC}" || echo -e "${RED}[✗] ATTENTION: $FAILED FAILED${NC}"
exit $((FAILED > 0 ? 1 : 0))
