#!/usr/bin/env bash
# aime_connectivity_check.sh — full-chain connectivity check for the AIME radiology loop.
# Run on the VPS. Exit 0 if everything is up; prints per-link status.
set -uo pipefail
FAIL=0
check() { # name, expected, actual
  if [ "$2" = "$3" ]; then echo "OK   $1 ($3)"; else echo "FAIL $1 (expected $2, got $3)"; FAIL=1; fi
}

echo "== AIME chain connectivity =="
# 1. Docker + containers
docker ps --format '{{.Names}} {{.Status}}' 2>/dev/null | grep -E "mirth|thairis|orthanc|ohif" | sed 's/^/     /' || { echo "FAIL docker ps (daemon?)"; FAIL=1; }

# 2. Mirth REST API
code=$(curl -k -s -o /dev/null -w "%{http_code}" -u "${MIRTH_ADMIN_USER:-admin}:${MIRTH_ADMIN_PASS:-}" -m 5 "${MIRTH_API_URL:-https://127.0.0.1:8443/api}/server/version" 2>/dev/null)
check "Mirth API auth" "200" "$code"

# 3. Mirth channel listeners (6001 ADT, 6002 ORM)
for p in 6001 6002; do
  (echo > /dev/tcp/127.0.0.1/$p) >/dev/null 2>&1 && echo "OK   MLLP :$p listening" || { echo "FAIL MLLP :$p not listening"; FAIL=1; }
done

# 4. ThaiRIS web
code=$(curl -s -o /dev/null -w "%{http_code}" -m 5 http://127.0.0.1:8085/ 2>/dev/null)
check "ThaiRIS web :8085" "200" "$code"

# 5. ThaiRIS MLLP listeners (6001/6002 destinations)
for p in 6001 6002; do
  docker exec thairis sh -c "(echo > /dev/tcp/127.0.0.1/$p) >/dev/null 2>&1" 2>/dev/null \
    && echo "OK   thairis :$p accepting" || { echo "FAIL thairis :$p not accepting (enable RIS HL7 listener)"; FAIL=1; }
done

# 6. NPM domains
for d in ris.nuratech.ai mirth.nuratech.ai pacs.nuratech.ai viewer.nuratech.ai; do
  code=$(curl -sk -o /dev/null -w "%{http_code}" -m 8 "https://$d/" 2>/dev/null)
  [ "$code" = "000" ] && echo "WARN $d unreachable (DNS/SSL not ready yet)" || echo "OK   $d -> $code"
done

# 7. OpenEMR hl7_out drop dir
if docker exec openemr sh -c "[ -d /opt/openemr/hl7_out ]" 2>/dev/null; then
  echo "OK   openemr hl7_out exists"
else
  echo "WARN openemr /opt/openemr/hl7_out not found (container name/path differs?)"
fi

[ "$FAIL" = "0" ] && echo "ALL CHECKS PASSED" || echo "FAILURES PRESENT — see above"
exit $FAIL
