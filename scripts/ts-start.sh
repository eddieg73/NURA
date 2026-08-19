#!/bin/bash
# Tailscale userspace join for the Hermes box (tailnet tail90d8a0.ts.net)
set -x
mkdir -p /opt/data/tailscale-state
# start tailscaled userspace if not running
if [ ! -S /tmp/tailscaled.sock ]; then
  /opt/data/bin/tailscaled --socket=/tmp/tailscaled.sock \
    --state=/opt/data/tailscale-state/tailscaled.state \
    --tun=userspace-networking \
    --socks5-server=localhost:1055 \
    --outbound-http-proxy-listen=localhost:1055 &
  sleep 5
fi
/opt/data/bin/tailscale --socket=/tmp/tailscaled.sock version
