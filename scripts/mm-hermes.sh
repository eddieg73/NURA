#!/bin/bash
# Hermes on Mattermost — the watcher seat + API token
MM=mattermost-r2wm-mattermost-1
MMCTL="docker exec $MM /mattermost/bin/mmctl --local"
$MMCTL user create --email hermes@nuratech.ai --username hermes --password "HermesNura2026!" 2>&1 | head -1 || echo "hermes exists"
$MMCTL team add nuratech hermes 2>&1 | head -1 || true
$MMCTL channel add nuratech:general hermes 2>&1 | head -1 || true
$MMCTL channel add nuratech:crm hermes 2>&1 | head -1 || true
$MMCTL channel add nuratech:engineering hermes 2>&1 | head -1 || true
$MMCTL channel add nuratech:content hermes 2>&1 | head -1 || true
$MMCTL channel add nuratech:atlas-briefings hermes 2>&1 | head -1 || true
echo "=== hermes token ==="
$MMCTL user create-token hermes --description "hermes watch lane" 2>&1 | head -4
echo "=== final users ==="
$MMCTL user list 2>&1 | head -8
