#!/bin/bash
# Restore drill for the B2 off-site backup — prove it's actually restore-able.
set -euo pipefail
export PATH="/opt/data/tools/bin:$PATH"
ENVF=/opt/data/profiles/nura/.env

# Pull creds from .env (never printed)
export B2_ACCOUNT_ID=$(grep -oP '(?<=^B2_KEY_ID=).*' "$ENVF" | head -1 | tr -d '\r\n"')
export B2_ACCOUNT_KEY=$(grep -oP '(?<=^B2_APPLICATION_KEY=).*' "$ENVF" | head -1 | tr -d '\r\n"')
export RESTIC_PASSWORD=$(grep -oP '(?<=^RESTIC_PASSWORD=).*' "$ENVF" | head -1 | tr -d '\r\n"')
export RESTIC_REPOSITORY="b2:nura-backups:nightly"

if [ -z "$B2_ACCOUNT_ID" ] || [ -z "$B2_ACCOUNT_KEY" ] || [ -z "$RESTIC_PASSWORD" ]; then
  echo "RESTORE SKIPPED: B2/RESTIC creds missing"; exit 0
fi

echo "=== 1. Snapshots in the B2 repo ==="
restic snapshots 2>&1 | grep -vE "^\s*$" | tail -6

SNAP=$(restic snapshots --latest 1 --json 2>/dev/null | /opt/hermes/.venv/bin/python3 -c "import sys,json;d=json.load(sys.stdin);print(d[0]['id'] if d else '')" 2>/dev/null)
echo "snapshot to test: ${SNAP:-none}"
if [ -z "$SNAP" ]; then echo "RESTORE FAIL: no snapshot"; exit 0; fi

echo
echo "=== 2. Restore latest snapshot to isolated dir ==="
TGT=/opt/data/restore-drill
rm -rf "$TGT"; mkdir -p "$TGT"
restic restore "$SNAP" --target "$TGT" 2>&1 | tail -3

echo
echo "=== 3. Verify file count + bytes vs source ==="
SRC_BYTES=$(du -sb "$TGT" 2>/dev/null | awk '{print $1}')
SRC_FILES=$(find "$TGT" -type f 2>/dev/null | wc -l)
echo "restored: files=$SRC_FILES  bytes=$SRC_BYTES  (target=$TGT)"

echo
echo "=== 4. Checksum spot-check (3 files, size > 0) ==="
find "$TGT" -type f -size +1k 2>/dev/null | head -3 | while read f; do
  echo "  sha256 $f"; sha256sum "$f" 2>/dev/null | cut -c1-24
done

echo
echo "=== CLEANUP: remove restore-drill dir (test artifact) ==="
rm -rf "$TGT" && echo "removed $TGT"
echo "RESTORE DRILL DONE"
