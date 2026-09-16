#!/usr/bin/env bash
# Fix the 502: nginx reaches the plugin via host.docker.internal = 172.17.0.1 (docker bridge gateway).
# The plugin was bound to 127.0.0.1, so the bridge could not reach it (connection refused).
#
# Bind instead to the DOCKER BRIDGE GATEWAY (172.17.0.1):
#   - reachable from containers (and the host)  -> nginx proxy works
#   - NOT reachable from the public interface   -> 172.17.0.1 is a private bridge address
#   - plugin keeps --network host so it can still reach OpenEMR on 127.0.0.1:32777,
#     which config.ts REQUIRES (it rejects non-HTTPS unless the host is localhost)
set -eu
CFG=/opt/data/profiles/nura/home/.ssh/config

echo "═══ confirm the gateway address ═══"
timeout 90 ssh -F "$CFG" clinic 'ip -4 addr show docker0 2>/dev/null | grep -oE "inet [0-9.]+" | head -1'

echo ""
echo "═══ rebind plugin to the bridge gateway ═══"
timeout 300 ssh -F "$CFG" clinic '
  docker rm -f nura-openemr-mcp >/dev/null 2>&1 || true
  HMAC=$(head -c 48 /dev/urandom | base64 | tr -d "=+/" | head -c 48)
  docker run -d --name nura-openemr-mcp --restart unless-stopped --network host \
    -e NODE_ENV=development \
    -e PORT=8787 \
    -e BIND_HOST=172.17.0.1 \
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
  echo "  state: $(docker ps --filter name=nura-openemr-mcp --format "{{.Status}}")"
  echo "  log  : $(docker logs nura-openemr-mcp 2>&1 | tail -1)"
  echo "  bind :"; (ss -ltn 2>/dev/null) | grep ":8787" | sed "s/^/    /"
'

echo ""
echo "═══ container -> plugin reachability ═══"
timeout 120 ssh -F "$CFG" clinic '
  echo -n "  radris -> 172.17.0.1:8787 : "
  docker exec radris-stack-nginx-1 sh -c "curl -s -o /dev/null -m 6 -w \"HTTP %{http_code}\n\" http://host.docker.internal:8787/healthz" 2>&1
  echo -n "  host   -> 127.0.0.1:8787   : "
  curl -s -o /dev/null -m 6 -w "HTTP %{http_code}\n" http://127.0.0.1:8787/healthz 2>&1
  echo -n "  public -> 72.61.71.211:8787: "
  curl -s -o /dev/null -m 6 -w "HTTP %{http_code}\n" http://72.61.71.211:8787/healthz 2>&1 || echo "refused (good)"
'