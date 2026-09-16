#!/usr/bin/env bash
# Complete the public route for mcp.nuratech.ai.
#
# DESIGN DECISION: the plugin runs in AUTH_MODE=jwt pointed at OpenEMR's advertised OAuth endpoints.
# OpenEMR's authorization server is currently DISABLED, so the JWKS fetch fails and EVERY request is
# rejected 401. That is deliberate: the route is live and TLS-correct, but nothing is reachable until
# real auth exists. Exposing the passthrough verifier publicly would recreate the exact
# "wide bind + any token accepted" defect identified in this plugin's own review.
set -eu
CFG=/opt/data/profiles/nura/home/.ssh/config

echo "═══ 1. REDEPLOY PLUGIN, fail-closed (jwt), host network so it can reach OpenEMR loopback ═══"
timeout 300 ssh -F "$CFG" clinic '
  docker rm -f nura-openemr-mcp >/dev/null 2>&1 || true
  HMAC=$(head -c 48 /dev/urandom | base64 | tr -d "=+/" | head -c 48)
  docker run -d --name nura-openemr-mcp --restart unless-stopped --network host \
    -e NODE_ENV=development \
    -e PORT=8787 \
    -e BIND_HOST=127.0.0.1 \
    -e OPENEMR_FHIR_BASE_URL=http://127.0.0.1:32777/apis/default/fhir \
    -e PATIENT_CONTEXT_HMAC_KEY="$HMAC" \
    -e AUTH_MODE=jwt \
    -e MCP_RESOURCE_URL=http://127.0.0.1:8787 \
    -e OAUTH_ISSUER=http://127.0.0.1:32777/apis/default/fhir \
    -e OAUTH_AUDIENCE=http://127.0.0.1:8787 \
    -e OAUTH_JWKS_URL=http://127.0.0.1:32777/oauth2/default/jwk \
    -e OAUTH_REQUIRED_SCOPES=ehr.read \
    -e UPSTREAM_AUTH_MODE=forward \
    nura-openemr-mcp:0.2.1 >/dev/null 2>&1
  sleep 4
  echo "  -- state --"
  docker ps --filter name=nura-openemr-mcp --format "{{.Names}}|{{.Status}}"
  echo "  -- logs --"
  docker logs nura-openemr-mcp 2>&1 | tail -4
  echo "  -- binding (host network + BIND_HOST=127.0.0.1) --"
  (ss -ltn 2>/dev/null) | grep ":8787" | head -3
'

echo ""
echo "═══ 2. VERIFY fail-closed BEHAVIOUR ═══"
timeout 120 ssh -F "$CFG" clinic '
  echo -n "  /healthz            : "; curl -s -m 8 -w " (HTTP %{http_code})\n" http://127.0.0.1:8787/healthz
  echo -n "  POST /mcp no token  : "; curl -s -m 8 -o /dev/null -w "HTTP %{http_code}\n" -X POST http://127.0.0.1:8787/mcp -H "content-type: application/json" -d "{}"
  echo -n "  POST /mcp w/ token  : "; curl -s -m 10 -o /tmp/f -w "HTTP %{http_code}\n" -X POST http://127.0.0.1:8787/mcp -H "content-type: application/json" -H "authorization: Bearer anything" -H "accept: application/json, text/event-stream" -d "{\"jsonrpc\":\"2.0\",\"id\":1,\"method\":\"tools/list\"}"
  echo "     body: $(head -c 180 /tmp/f | tr -d "\n")"
  echo -n "  external 72.61.71.211:8787 : "; curl -s -o /dev/null -m 6 -w "HTTP %{http_code}\n" http://72.61.71.211:8787/healthz 2>/dev/null || echo "refused (correct)"
'

echo ""
echo "═══ 3. INSTALL CERT + VHOST INTO radris-stack-nginx-1 (the real :443 owner) ═══"
timeout 300 ssh -F "$CFG" clinic '
  cp /etc/letsencrypt/live/mcp.nuratech.ai/fullchain.pem /docker/radris-stack/nginx/certs/mcp.nuratech.ai.crt
  cp /etc/letsencrypt/live/mcp.nuratech.ai/privkey.pem  /docker/radris-stack/nginx/certs/mcp.nuratech.ai.key
  chmod 644 /docker/radris-stack/nginx/certs/mcp.nuratech.ai.crt
  chmod 600 /docker/radris-stack/nginx/certs/mcp.nuratech.ai.key
  cat > /docker/radris-stack/nginx/conf.d/mcp.conf <<EOF
server {
    listen 443 ssl;
    server_name mcp.nuratech.ai;

    ssl_certificate     /etc/nginx/certs/mcp.nuratech.ai.crt;
    ssl_certificate_key /etc/nginx/certs/mcp.nuratech.ai.key;

    client_max_body_size 1m;

    location / {
        proxy_pass http://host.docker.internal:8787;
        proxy_http_version 1.1;
        proxy_set_header Host \$host;
        proxy_set_header X-Real-IP \$remote_addr;
        proxy_set_header X-Forwarded-For \$proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto \$scheme;
    }
}
EOF
  echo "  vhost written:"
  cat /docker/radris-stack/nginx/conf.d/mcp.conf | head -8 | sed "s/^/    /"
  echo ""
  echo "  config test:"
  docker exec radris-stack-nginx-1 nginx -t 2>&1 | tail -4 | sed "s/^/    /"
  echo "  reload:"
  docker exec radris-stack-nginx-1 nginx -s reload 2>&1 | tail -2 | sed "s/^/    /"
  echo "    (exit $?)"
'