#!/bin/bash
# Mattermost setup — mmctl local mode
MM=mattermost-r2wm-mattermost-1
docker exec "$MM" /mattermost/bin/mmctl --local version 2>&1 | head -3
echo "=== users ==="
docker exec "$MM" /mattermost/bin/mmctl --local user list 2>&1 | head -6
