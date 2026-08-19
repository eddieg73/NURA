#!/bin/bash
cd /opt/data/uploads
/opt/data/chrome/chrome-linux64/chrome --headless --disable-gpu --no-sandbox \
  --screenshot=/opt/data/uploads/app-ui-mock.png \
  --window-size=460,920 --hide-scrollbars \
  "file:///opt/data/uploads/app-ui-mock.html" >/dev/null 2>&1
ls -la /opt/data/uploads/app-ui-mock.png | awk '{print $5, $9}'
