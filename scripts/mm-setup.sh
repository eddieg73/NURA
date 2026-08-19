#!/bin/bash
# Mattermost org setup — Atlas (CEO) + team + founder (system admin, watches all)
set -e
MM=mattermost-r2wm-mattermost-1
MMCTL="docker exec $MM /mattermost/bin/mmctl --local"
# 1. Founder = system admin (oversight)
$MMCTL user create --email eddie@nuratech.ai --username eddie --password "EddieNura2026!" --system-admin 2>&1 | head -1 || echo "eddie exists"
# 2. Team members (agents + humans)
$MMCTL user create --email atlas@nuratech.ai --username atlas --password "AtlasNura2026!" 2>&1 | head -1 || echo "atlas exists"
$MMCTL user create --email oussama@nuratech.ai --username oussama --password "OussamaNura2026!" 2>&1 | head -1 || echo "oussama exists"
$MMCTL user create --email amrit@nuratech.ai --username amrit --password "AmritNura2026!" 2>&1 | head -1 || echo "amrit exists"
$MMCTL user create --email jade@nuratech.ai --username jade --password "JadeNura2026!" 2>&1 | head -1 || echo "jade exists"
# 3. Team
$MMCTL team create --name nuratech --display-name "NURATECH" 2>&1 | head -1 || echo "team exists"
# 4. Channels
for CH in general crm engineering content atlas-briefings; do
  $MMCTL channel create --team nuratech --name "$CH" --display-name "$CH" 2>&1 | head -1 || echo "channel $CH exists"
done
# 5. Add members
for U in eddie atlas oussama amrit jade; do
  $MMCTL team add nuratech "$U" 2>&1 | head -1 || true
done
echo "=== users ==="
$MMCTL user list 2>&1 | head -8
echo "=== channels ==="
$MMCTL channel list --team nuratech 2>&1 | head -8
