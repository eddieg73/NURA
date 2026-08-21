#!/usr/bin/env bash
# NURA weather advisory — the heat + winter advisories for Tampa + Pompano.
# Silent when clean (the no_agent cron pattern). The NWS alerts API (keyless).
POINTS=("27.9506,-82.4572" "26.2379,-80.1248")  # Tampa, Pompano Beach
NAMES=("Tampa" "Pompano")

OUT=""
for i in 0 1; do
  P=${POINTS[$i]}; N=${NAMES[$i]}
  DATA=$(curl -s -m 15 -H "User-Agent: NURA-Watch (eg@nuratech.ai)" \
    "https://api.weather.gov/alerts/active?point=$P")
  EVENTS=$(echo "$DATA" | python3 -c "
import sys, json
try:
    d = json.load(sys.stdin)
except Exception:
    sys.exit()
keep = ['Heat Advisory','Excessive Heat Warning','Excessive Heat Watch',
        'Freeze Warning','Freeze Watch','Cold Weather Advisory','Wind Chill Advisory',
        'Wind Chill Warning','Hard Freeze Warning']
seen = set()
for f in d.get('features', []):
    p = f.get('properties', {})
    ev = p.get('event', '')
    if ev in keep and ev not in seen:
        seen.add(ev)
        onset = (p.get('onset') or '')[:16].replace('T',' ')
        ends = (p.get('ends') or '')[:16].replace('T',' ')
        sev = p.get('severity', '')
        print(f'{ev} [{sev}] {onset} -> {ends}')
")
  if [ -n "$EVENTS" ]; then
    OUT+="$N: $EVENTS
"
  fi
done

if [ -n "$OUT" ]; then
  HOUR=$(date +%H)
  PERIOD="morning"
  [ "$HOUR" -ge 11 ] && PERIOD="afternoon/evening"
  echo "🌡️ Weather advisories — $PERIOD update
$OUT"
fi
