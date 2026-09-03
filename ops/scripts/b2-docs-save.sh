#!/bin/bash
# Sync valuable docs + software to Backblaze B2 for durability.
# A: nura-documents bucket = Obsidian Vault + nura_medical/docs (the source-of-truth docs)
# B: nura-backups bucket = already nightly restic (config/skills/memories); this adds the docs.
set -uo pipefail
export HOME=/opt/data/profiles/nura/home
ENVF=/opt/data/profiles/nura/.env
export B2_APPLICATION_KEY_ID=$(grep -oP '(?<=^B2_KEY_ID=).*' "$ENVF" | head -1 | tr -d '\r\n"')
export B2_APPLICATION_KEY=$(grep -oP '(?<=^B2_APPLICATION_KEY=).*' "$ENVF" | head -1 | tr -d '\r\n"')

echo "=== B2 reachable + buckets ==="
/opt/data/pdf-venv/bin/b2 bucket list 2>&1 | awk '{print $1, $3}'

echo
echo "=== B2 sync: Obsidian Vault (source-of-truth docs) -> nura-documents/vault ==="
/opt/data/pdf-venv/bin/b2 sync --no-progress "/opt/data/Obsidian Vault" b2://nura-documents/vault 2>&1 | tail -4

echo
echo "=== B2 sync: nura_medical/docs + ops/scripts (software docs + versioned scripts) -> nura-documents/nura-repo ==="
/opt/data/pdf-venv/bin/b2 sync --no-progress /opt/data/nura_medical/docs b2://nura-documents/nura-repo/docs 2>&1 | tail -3
/opt/data/pdf-venv/bin/b2 sync --no-progress /opt/data/nura_medical/ops/scripts b2://nura-documents/nura-repo/ops-scripts 2>&1 | tail -3

echo
echo "=== VERIFY: count files now in nura-documents ==="
N=$(/opt/data/pdf-venv/bin/b2 ls -r --json b2://nura-documents 2>&1 | grep -c '"fileName"')
echo "files in nura-documents: $N"
