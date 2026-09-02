#!/bin/bash
# Verify the B2 nura-backups bucket is populated with the restic repo
export HOME=/opt/data/profiles/nura/home
ENVF=/opt/data/profiles/nura/.env
export B2_APPLICATION_KEY_ID=$(grep -oP '(?<=^B2_KEY_ID=).*' "$ENVF" | head -1 | tr -d '\r\n"')
export B2_APPLICATION_KEY=$(grep -oP '(?<=^B2_APPLICATION_KEY=).*' "$ENVF" | head -1 | tr -d '\r\n"')

echo "=== B2 nura-backups bucket (--json, raw) ==="
/opt/data/pdf-venv/bin/b2 ls -r --json b2://nura-backups 2>&1 | head -c 900
echo
echo "=== file count via plain ls ==="
/opt/data/pdf-venv/bin/b2 ls -r b2://nura-backups 2>&1 | wc -l
