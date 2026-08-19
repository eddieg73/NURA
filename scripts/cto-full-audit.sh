#!/bin/bash
# CTO FULL AUDIT — servers + software + dockers (2026-08-05)
echo "############################################################"
echo "# NURA CTO AUDIT — $(date -u +%Y-%m-%dT%H:%MZ)"
echo "############################################################"
for NODE in "72.61.71.211:clinic" "72.60.163.140:lab" "195.35.32.113:edge"; do
  H="${NODE%%:*}"; NAME="${NODE##*:}"
  echo ""
  echo "==================== $NAME ($H) ===================="
  ssh -o BatchMode=yes -o ConnectTimeout=8 -i ~/.ssh/id_nura_clean root@$H '
    echo "--- resources ---"
    uptime | sed "s/^ *//"
    free -m | awk "NR==2{print \"mem: \"\$3\"/\"\$2\" MB used\"}"
    df -h / | awk "NR==2{print \"disk: \"\$5\" used, \"\$4\" free\"}"
    swapon --show 2>/dev/null | tail -1 || echo "no swap"
    echo "--- docker ---"
    docker ps -a --format "{{.Names}} | {{.Status}} | {{.Ports}}" 2>/dev/null | head -40
    echo "--- docker resource use ---"
    docker stats --no-stream --format "{{.Name}} cpu={{.CPUPerc}} mem={{.MemUsage}}" 2>/dev/null | sort -t= -k2 -rn | head -5
    echo "--- SSH config ---"
    grep -E "^PermitRootLogin|^PasswordAuthentication|^PubkeyAuthentication" /etc/ssh/sshd_config 2>/dev/null | head -4
    echo "--- exposed listeners (non-ssh) ---"
    ss -tlnp 2>/dev/null | awk "NR>1{print \$4}" | grep -vE ":22$|127.0.0.1|::1" | sort -u | head -20
    echo "--- key services ---"
    systemctl is-active docker ssh fail2ban 2>/dev/null | head -4
  ' 2>&1 | head -80
done
echo ""
echo "==================== APP-LEVEL CHECKS ===================="
echo "--- Hermes gateway ---"
ssh -o BatchMode=yes -o ConnectTimeout=8 -i ~/.ssh/id_nura_clean root@72.61.71.211 "docker ps --format '{{.Names}} {{.Status}}' | grep -E 'hermes-gateway|hermes-dashboard'; docker exec hermes-gateway sh -c \"grep -i ':21C2' /proc/net/tcp | awk '{print \\\$2}' | head -1\" 2>/dev/null" 2>&1 | head -3
echo "--- Redis ---"
ssh -o BatchMode=yes -o ConnectTimeout=8 -i ~/.ssh/id_nura_clean root@72.61.71.211 "docker exec redis-gc8b-redis-1 redis-cli ping 2>/dev/null | head -1" 2>&1 | head -1
echo "--- Qdrant ---"
curl -s -m 5 http://72.61.71.211:32769/healthz 2>/dev/null | head -c 60; echo
echo "--- OpenEMR ---"
curl -s -m 6 -o /dev/null -w "openemr:32776 -> %{http_code}\n" http://72.61.71.211:32776/ 2>/dev/null | head -1
echo "--- Orthanc ---"
curl -s -m 5 -o /dev/null -w "orthanc:8042 -> %{http_code}\n" http://72.61.71.211:8042/ 2>/dev/null | head -1
echo "--- Mirth ---"
curl -s -m 5 -o /dev/null -w "mirth:8444 -> %{http_code}\n" http://72.61.71.211:8444/ 2>/dev/null | head -1
echo "--- Mattermost ---"
curl -s -m 5 -o /dev/null -w "mattermost:32777 -> %{http_code}\n" http://72.61.71.211:32777/ 2>/dev/null | head -1
echo "--- Chatwoot ---"
curl -s -m 5 -o /dev/null -w "chatwoot:3000 -> %{http_code}\n" http://72.61.71.211:3000/ 2>/dev/null | head -1
echo "--- ThaiRIS ---"
curl -s -m 5 -o /dev/null -w "thairis:32790 -> %{http_code}\n" http://72.61.71.211:32790/ 2>/dev/null | head -1
echo "--- OHIF ---"
curl -s -m 5 -o /dev/null -w "ohif:32791 -> %{http_code}\n" http://72.61.71.211:32791/ 2>/dev/null | head -1
echo "--- NPM ---"
curl -s -m 5 -o /dev/null -w "npm:8181 -> %{http_code}\n" http://72.61.71.211:8181/ 2>/dev/null | head -1
echo "--- public doors ---"
for D in api.nuratech.ai ris.nuratech.ai pacs.nuratech.ai; do curl -s -m 6 -o /dev/null -w "$D -> %{http_code}\n" http://$D/ 2>/dev/null | head -1; done
echo ""
echo "=== AUDIT COMPLETE ==="
