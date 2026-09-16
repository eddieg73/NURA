#!/usr/bin/env python3
"""
Cron monitor shim for the lane state watchdog.

WHY THIS FILE EXISTS: cron `monitor` accepts only a bare filename relative to the profile's
scripts dir, so arguments cannot be passed. This shim runs the real watchdog with `--state` and
prints its deterministic state line, which is exactly what the monitor needs to diff tick to tick.

Determinism is the whole contract here: if this output changes between two ticks with no real
change, the monitor false-fires and the watchdog gets muted. `--state` emits only over-threshold
lanes, sorted, so an unchanged system produces a byte-identical line.

Stdout is the monitor signal. Everything diagnostic goes to stderr so it cannot pollute the signal.
"""
import subprocess
import sys

WATCHDOG = "/opt/data/profiles/nura/scripts/lane-state-watchdog.py"
PY = "/opt/hermes/.venv/bin/python3"

try:
    r = subprocess.run([PY, WATCHDOG, "--state"],
                       capture_output=True, text=True, timeout=180)
    line = (r.stdout or "").strip()
    if not line:
        # A silent watchdog is indistinguishable from a healthy one — surface that as a change.
        print("WATCHDOG-NO-OUTPUT")
        if r.stderr:
            sys.stderr.write(r.stderr[:400])
    else:
        print(line)
except Exception as e:
    print(f"WATCHDOG-ERROR:{type(e).__name__}")
    sys.stderr.write(str(e)[:400])

# Always exit 0: the monitor compares stdout, and a non-zero exit here would be indistinguishable
# from a broken shim. The state string itself carries the meaning.
sys.exit(0)
