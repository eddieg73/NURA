#!/usr/bin/env bash
# Does the DEV path (`npm run dev` = tsx watch src/index.ts) actually run?
# I claimed the skipped esbuild postinstall "affects tsx" — that claim was never tested. Test it.
set -u
cd /opt/data/openemr_plugin_review
PORT=18789
export NODE_ENV=development PORT=$PORT
export OPENEMR_FHIR_BASE_URL=http://127.0.0.1:9999/apis/default/fhir
export PATIENT_CONTEXT_HMAC_KEY=0123456789abcdef0123456789abcdef0123456789
export AUTH_MODE=passthrough

echo "═══ RUN THE TYPESCRIPT SOURCE DIRECTLY VIA tsx (no build step) ═══"
./node_modules/.bin/tsx src/index.ts > /tmp/dev.log 2>&1 &
PID=$!
for i in $(seq 1 40); do
  curl -s -m 2 "http://127.0.0.1:$PORT/healthz" >/dev/null 2>&1 && break
  sleep 0.4
done
echo "  log    : $(head -3 /tmp/dev.log)"
echo -n "  healthz: "; curl -s -m 5 -w " (HTTP %{http_code})\n" "http://127.0.0.1:$PORT/healthz"
echo -n "  bind   : "; curl -s -m 5 -o /dev/null -w "loopback HTTP %{http_code}\n" "http://127.0.0.1:$PORT/healthz"

kill $PID 2>/dev/null; wait $PID 2>/dev/null
echo "  stopped"
