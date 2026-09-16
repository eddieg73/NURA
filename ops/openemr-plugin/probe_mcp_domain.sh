#!/usr/bin/env bash
# What does the existing mcp.nuratech.ai vhost actually serve today?
CFG=/opt/data/profiles/nura/home/.ssh/config
echo "════════════════════════════════════════════════════════════"
echo "  nginx: mcp.nuratech.ai site config"
echo "════════════════════════════════════════════════════════════"
timeout 90 ssh -F "$CFG" -o ConnectTimeout=12 clinic '
  cat /etc/nginx/sites-enabled/mcp.nuratech.ai 2>/dev/null
  echo ""
  echo "  ---- cert details ----"
  openssl x509 -in /etc/letsencrypt/live/mcp.nuratech.ai/cert.pem -noout -subject -dates -ext subjectAltName 2>/dev/null
' 2>&1 | head -70
echo ""
echo "════════════════════════════════════════════════════════════"
echo "  public behaviour of mcp.nuratech.ai"
echo "════════════════════════════════════════════════════════════"
echo -n "  DNS: "; getent hosts mcp.nuratech.ai 2>/dev/null | head -1 || echo "(no local DNS)"
echo -n "  https://mcp.nuratech.ai/healthz -> "
curl -s -o /tmp/mh -m 15 -w "HTTP %{http_code}\n" https://mcp.nuratech.ai/healthz 2>&1
echo -n "  https://mcp.nuratech.ai/mcp -> "
curl -s -o /tmp/mm -m 15 -w "HTTP %{http_code}\n" https://mcp.nuratech.ai/mcp 2>&1
echo "  body(/healthz): $(head -c 200 /tmp/mh 2>/dev/null | tr -d '\n')"
echo "  body(/mcp)    : $(head -c 200 /tmp/mm 2>/dev/null | tr -d '\n')"
echo ""
echo "  TLS cert as served:"
echo | timeout 20 openssl s_client -connect mcp.nuratech.ai:443 -servername mcp.nuratech.ai 2>/dev/null \
  | openssl x509 -noout -subject -issuer -dates 2>/dev/null | sed 's/^/    /'