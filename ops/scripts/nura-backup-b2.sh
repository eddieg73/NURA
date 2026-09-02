#!/bin/bash
# NURA encrypted off-site backup → Backblaze B2 (restic native B2 backend).
# Uses the live B2 account (B2_KEY_ID / B2_APPLICATION_KEY in .env) + restic repo password.
# Bucket: nura-backups  Repo path: nightly  (restic b2:bucket:path)
set -euo pipefail
export PATH="/opt/data/tools/bin:$PATH"
ENVF=/opt/data/profiles/nura/.env

# --- credentials from .env (never printed) ---
B2_ACCOUNT_ID=$(grep -oP '(?<=^B2_KEY_ID=).*' "$ENVF" 2>/dev/null | head -1 | tr -d '\r\n"')
B2_ACCOUNT_KEY=$(grep -oP '(?<=^B2_APPLICATION_KEY=).*' "$ENVF" 2>/dev/null | head -1 | tr -d '\r\n"')
RESTIC_PASSWORD=$(grep -oP '(?<=^RESTIC_PASSWORD=).*' "$ENVF" 2>/dev/null | head -1 | tr -d '\r\n"')

if [ -z "$B2_ACCOUNT_ID" ] || [ -z "$B2_ACCOUNT_KEY" ] || [ -z "$RESTIC_PASSWORD" ]; then
  echo "B2 BACKUP SKIPPED: B2_KEY_ID / B2_APPLICATION_KEY / RESTIC_PASSWORD missing in .env"
  exit 0
fi

# restic B2 backend uses B2_ACCOUNT_ID / B2_ACCOUNT_KEY env vars natively
export B2_ACCOUNT_ID
export B2_ACCOUNT_KEY
export RESTIC_PASSWORD
export RESTIC_REPOSITORY="b2:nura-backups:nightly"

# --- init if repo doesn't exist yet ---
if ! restic snapshots 2>/dev/null | grep -q "repository is empty\|snapshots"; then
  echo "B2 repo not initialized — initializing..."
  restic init 2>&1 | tail -3
fi

restic unlock 2>/dev/null || true

# --- the actual backup (selective, excludes git/caches/node_modules; PHI-safe paths only) ---
restic backup /opt/data/profiles/nura/config.yaml \
  /opt/data/profiles/nura/skills \
  /opt/data/profiles/nura/memories \
  /opt/data/Obsidian\ Vault/NURA-OS \
  /opt/data/home/nura-clinical-platform \
  /opt/data/home/second-opinion \
  /opt/data/home/meal-planner \
  --exclude '**/.git' --exclude '**/__pycache__' --exclude '**/node_modules' \
  --tag nightly 2>&1 | tail -4

# --- retention ---
restic forget --keep-daily 7 --keep-weekly 4 --keep-monthly 6 --prune 2>&1 | tail -2

echo "B2 BACKUP OK: $(restic snapshots --latest 1 2>/dev/null | tail -2)"
