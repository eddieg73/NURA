#!/usr/bin/env bash
# Clean-room verification of the REPACKAGED deliverable.
# Extract the patched zip into a fresh dir, install, build, test — proves the artifact stands alone.
set -u
Z=/opt/data/NURA/ops/openemr-plugin/NURA_OpenEMR_Plugin_v0.2.1-patched.zip
C=/tmp/cleanroom_openemr
rm -rf "$C"; mkdir -p "$C"

echo "═══ EXTRACT ═══"
/opt/hermes/.venv/bin/python3 - "$Z" "$C" <<'PY'
import sys, zipfile
z = zipfile.ZipFile(sys.argv[1])
assert z.testzip() is None, "zip corrupt"
z.extractall(sys.argv[2])
print(f"  entries: {len(z.namelist())}  CRC ok")
PY

echo ""
echo "═══ NO SECRETS / NO BUILD ARTIFACTS SHIPPED ═══"
for bad in node_modules dist .env; do
  found=$(find "$C" -name "$bad" 2>/dev/null | head -1)
  echo "  $bad: ${found:-absent -- OK}"
done
echo -n "  version in package.json: "
/opt/hermes/.venv/bin/python3 -c "import json;print(json.load(open('$C/package.json'))['version'])"

echo ""
echo "═══ INSTALL ═══"
cd "$C"
npm ci --no-audit --no-fund 2>&1 | tail -3 | sed 's/^/  /'

echo ""
echo "═══ BUILD ═══"
npx tsc -p tsconfig.json 2>&1 | tail -5
echo "  tsc exit: $?"

echo ""
echo "═══ TEST ═══"
node --test dist/test/*.test.js 2>&1 | grep -E '^(ℹ|✔|✖)' | tail -12

echo ""
echo "═══ THE FIX IS PRESENT IN THE SHIPPED SOURCE ═══"
grep -n "bindHost" "$C/src/config.ts" | sed 's/^/  config.ts:/'
grep -n "bindHost" "$C/src/index.ts" | sed 's/^/  index.ts:/'
grep -n "BIND_HOST" "$C/.env.example" | sed 's/^/  .env.example:/'
echo -n "  '0.0.0.0' still in source? "
if grep -rn '0\.0\.0\.0' "$C/src/" 2>/dev/null | grep -v '^\s*//' | grep -q .; then
  echo "YES:"; grep -rn '0\.0\.0\.0' "$C/src/" | sed 's/^/    /'
else
  echo "no -- only in comments/tests"
fi
