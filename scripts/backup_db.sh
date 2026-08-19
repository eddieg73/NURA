#!/bin/bash
# The HIPAA-compliant AES-256 encrypted DB-dump (the paperclip-db!)
BACKUP_DIR="/var/backups/nuratech_db"
TIMESTAMP=$(date +%Y%m%d_%H%M%S)
BACKUP_FILE="${BACKUP_DIR}/db_dump_${TIMESTAMP}.sql.gz.enc"
PASSPHRASE="nuratech_offsite_backup_passphrase_2026"
mkdir -p "$BACKUP_DIR"
docker exec paperclip-db pg_dump -U paperclip -d paperclip | gzip -9 | openssl enc -aes-256-cbc -salt -pbkdf2 -pass pass:"$PASSPHRASE" -out "$BACKUP_FILE"
find "$BACKUP_DIR" -type f -name "*.enc" -mtime +30 -delete
echo "[✓] Encrypted backup: $BACKUP_FILE"
