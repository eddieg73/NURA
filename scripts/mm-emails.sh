#!/bin/bash
# Mattermost real-email correction (founder 08-04)
MM=mattermost-r2wm-mattermost-1
MMCTL="docker exec $MM /mattermost/bin/mmctl --local"
$MMCTL user change-email eddie eg@nuratech.ai 2>&1 | head -1 || echo "eddie email cmd failed"
$MMCTL user change-email hermes Nura@nuratech.ai 2>&1 | head -1 || echo "hermes email cmd failed"
$MMCTL user change-email amrit araj@nuratech.ai 2>&1 | head -1 || echo "amrit email cmd failed"
$MMCTL user change-email oussama Oussama@nuratech.ai 2>&1 | head -1 || echo "oussama email cmd failed"
$MMCTL user change-email jade Jade@nuratech.ai 2>&1 | head -1 || echo "jade email cmd failed"
echo "=== final users ==="
$MMCTL user list 2>&1 | head -8
