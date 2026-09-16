#!/usr/bin/env bash
# End-to-end verification of the NURA OpenEMR MCP plugin — env vars, not a .env file.
# FINDING: the app does NOT load .env (no dotenv import; loadConfig reads process.env directly),
# despite the README instructing "Copy .env.example to .env". Node's --env-file is not used in the
# Dockerfile either. So config MUST come from the process environment.
set -u
D=/opt/data/openemr_plugin_review
PORT=18787
cd "$D"

export NODE_ENV=development
export PORT=$PORT
export OPENEMR_FHIR_BASE_URL=http://127.0.0.1:9999/apis/default/fhir
export PATIENT_CONTEXT_HMAC_KEY=0123456789abcdef0123456789abcdef0123456789
export PATIENT_CONTEXT_TTL_SECONDS=900
export FHIR_TIMEOUT_MS=10000
export MAX_BUNDLE_ENTRIES=50
export TRUST_PROXY=false
export AUTH_MODE=passthrough

echo "═══ 1. START ═══"
node dist/src/index.js > /tmp/oemr_mcp.log 2>&1 &
SRV=$!
for i in $(seq 1 40); do
  curl -s -m 2 "http://127.0.0.1:$PORT/healthz" >/dev/null 2>&1 && break
  sleep 0.4
done
echo "  pid $SRV"
echo "  log: $(cat /tmp/oemr_mcp.log)"

echo ""
echo "═══ 2. /healthz ═══"
curl -s -m 5 -w "\n    HTTP %{http_code}\n" "http://127.0.0.1:$PORT/healthz" | sed 's/^/  /'

echo ""
echo "═══ 3. SECURITY HEADERS (declared in code — now proven live) ═══"
curl -s -m 5 -D - -o /dev/null "http://127.0.0.1:$PORT/healthz" \
  | grep -iE 'cache-control|pragma|x-content-type|referrer-policy|content-security|x-powered' | sed 's/^/  /'

echo ""
echo "═══ 4. AUTH ENFORCEMENT ═══"
echo -n "  POST /mcp with NO auth            -> "
curl -s -m 5 -o /tmp/r1 -w "HTTP %{http_code}" -X POST "http://127.0.0.1:$PORT/mcp" \
  -H 'content-type: application/json' -d '{"jsonrpc":"2.0","id":1,"method":"tools/list"}' 2>/dev/null
echo "  | $(head -c 160 /tmp/r1 2>/dev/null | tr -d '\n')"
echo -n "  POST /mcp with dummy bearer       -> "
curl -s -m 10 -o /tmp/r2 -w "HTTP %{http_code}" -X POST "http://127.0.0.1:$PORT/mcp" \
  -H 'content-type: application/json' -H 'authorization: Bearer dummy-dev-token' \
  -H 'accept: application/json, text/event-stream' \
  -d '{"jsonrpc":"2.0","id":1,"method":"tools/list"}' 2>/dev/null
echo "  | $(head -c 400 /tmp/r2 2>/dev/null | tr -d '\n')"

echo ""
echo "═══ 5. METHOD RESTRICTIONS ═══"
for m in GET DELETE; do
  echo -n "  $m /mcp -> "
  curl -s -m 5 -o /tmp/rm -w "HTTP %{http_code}" -X "$m" "http://127.0.0.1:$PORT/mcp"
  echo " | $(head -c 90 /tmp/rm 2>/dev/null | tr -d '\n')"
done

echo ""
echo "═══ 6. BIND ADDRESS (code says 0.0.0.0) ═══"
(ss -ltn 2>/dev/null || netstat -ltn 2>/dev/null) | grep -E "[:.]$PORT" | sed 's/^/  /'

echo ""
echo "═══ 7. REACHABLE OFF-LOOPBACK? ═══"
HOSTIP=$(hostname -I 2>/dev/null | awk '{print $1}')
echo "  host ip: ${HOSTIP:-none}"
[ -n "$HOSTIP" ] && echo -n "  http://$HOSTIP:$PORT/healthz -> " && \
  curl -s -m 5 -o /dev/null -w "HTTP %{http_code}\n" "http://$HOSTIP:$PORT/healthz"

echo ""
echo "═══ 8. FAIL-CLOSED: does NODE_ENV=production refuse passthrough? ═══"
NODE_ENV=production AUTH_MODE=passthrough UPSTREAM_AUTH_MODE=forward \
  node -e 'import("./dist/src/config.js").then(m=>{try{m.loadConfig();console.log("  ** DID NOT FAIL — passthrough allowed in production")}catch(e){console.log("  refused:",e.message)}}).catch(e=>console.log("  err",e.message))'

echo ""
echo "═══ 9. SHUTDOWN ═══"
kill $SRV 2>/dev/null; sleep 1; kill -9 $SRV 2>/dev/null
echo "  stopped"
