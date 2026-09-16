#!/usr/bin/env bash
# Find the OpenEMR deployment and the public ingress across the NURA fleet.
CFG=/opt/data/profiles/nura/home/.ssh/config
for h in clinic lab edge; do
  echo "════════════════════════════════════════════════════════════"
  echo "  $h"
  echo "════════════════════════════════════════════════════════════"
  timeout 90 ssh -F "$CFG" -o ConnectTimeout=12 "$h" '
    echo "  -- containers matching emr/fhir/db --"
    docker ps --format "{{.Names}}|{{.Status}}|{{.Ports}}" 2>/dev/null | grep -iE "openemr|emr|fhir|medplum|mysql|maria|mirth" | head -10
    echo "  -- total containers --"
    docker ps -q 2>/dev/null | wc -l
    echo "  -- owners of :443 and :80 --"
    (ss -ltnp 2>/dev/null || netstat -ltnp 2>/dev/null) | grep -E ":443|:80 " | head -6
    echo "  -- nginx site names --"
    ls /etc/nginx/sites-enabled/ 2>/dev/null | head -12
    echo "  -- nginx conf.d --"
    ls /etc/nginx/conf.d/ 2>/dev/null | head -12
    echo "  -- certs (domains) --"
    ls /etc/letsencrypt/live/ 2>/dev/null | head -12
  ' 2>&1 | head -45
  echo ""
done