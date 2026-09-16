#!/usr/bin/env bash
# Fix MCP_RESOURCE_URL: the discovery doc was advertising an internal loopback address.
# A public MCP client (ChatGPT) needs the public resource identifier, and OAuth audience binding
# against a 127.0.0.1 resource URL would be meaningless for a remote client.
#
# OAUTH_ISSUER / OAUTH_JWKS_URL stay internal FOR NOW: OpenEMR's authorization server is disabled, and
# exposing it publicly is part of the gated work. They must become public HTTPS before ChatGPT can
# complete an authorization-code flow.
set -eu
CFG=/opt/data/profiles/nura/home/.ssh/config
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
    -e MCP_RESOURCE_URL=https://mcp.nuratech.ai \
    -e OAUTH_ISSUER=http://127.0.0.1:32777/apis/default/fhir \
    -e OAUTH_AUDIENCE=https://mcp.nuratech.ai \
    -e OAUTH_JWKS_URL=http://127.0.0.1:32777/oauth2/default/jwk \
    -e OAUTH_REQUIRED_SCOPES=ehr.read \
    -e UPSTREAM_AUTH_MODE=forward \
    nura-openemr-mcp:0.2.1 >/dev/null 2>&1
  sleep 4
  echo "  state: $(docker ps --filter name=nura-openemr-mcp --format "{{.Status}}")"
'
echo ""
echo "  discovery doc now advertises:"
curl -s -m 20 https://mcp.nuratech.ai/.well-known/oauth-protected-resource 2>/dev/null \
  | /opt/hermes/.venv/bin/python3 -m json.tool 2>/dev/null | sed 's/^/    /'
echo ""
echo "  re-verify public route:"
for spec in "GET /healthz" "GET /mcp"; do
  set -- $spec
  echo -n "    $1 $2 -> "; curl -s -o /dev/null -m 20 -w "HTTP %{http_code}\n" -X $1 "https://mcp.nuratech.ai$2" 2>&1
done
echo -n "    POST /mcp (no token) -> "
curl -s -m 20 -o /dev/null -w "HTTP %{http_code}\n" -X POST https://mcp.nuratech.ai/mcp \
  -H 'content-type: application/json' -d '{}' 2>&1