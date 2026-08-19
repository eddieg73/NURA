#!/bin/bash
# NURA HEALTH WATCHDOG — the cron wrapper: SILENT when healthy, ALERT when anything is down.
OUT=$(timeout 110 python3 /opt/data/scripts/nura-inventory-health.py 2>/dev/null | grep 'UNHEALTHY')
if [ -n "$OUT" ]; then
  echo "🔴 NURA HEALTH ALERT: $OUT"
fi
exit 0
