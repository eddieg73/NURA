#!/usr/bin/env bash
# Assess the TLS/public-route situation for mcp.nuratech.ai before changing anything.
CFG=/opt/data/profiles/nura/home/.ssh/config
timeout 150 ssh -F "$CFG" -o ConnectTimeout=12 clinic '
  echo "=== certbot present? ==="
  command -v certbot && certbot --version 2>&1 | head -2 || echo "  certbot ABSENT"
  echo ""
  echo "=== existing LE certs on the host ==="
  ls /etc/letsencrypt/live/ 2>/dev/null
  echo ""
  echo "=== mcp.nuratech.ai cert validity ==="
  openssl x509 -in /etc/letsencrypt/live/mcp.nuratech.ai/cert.pem -noout -subject -dates 2>/dev/null
  echo ""
  echo "=== renewal config (how was it issued?) ==="
  cat /etc/letsencrypt/renewal/mcp.nuratech.ai.conf 2>/dev/null | grep -vE "^#" | head -20
  echo ""
  echo "=== renewal timer / cron ==="
  systemctl list-timers 2>/dev/null | grep -i certbot | head -3
  ls /etc/cron.d/ 2>/dev/null | grep -i certbot
  echo ""
  echo "=== who answers :80 (ACME http-01 would need this) ==="
  (ss -ltnp 2>/dev/null || netstat -ltnp 2>/dev/null) | grep -E ":80 " | head -4
  echo ""
  echo "=== radris viewer.conf + radris.conf (to see the cert pattern used) ==="
  docker exec radris-stack-nginx-1 sh -c "cat /etc/nginx/conf.d/radris.conf" 2>/dev/null | head -25
  echo "  ---- viewer.conf ---"
  docker exec radris-stack-nginx-1 sh -c "sed -n 1,25p /etc/nginx/conf.d/viewer.conf" 2>/dev/null
' 2>&1 | head -75