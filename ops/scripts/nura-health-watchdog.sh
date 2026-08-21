#!/bin/bash
# NURA HEALTH WATCHDOG — SILENT when healthy, ALERT on NEW failures only.
# The anti-flood law (the 08-13 mandate): the known/standing unhealthy items alert ONCE (the on the transition),
# never every 5 minutes. The state file remembers the last unhealthy set.
STATE=/opt/data/profiles/nura/cron/health-watchdog.state
OUT=$(timeout 110 python3 /opt/data/scripts/nura-inventory-health.py 2>/dev/null | grep 'UNHEALTHY')

# The extract the current unhealthy set (the everything after "UNHEALTHY:")
CUR=$(echo "$OUT" | sed 's/.*UNHEALTHY: //')
PREV=$(cat "$STATE" 2>/dev/null)

if [ -n "$OUT" ]; then
  if [ "$CUR" != "$PREV" ]; then
    echo "🔴 NURA HEALTH ALERT: $OUT"
    echo "$CUR" > "$STATE"
  fi
  # The same as before → the SILENT (the known condition, the never re-alert)
else
  # The all healthy: the clear the state so the next failure is a NEW alert
  [ -n "$PREV" ] && rm -f "$STATE"
fi
exit 0
