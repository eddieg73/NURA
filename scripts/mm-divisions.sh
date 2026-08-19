#!/bin/bash
# Mattermost division channels + agent seats (the division managers)
MM=mattermost-r2wm-mattermost-1
MMCTL="docker exec $MM /mattermost/bin/mmctl --local"
# Division channels
for CH in radiology assurance aero ems avionics wearables capital-markets mlr core; do
  $MMCTL channel create --team nuratech --name "$CH" --display-name "$CH" 2>&1 | grep -E "New channel|exists" | head -1 || true
done
# Agent users (division managers + the NURA agents)
$MMCTL user create --email veronica@nuratech.ai --username veronica --password "VeronicaNura2026!" 2>&1 | head -1 || true
$MMCTL user create --email cora@nuratech.ai --username cora --password "CoraNura2026!" 2>&1 | head -1 || true
$MMCTL user create --email jarvis@nuratech.ai --username jarvis --password "JarvisNura2026!" 2>&1 | head -1 || true
$MMCTL user create --email lexa@nuratech.ai --username lexa --password "LexaNura2026!" 2>&1 | head -1 || true
$MMCTL user create --email aura@nuratech.ai --username aura --password "AuraNura2026!" 2>&1 | head -1 || true
$MMCTL user create --email alexis@nuratech.ai --username alexis --password "AlexisNura2026!" 2>&1 | head -1 || true
# Add agents to team + their division channels
for A in veronica cora jarvis lexa aura alexis; do
  $MMCTL team add nuratech "$A" 2>&1 | head -1 || true
done
$MMCTL channel add nuratech:general veronica cora jarvis lexa aura alexis 2>&1 | head -1 || true
$MMCTL channel add nuratech:radiology jarvis alexis 2>&1 | head -1 || true
$MMCTL channel add nuratech:content veronica aura 2>&1 | head -1 || true
$MMCTL channel add nuratech:mlr lexa 2>&1 | head -1 || true
$MMCTL channel add nuratech:assurance cora 2>&1 | head -1 || true
echo "=== users ==="
$MMCTL user list 2>&1 | tail -8
