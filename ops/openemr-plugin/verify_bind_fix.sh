#!/usr/bin/env bash
# Prove the bind fix: default = loopback only; explicit BIND_HOST=0.0.0.0 = deliberate exposure.
set -u
cd /opt/data/openemr_plugin_review
PORT=18788
export NODE_ENV=development PORT=$PORT
export OPENEMR_FHIR_BASE_URL=http://127.0.0.1:9999/apis/default/fhir
export PATIENT_CONTEXT_HMAC_KEY=0123456789abcdef0123456789abcdef0123456789
export AUTH_MODE=passthrough
HOSTIP=$(hostname -I 2>/dev/null | awk '{print $1}')
echo "  host LAN ip: $HOSTIP"

run_case () {
  local label="$1"; local bind="$2"
  echo ""
  echo "── $label ──"
  if [ -n "$bind" ]; then export BIND_HOST="$bind"; else unset BIND_HOST; fi
  node dist/src/index.js > /tmp/bind.log 2>&1 &
  local pid=$!
  for i in $(seq 1 40); do curl -s -m 2 "http://127.0.0.1:$PORT/healthz" >/dev/null 2>&1 && break; sleep 0.4; done
  echo "  startup : $(cat /tmp/bind.log)"
  echo -n "  loopback: "; curl -s -m 5 -o /dev/null -w "HTTP %{http_code}\n" "http://127.0.0.1:$PORT/healthz"
  echo -n "  LAN     : "; curl -s -m 5 -o /dev/null -w "HTTP %{http_code}\n" "http://$HOSTIP:$PORT/healthz" 2>/dev/null || echo "REFUSED"
  kill $pid 2>/dev/null; wait $pid 2>/dev/null
}

echo ""
echo "════════════════════════════════════════════════════════"
echo "  CASE 1 — DEFAULT (no BIND_HOST set)"
echo "════════════════════════════════════════════════════════"
run_case "default" ""

echo ""
echo "════════════════════════════════════════════════════════"
echo "  CASE 2 — EXPLICIT BIND_HOST=0.0.0.0"
echo "════════════════════════════════════════════════════════"
run_case "explicit 0.0.0.0" "0.0.0.0"

echo ""
echo "════════════════════════════════════════════════════════"
echo "  CASE 3 — MALFORMED BIND_HOST (must fail closed)"
echo "════════════════════════════════════════════════════════"
export BIND_HOST="127.0.0.1; rm -rf /tmp/nope"
node dist/src/index.js 2>&1 | head -3 | sed 's/^/  /'
