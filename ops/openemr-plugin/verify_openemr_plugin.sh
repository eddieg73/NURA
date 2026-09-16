#!/usr/bin/env bash
# End-to-end verification of the NURA OpenEMR MCP plugin.
# Starts the real built server, probes the real endpoints, records raw evidence.
set -u
D=/opt/data/openemr_plugin_review
PORT=18787

cd "$D"

# --- synthetic local config (no real PHI, no real endpoints) --------------
cat > .env <<'EOF'
NODE_ENV=development
PORT=18787
OPENEMR_FHIR_BASE_URL=http://127.0.0.1:9999/apis/default/fhir
PATIENT_CONTEXT_HMAC_KEY=0123456789abcdef0123456789abcdef0123456789
PATIENT_CONTEXT_TTL_SECONDS=900
FHIR_TIMEOUT_MS=10000
MAX_BUNDLE_ENTRIES=50
TRUST_PROXY=false
AUTH_MODE=passthrough
EOF

echo "═══ 1. START THE SERVER ═══"
node dist/src/index.js > /tmp/oemr_mcp.log 2>&1 &
SRV=$!
echo "  pid $SRV"

for i in $(seq 1 30); do
  if curl -s -m 2 "http://127.0.0.1:$PORT/healthz" >/dev/null 2>&1; then break; fi
  sleep 0.4
done

echo ""
echo "  startup log:"
sed 's/^/    /' /tmp/oemr_mcp.log

echo ""
echo "═══ 2. /healthz ═══"
curl -s -m 5 -w "\n    HTTP %{http_code}\n" "http://127.0.0.1:$PORT/healthz" | sed 's/^/  /'

echo ""
echo "═══ 3. SECURITY HEADERS ═══"
curl -s -m 5 -D - -o /dev/null "http://127.0.0.1:$PORT/healthz" \
  | grep -iE 'cache-control|pragma|x-content-type|referrer|content-security|x-powered' | sed 's/^/  /'

echo ""
echo "═══ 4. AUTH ENFORCEMENT on POST /mcp ═══"
echo -n "  no Authorization header  -> "
curl -s -m 5 -o /tmp/r1 -w "HTTP %{http_code}" -X POST "http://127.0.0.1:$PORT/mcp" \
  -H 'content-type: application/json' -d '{"jsonrpc":"2.0","id":1,"method":"tools/list"}'
echo "  body: $(head -c 200 /tmp/r1 | tr -d '\n')"

echo -n "  with dummy bearer (passthrough mode) -> "
curl -s -m 8 -o /tmp/r2 -w "HTTP %{http_code}" -X POST "http://127.0.0.1:$PORT/mcp" \
  -H 'content-type: application/json' -H 'authorization: Bearer dummy-dev-token' \
  -H 'accept: application/json, text/event-stream' \
  -d '{"jsonrpc":"2.0","id":1,"method":"tools/list"}'
echo "  body: $(head -c 300 /tmp/r2 | tr -d '\n')"

echo ""
echo "═══ 5. METHOD RESTRICTIONS ═══"
for m in GET DELETE; do
  echo -n "  $m /mcp -> "
  curl -s -m 5 -o /dev/null -w "HTTP %{http_code}" -X "$m" "http://127.0.0.1:$PORT/mcp"
  echo ""
done

echo ""
echo "═══ 6. WHAT INTERFACES IS IT BOUND TO? ═══"
(ss -ltnp 2>/dev/null || netstat -ltnp 2>/dev/null) | grep -E "$PORT" | sed 's/^/  /'

echo ""
echo "═══ 7. IS IT REACHABLE ON A NON-LOOPBACK ADDRESS? ═══"
HOSTIP=$(hostname -I 2>/dev/null | awk '{print $1}')
echo "  host ip: ${HOSTIP:-none}"
if [ -n "$HOSTIP" ]; then
  echo -n "  http://$HOSTIP:$PORT/healthz -> "
  curl -s -m 5 -o /dev/null -w "HTTP %{http_code}\n" "http://$HOSTIP:$PORT/healthz" || echo "unreachable"
fi

echo ""
echo "═══ 8. SHUTDOWN ═══"
kill $SRV 2>/dev/null
sleep 1
kill -9 $SRV 2>/dev/null
echo "  server stopped"
