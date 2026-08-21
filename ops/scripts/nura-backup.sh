#!/bin/bash
# NURA nightly backup — silent-OK: no output on success, error alert on failure.
set -euo pipefail
SRC=/opt/data
OUT=/opt/data/uploads
STAMP=$(date +%Y%m%d)
KEEP=7
ARCHIVE="$OUT/nura-backup-$STAMP.tar.gz"

cd "$SRC"
tar czf "$ARCHIVE" \
  --warning=no-file-changed \
  --exclude='profiles/nura/cache' --exclude='profiles/nura/audio_cache' \
  --exclude='profiles/nura/logs' --exclude='chrome' --exclude='*.pyc' \
  "Obsidian Vault" profiles/nura/data profiles/nura/scripts profiles/nura/config.yaml \
  profiles/nura/.env profiles/nura/skills profiles/nura/cron profiles/nura/memories \
  || { echo "BACKUP FAILED: tar error $?"; exit 1; }

chmod 600 "$ARCHIVE"

# Rotate: keep last 7
ls -1t "$OUT"/nura-backup-*.tar.gz 2>/dev/null | tail -n +$((KEEP+1)) | xargs -r rm -f

# Verify archive integrity (quick test)
tar tzf "$ARCHIVE" >/dev/null 2>&1 || { echo "BACKUP VERIFY FAILED: $ARCHIVE"; exit 1; }

echo "OK $(du -h "$ARCHIVE" | cut -f1) $ARCHIVE"
