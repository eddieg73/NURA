#!/usr/bin/env python3
"""
Cron monitor shim for the estate watchdog.

Same reason as lane-state-monitor.py: cron `monitor` accepts only a bare filename, so this runs the
real watchdog with --state and prints its deterministic problem string for tick-to-tick diffing.
Deterministic output is the contract — a varying string false-fires every tick and gets the watchdog
muted, which is exactly how a monitoring system dies.
"""
import subprocess
import sys

WATCHDOG = "/opt/data/profiles/nura/scripts/estate-watchdog.py"
PY = "/opt/hermes/.venv/bin/python3"

try:
    r = subprocess.run([PY, WATCHDOG, "--state"], capture_output=True, text=True, timeout=240)
    line = (r.stdout or "").strip()
    print(line if line else "ESTATE-WATCHDOG-NO-OUTPUT")
except Exception as e:
    print(f"ESTATE-WATCHDOG-ERROR:{type(e).__name__}")
    sys.stderr.write(str(e)[:400])

sys.exit(0)
