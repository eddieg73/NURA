#!/usr/bin/env bash
set -euo pipefail

manager=/opt/data/scripts/behive_service_manager.py
if ! "$manager" status >/dev/null 2>&1; then
  "$manager" ensure --quiet
fi
