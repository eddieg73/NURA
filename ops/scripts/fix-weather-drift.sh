#!/bin/bash
# Fix the weather-alert monitor config drift: ensure ALL copies are the signal-only rewrite.
set -uo pipefail
SRC=/opt/data/scripts/local-weather-monitor.py
[ -f "$SRC" ] || { echo "SRC missing: $SRC"; exit 1; }

# 1. Install into cron-resolvable ~/.hermes/scripts/
mkdir -p /opt/data/profiles/nura/home/.hermes/scripts
cp "$SRC" /opt/data/profiles/nura/home/.hermes/scripts/local-weather-monitor.py
chmod 700 /opt/data/profiles/nura/home/.hermes/scripts/local-weather-monitor.py
echo "1. installed -> ~/.hermes/scripts/local-weather-monitor.py"

# 2. Fix the stale copies (remove the old forecast-emitting versions)
for d in /opt/data/profiles/nura/scripts /opt/data/NURA/scripts /opt/data/NURA/servers; do
  cp "$SRC" "$d/local-weather-monitor.py" 2>/dev/null && echo "2. overwrote $d/local-weather-monitor.py"
done

# 3. Verify every copy now carries the signal-only marker and NO 'through <time>' forecast line
echo "3. verification (signal-marker counts; expect >=1 on each, and 0 'forecast through'):"
for f in \
  /opt/data/profiles/nura/home/.hermes/scripts/local-weather-monitor.py \
  /opt/data/scripts/local-weather-monitor.py \
  /opt/data/profiles/nura/scripts/local-weather-monitor.py \
  /opt/data/NURA/scripts/local-weather-monitor.py \
  /opt/data/NURA/servers/local-weather-monitor.py ; do
    if [ -f "$f" ]; then
      s=$(grep -c "severity-laddered" "$f")
      thru=$(grep -c "through" "$f")
      echo "  $f  signal=$s  forecast_through=$thru"
    else
      echo "  $f  MISSING"
    fi
done
