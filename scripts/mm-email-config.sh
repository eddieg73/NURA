#!/bin/bash
# Mattermost email engine — verify users + SMTP config (auth pending the app password)
MM=mattermost-r2wm-mattermost-1
MMCTL="docker exec $MM /mattermost/bin/mmctl --local"
# 1. Mark all users verified (email identity confirmed regardless of SMTP)
for U in eddie atlas hermes oussama amrit jade alexis veronica cora jarvis lexa aura; do
  $MMCTL user verify "$U" 2>&1 | grep -vE "^$" | head -1 || true
done
# 2. SMTP skeleton (host/port/from — auth + password land with the app password)
$MMCTL config set EmailSettings.SMTPServer "smtp.gmail.com" 2>&1 | head -1
$MMCTL config set EmailSettings.SMTPPort "587" 2>&1 | head -1
$MMCTL config set EmailSettings.SMTPUsername "Nura@nuratech.ai" 2>&1 | head -1
$MMCTL config set EmailSettings.FeedbackEmail "Nura@nuratech.ai" 2>&1 | head -1
$MMCTL config set EmailSettings.FeedbackName "NURATECH" 2>&1 | head -1
$MMCTL config set EmailSettings.RequireEmailVerification "false" 2>&1 | head -1
echo "=== verify ==="
$MMCTL user list 2>&1 | grep -E "eddie|hermes|atlas|oussama" | head -4
