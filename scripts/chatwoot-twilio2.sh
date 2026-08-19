#!/bin/bash
# Twilio SMS inbox creation v2 (bundle exec rails runner)
SID="$1"
TOKEN="$2"
docker exec -w /app chatwoot-rails-1 bundle exec rails runner "
account = Account.find(1)
existing = account.inboxes.where(name: 'Twilio SMS').first
if existing
  puts 'INBOX_EXISTS ' + existing.id.to_s
else
  channel = Channel::TwilioSms.new(
    twilio_account_sid: '$SID',
    twilio_auth_token: '$TOKEN',
    twilio_phone_number: '+17274773636',
    twilio_messaging_service_sid: nil
  )
  channel.save!
  inbox = account.inboxes.create!(name: 'Twilio SMS', channel: channel)
  puts 'INBOX_CREATED ' + inbox.id.to_s
end
" 2>&1 | tail -3
echo "=== verify inboxes ==="
CWU=$(docker inspect chatwoot-postgres-1 --format '{{range .Config.Env}}{{println .}}{{end}}' 2>/dev/null | grep '^POSTGRES_USER=' | cut -d= -f2-)
docker exec chatwoot-postgres-1 psql -U "$CWU" -d chatwoot -t -c "SELECT id, name, channel_type FROM inboxes" 2>&1 | head -6
