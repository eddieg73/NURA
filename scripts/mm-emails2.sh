#!/bin/bash
# Mattermost real-email correction v2 (current-email -> new-email)
MM=mattermost-r2wm-mattermost-1
MMCTL="docker exec $MM /mattermost/bin/mmctl --local"
$MMCTL user change-email eddie@nuratech.ai eg@nuratech.ai 2>&1 | head -1
$MMCTL user change-email hermes@nuratech.ai Nura@nuratech.ai 2>&1 | head -1
$MMCTL user change-email amrit@nuratech.ai araj@nuratech.ai 2>&1 | head -1
$MMCTL user change-email oussama@nuratech.ai Oussama@nuratech.ai 2>&1 | head -1
$MMCTL user change-email jade@nuratech.ai Jade@nuratech.ai 2>&1 | head -1
echo "=== final ==="
$MMCTL user list 2>&1 | head -8
