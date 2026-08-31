#!/usr/bin/env bash
# Daily Perfex/pay.nuratech.ai backup — mysqldump + tar of /var/www/crm, dated, keep 7.
# Installed as crontab by the agent. Creates files in /root/pay_backup/ (same as the
# existing 07-28 dump) with today's date. Retention: keep 7 (delete older).
set -e
export PATH="/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin"
DEST="/root/pay_backup"
mkdir -p "$DEST"
TODAY="$(date +%F)"

# DB credentials from the app config (read-only define() lines)
DB_USER="$(grep -oE "define\('APP_DB_USERNAME', *'[^']+'" /var/www/crm/application/config/app-config.php 2>/dev/null | grep -oE "'[^']+'$" | tr -d "'")"
DB_NAME="$(grep -oE "define\('APP_DB_NAME', *'[^']+'" /var/www/crm/application/config/app-config.php 2>/dev/null | grep -oE "'[^']+'$" | tr -d "'")"
DB_PASS="$(grep -oE "define\('APP_DB_PASSWORD', *'[^']+'" /var/www/crm/application/config/app-config.php 2>/dev/null | grep -oE "'[^']+'$" | tr -d "'")"
DB_USER="${DB_USER:-merchant_user}"; DB_NAME="${DB_NAME:-merchant_db}"

echo "[backup] ${TODAY} — dumping DB (user=${DB_USER}, db=${DB_NAME})..."
if [ -n "$DB_PASS" ]; then
  mysqldump --no-tablespaces -u "$DB_USER" -p"$DB_PASS" "$DB_NAME" > "$DEST/pay.nuratech.ai-db-${TODAY}.sql"
else
  mysqldump --no-tablespaces -u "$DB_USER" "$DB_NAME" > "$DEST/pay.nuratech.ai-db-${TODAY}.sql"
fi
echo "[backup] ${TODAY} — archiving files..."
tar -czf "$DEST/pay.nuratech.ai-files-${TODAY}.tar.gz" -C /var/www crm 2>/dev/null

echo "[backup] ${TODAY} — verifying..."
zsize=$(stat -c%s "$DEST/pay.nuratech.ai-db-${TODAY}.sql" 2>/dev/null || echo 0)
fz=$(stat -c%s "$DEST/pay.nuratech.ai-files-${TODAY}.tar.gz" 2>/dev/null || echo 0)
echo "  db size: ${zsize} bytes | files: ${fz} bytes"

# retention: keep latest 7 of each
ls -1t "$DEST"/pay.nuratech.ai-db-*.sql 2>/dev/null | tail -n +8 | xargs -r rm -f
ls -1t "$DEST"/pay.nuratech.ai-files-*.tar.gz 2>/dev/null | tail -n +8 | xargs -r rm -f
echo "[backup] ${TODAY} — complete. Retention: 7."
