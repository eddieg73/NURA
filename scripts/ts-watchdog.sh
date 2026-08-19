#!/bin/bash
# Tailscale userspace + Serve + WebUI watchdog (silent when healthy)
SOCK=/tmp/tailscaled.sock
TS=/opt/data/bin/tailscale
if [ ! -S "$SOCK" ] || ! $TS --socket=$SOCK status >/dev/null 2>&1; then
  TS_VAR_ROOT=/opt/data/tailscale-state nohup /opt/data/bin/tailscaled \
    --socket=$SOCK --statedir=/opt/data/tailscale-state \
    --tun=userspace-networking \
    --socks5-server=localhost:1055 \
    --outbound-http-proxy-listen=localhost:1055 >/dev/null 2>&1 &
  sleep 6
fi
if ! $TS --socket=$SOCK serve status 2>/dev/null | grep -q "proxy http://127.0.0.1:8787"; then
  $TS --socket=$SOCK serve --bg --http=80 8787 >/dev/null 2>&1
fi
# WebUI guard: relaunch if the health endpoint is down
if ! curl -sf -m 5 http://127.0.0.1:8787/health >/dev/null 2>&1; then
  HERMES_WEBUI_PASSWORD="$(grep -E '^HERMES_WEBUI_PASSWORD=' /opt/data/profiles/nura/.env | head -1 | cut -d= -f2- | tr -d '"'"'"'"')" \
  HERMES_WEBUI_PORT=8787 \
  HERMES_WEBUI_STATE_DIR=/opt/data/hermes-webui-state \
  nohup /opt/data/profiles/nura/hermes-agent/venv/bin/python \
    /opt/data/hermes-webui/server.py >/dev/null 2>&1 &
fi
# Mesh monitor guard: relaunch the meshtastic-monitor web app if down
if ! curl -sf -m 5 http://127.0.0.1:5000/api/health >/dev/null 2>&1; then
  PYTHONPATH=/opt/data/profiles/nura/python-packages MESHTASTIC_DB=/opt/data/meshtastic-monitor/data/meshtastic.db PORT=5000 \
    nohup python3 /opt/data/meshtastic-monitor/app.py >/dev/null 2>&1 &
fi
# NURA tools API guard (derm/verify/metar) + radiology intelligence guard
if ! curl -sf -m 5 http://127.0.0.1:8095/health >/dev/null 2>&1; then
  PYTHONPATH=/opt/data/profiles/nura/python-packages nohup python3 /opt/data/scripts/nura-tools-api.py >/dev/null 2>&1 &
fi
if ! curl -sf -m 5 http://127.0.0.1:8092/health >/dev/null 2>&1; then
  PYTHONPATH=/opt/data/profiles/nura/python-packages nohup python3 /opt/data/nura-radiology-intelligence/app.py >/dev/null 2>&1 &
fi
# Paperclip gateway reverse tunnel: Lab 127.0.0.1:8642 -> this box's Hermes gateway
if ! ssh -o BatchMode=yes -o ConnectTimeout=8 -i /opt/data/profiles/nura/home/.ssh/id_nura_clean root@72.60.163.140 'curl -s -m 6 http://127.0.0.1:8642/v1/models -o /dev/null -w "%{http_code}"' 2>/dev/null | grep -qE '200|401'; then
  nohup ssh -o BatchMode=yes -o ExitOnForwardFailure=yes -o ServerAliveInterval=30 -N \
    -R 8642:127.0.0.1:8642 -i /opt/data/profiles/nura/home/.ssh/id_nura_clean root@72.60.163.140 >/dev/null 2>&1 &
fi
# silent when all healthy
