#!/bin/bash
# NURA encrypted backup → Cloudflare R2 (restic). Arms when R2 token lands.
# Operator: create R2 bucket "nura-backup" + API token (Object Read/Write) → drop in uploads → I wire the remote.
set -euo pipefail
export PATH="/opt/data/tools/bin:$PATH"
ENVF=/opt/data/profiles/nura/.env
TOKEN=$(grep -oP '(?<=^R2_API_TOKEN=).*' "$ENVF" 2>/dev/null | head -1 | tr -d '\r\n"'"'"'') || true
RESTIC_PASS=$(grep -oP '(?<=^RESTIC_PASSWORD=).*' "$ENVF" 2>/dev/null | head -1 | tr -d '\r\n"'"'"'') || true
if [ -z "$TOKEN" ] || [ -z "$RESTIC_PASS" ]; then
  echo "BACKUP SKIPPED: R2_API_TOKEN / RESTIC_PASSWORD missing in .env"
  exit 0
fi
export R2_ENDPOINT="${R2_ENDPOINT:-https://<accountid>.r2.cloudflarestorage.com}"
export RESTIC_REPOSITORY="rclone:r2-nura:nura-backup"
export RESTIC_PASSWORD
export RCLONE_R2_PROVIDER=Cloudflare
export RCLONE_R2_ACCESS_KEY_ID="${R2_ACCESS_KEY_ID:-}"
export RCLONE_R2_SECRET_ACCESS_KEY="$TOKEN"
rclone config create r2-nura s3 provider Cloudflare access_key_id "$R2_ACCESS_KEY_ID" secret_access_key "$TOKEN" endpoint "$R2_ENDPOINT" 2>/dev/null || true
restic unlock 2>/dev/null || true
restic backup /opt/data/profiles/nura/config.yaml /opt/data/profiles/nura/.env \
  /opt/data/home/nura-clinical-platform /opt/data/home/second-opinion /opt/data/home/meal-planner /opt/data/home/mail-triage \
  /opt/data/profiles/nura/skills /opt/data/profiles/nura/memories \
  --exclude '**/.git' --exclude '**/__pycache__' --exclude '**/node_modules' \
  --tag nightly
restic forget --keep-daily 7 --keep-weekly 4 --keep-monthly 6 --prune
echo "BACKUP OK: $(restic snapshots --latest 1 | tail -2 | head -1)"
