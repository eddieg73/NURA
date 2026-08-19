#!/bin/bash
# Chatwoot + Twilio config probe (read-only)
echo "=== Chatwoot env (non-secret keys) ==="
grep -E 'FRONTEND_URL|TWILIO|ACCOUNT|DEFAULT_LOCALE' /docker/chatwoot/.env 2>/dev/null | grep -vE 'SECRET|KEY|PASS|TOKEN' | head -8
echo "=== Twilio creds present in env? ==="
grep -cE 'TWILIO_(ACCOUNT_SID|AUTH_TOKEN|API_KEY)' /docker/chatwoot/.env 2>/dev/null | head -1
echo "=== Chatwoot DB users (admin) ==="
CWU=$(grep -E '^POSTGRES_USER=' /docker/chatwoot/.env 2>/dev/null | cut -d= -f2-)
CWP=$(grep -E '^POSTGRES_PASSWORD=' /docker/chatwoot/.env 2>/dev/null | cut -d= -f2-)
echo "pg creds: user=${#CWU} pass=${#CWP}"
DB=$(docker ps --format '{{.Names}}' | grep -iE 'chatwoot.*postgres|postgres.*chatwoot' | head -1)
echo "db_container=$DB"
if [ -n "$DB" ] && [ -n "$CWU" ]; then
  docker exec "$DB" psql -U "$CWU" -d chatwoot_production -t -c "SELECT email, name, type FROM users ORDER BY id LIMIT 5" 2>&1 | head -6
fi
