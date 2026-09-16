#!/usr/bin/env bash
# Run the plugin on clinic, loopback-bound, synthetic FHIR target. NO PHI.
set -eu
CFG=/opt/data/profiles/nura/home/.ssh/config
DEST=/docker/nura-openemr-mcp
PORT=8787

echo "═══ free-port check ═══"
ssh -F "$CFG" clinic "(ss -ltn 2>/dev/null || netstat -ltn 2>/dev/null) | grep -c ':8787' || echo '0 (port free)'"

echo ""
echo "═══ launch container (bind 127.0.0.1 ONLY, synthetic upstream) ═══"
ssh -F "$CFG" clinic "
  docker rm -f nura-openemr-mcp >/dev/null 2>&1 || true
  # NOTE: synthetic, deliberately-dead upstream. NO PHI, no real OpenEMR.
  # AUTH_MODE=passthrough is used ONLY because it is loopback-bound and NOT publicly routed.
  # Production requires AUTH_MODE=jwt + token_exchange, which the fail-closed config enforces.
  docker run -d --name nura-openemr-mcp --restart unless-stopped \
    -p 127.0.0.1:$PORT:8787 \
    -e NODE_ENV=development \
    -e PORT=8787 \
    -e BIND_HOST=0.0.0.0 \
    -e OPENEMR_FHIR_BASE_URL=http://127.0.0.1:9/apis/default/fhir \
    -e PATIENT_CONTEXT_HMAC_KEY=\$(head -c 48 /dev/urandom | base64 | tr -d '=+/' | head -c 48) \
    -e AUTH_MODE=passthrough \
    -e UPSTREAM_AUTH_MODE=forward \
    nura-openemr-mcp:0.2.1 2>&1 | tail -2
  sleep 3
  echo ''
  echo '  -- state --'
  docker ps --filter name=nura-openemr-mcp --format '{{.Names}}|{{.Status}}|{{.Ports}}'
  echo ''
  echo '  -- logs --'
  docker logs nura-openemr-mcp 2>&1 | tail -6
  echo ''
  echo '  -- published bind (must be 127.0.0.1, NOT 0.0.0.0) --'
  docker port nura-openemr-mcp 2>/dev/null
" 2>&1 | tail -25

echo ""
echo "═══ VERIFY FROM THIS HOST (over SSH tunnel to loopback) ═══"
ssh -F "$CFG" clinic "
  echo -n '  /healthz : '; curl -s -m 8 -w ' (HTTP %{http_code})\n' http://127.0.0.1:$PORT/healthz
  echo -n '  /mcp noauth: '; curl -s -m 8 -o /tmp/n -w 'HTTP %{http_code}\n' -X POST http://127.0.0.1:$PORT/mcp \
     -H 'content-type: application/json' -d '{\"jsonrpc\":\"2.0\",\"id\":1,\"method\":\"tools/list\"}'
  head -c 150 /tmp/n | sed 's/^/       /'
  echo ''
  echo -n '  /mcp withdummy: '; curl -s -m 10 -o /tmp/t -w 'HTTP %{http_code}\n' -X POST http://127.0.0.1:$PORT/mcp \
     -H 'content-type: application/json' -H 'authorization: Bearer synthetic-dev-token' \
     -H 'accept: application/json, text/event-stream' \
     -d '{\"jsonrpc\":\"2.0\",\"id\":1,\"method\":\"tools/list\"}'
  head -c 260 /tmp/t | sed 's/^/       /'
  echo ''
  echo -n '  external reachability (should FAIL): '
  curl -s -o /dev/null -m 6 -w 'HTTP %{http_code}\n' http://72.61.71.211:$PORT/healthz || echo 'refused'
" 2>&1 | tail -20