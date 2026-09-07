#!/bin/bash
# NURA Command Center daily runner — regenerate NOC page + file daily snapshot to Notion.
# STDOUT is the delivered message (no_agent watchdog): EMPTY = silent (healthy). Alert only if real problems.
set -uo pipefail
P=/opt/data/profiles/nura/scripts
PY=/opt/hermes/.venv/bin/python3
export NURA_PROFILE=/opt/data/profiles/nura

# 1) Regenerate the served NOC page (always) + emit state json
$PY "$P/command-center.py" --emit-json > "$P/../mission-control/state.json" 2>/dev/null || true

# 2) Compute actionable alerts; file to Notion only when there are real problems OR always daily
ALERT_JSON=$($PY "$P/command-center.py" --emit-json 2>/dev/null)
ERR=$(echo "$ALERT_JSON" | $PY -c "import sys,json;d=json.load(sys.stdin);print(d['cron_err'])" 2>/dev/null || echo 0)

# Is the NOC page serving? If not, start it (detached so it survives the cron shell)
if ! curl -s -m 3 -o /dev/null http://127.0.0.1:4100/index.html 2>/dev/null; then
  setsid /opt/hermes/.venv/bin/python3 -m http.server 4100 --bind 127.0.0.1 \
    --directory /opt/data/profiles/nura/mission-control \
    >/opt/data/profiles/nura/mission-control/server.log 2>&1 < /dev/null &
  disown 2>/dev/null || true
  sleep 2
  # re-assert the Tailscale serve proxy (mapping survives; only needed if it was dropped)
  export PATH="/opt/data/bin:$PATH"
  /opt/data/bin/tailscale --socket=/tmp/tailscaled.sock serve --bg --http=4100 http://127.0.0.1:4100 >/dev/null 2>&1 || true
fi

# 3) If there are real problems, that's the ONLY time we speak (deliver a signal)
if [ "$ERR" -gt 0 ]; then
  echo "🔴 NURA Command Center — $(echo "$ALERT_JSON" | $PY -c "import sys,json;d=json.load(sys.stdin);print(d['cron_err'],'crons erroring of',d['cron_total'])")"
fi

# 4) File the daily snapshot to Notion (always, silently)
$PY - <<'PY' 2>/dev/null || true
import importlib.util, os
spec=importlib.util.spec_from_file_location("cc","/opt/data/profiles/nura/scripts/command-center.py")
cc=importlib.util.module_from_spec(spec); spec.loader.exec_module(cc)
try:
    st,_=cc.build()
    md="\n".join("🔴 "+a for a in st["alerts"]) or "✅ All clear."
    md+=f"\n· Cron fleet {st['cron_total']} ({st['cron_ok']} ok / {st['cron_err']} err / {st['cron_paused']} paused)"
    md+=f"\n· Gateway {'UP' if st['gw_ok'] else 'DOWN'} · disk {st['disk'][4] if len(st['disk'])>4 else '?'} · {st['mcp_count']} MCP lanes"
    cc.daily_notion(md,"Daily Ops Snapshot")
except Exception as e:
    pass
PY
exit 0
