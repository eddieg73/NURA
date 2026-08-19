#!/usr/bin/env bash
# Nightly DB snapshots — Perfex + OpenEMR (host-side, cron 02:00 UTC)
# Places: /opt/docker/backups/archive/ · purge >14d · scoped users only
set -euo pipefail
BK=/opt/docker/backups
ARC=$BK/archive
mkdir -p "$ARC"
TS=$(date -u +%F_%H-%M-%S)
LOG=$BK/db-snapshot.log

# --- Perfex (host 817449 or via tunnel) ---
# shellcheck disable=SC1091
[ -f /opt/docker/.env ] && . /opt/docker/.env
PUSER="${PERFEX_DB_USER:-perfex_mcp_user}"
PPASS="${PERFEX_DB_PASSWORD:-}"
PDB="${PERFEX_DB_NAME:-perfex_crm_db}"
PHOST="${PERFEX_DB_HOST:-127.0.0.1}"
# --- OpenEMR (core host) ---
EUSER="${OPENEMR_DB_USER:-openemr}"
EPASS="${OPENEMR_DB_PASSWORD:-}"
EDB="${OPENEMR_DB_NAME:-openemr}"
EHOST="${OPENEMR_DB_HOST:-127.0.0.1}"

if [ -n "$PPASS" ]; then
  mysqldump -h "$PHOST" -u "$PUSER" -p"$PPASS" "$PDB" > "$BK/perfex_$TS.sql" 2>>"$LOG"
  tar -czf "$ARC/perfex_$TS.tar.gz" -C "$BK" "perfex_$TS.sql" && rm -f "$BK/perfex_$TS.sql"
  echo "$(date -u +%FT%TZ) perfex OK $TS" >> "$LOG"
else
  echo "$(date -u +%FT%TZ) perfex SKIP (no creds)" >> "$LOG"
fi

if [ -n "$EPASS" ]; then
  mysqldump -h "$EHOST" -u "$EUSER" -p"$EPASS" "$EDB" > "$BK/openemr_$TS.sql" 2>>"$LOG"
  tar -czf "$ARC/openemr_$TS.tar.gz" -C "$BK" "openemr_$TS.sql" && rm -f "$BK/openemr_$TS.sql"
  echo "$(date -u +%FT%TZ) openemr OK $TS" >> "$LOG"
else
  echo "$(date -u +%FT%TZ) openemr SKIP (no creds)" >> "$LOG"
fi

find "$ARC" -name "*.tar.gz" -mtime +14 -delete
echo "$(date -u +%FT%TZ) purge done; archive: $(find "$ARC" -name '*.tar.gz' | wc -l) files" >> "$LOG"
