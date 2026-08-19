#!/usr/bin/env bash
set -euo pipefail

# FIX (two-gateway conflict): restart the CANONICAL gateway (gateway-nura).
# This script previously targeted gateway-default, which resurrected the
# duplicate root-slot gateway (it runs the nura profile via active_profile)
# and caused the two-gateway fight over ports 8080/8642 and the Telegram bot.
service_dir="/run/service/gateway-nura"
[[ -d "$service_dir" ]]

if command -v s6-svc >/dev/null 2>&1; then
  s6-svc -r "$service_dir"
else
  /package/admin/s6/command/s6-svc -r "$service_dir"
fi
