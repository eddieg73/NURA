#!/usr/bin/env bash
# Deploy the NURA OpenEMR MCP plugin on clinic (/docker/nura-openemr-mcp).
# Loopback-bound (the bind fix), synthetic FHIR target, NO PHI.
set -eu
CFG=/opt/data/profiles/nura/home/.ssh/config
ZIP=/opt/data/NURA/ops/openemr-plugin/NURA_OpenEMR_Plugin_v0.2.1-patched.zip
DEST=/docker/nura-openemr-mcp

echo "═══ 1. TRANSFER ═══"
timeout 120 ssh -F "$CFG" clinic "mkdir -p $DEST" 2>&1
timeout 300 scp -F "$CFG" -o ConnectTimeout=15 "$ZIP" "clinic:$DEST/plugin.zip" 2>&1 | tail -2
echo "  transferred: $(ssh -F "$CFG" clinic "ls -la $DEST/plugin.zip" 2>/dev/null)"

echo ""
echo "═══ 2. EXTRACT + BUILD ═══"
timeout 590 ssh -F "$CFG" clinic "
  set -e
  cd $DEST
  if [ ! -f package.json ]; then
    command -v unzip >/dev/null || (apt-get update -qq && apt-get install -y -qq unzip) >/dev/null 2>&1
    unzip -oq plugin.zip
  fi
  echo '  files:'; ls | head -20
  echo ''
  echo '  version:'; grep -m1 '\"version\"' package.json
  echo ''
  echo '  building image...'
  docker build -q -t nura-openemr-mcp:0.2.1 . 2>&1 | tail -8
  echo ''
  echo '  image:'; docker images nura-openemr-mcp --format '{{.Repository}}:{{.Tag}} {{.Size}}'
" 2>&1 | tail -30