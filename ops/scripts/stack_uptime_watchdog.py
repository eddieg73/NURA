#!/usr/bin/env python3
"""stack_uptime_watchdog.py — bounded uptime watchdog for the NURA stack.

Checks: (a) local reachable endpoints (Hermes API, UI, carepilot, nuratech.ai),
(b) optionally VPS-side ports/domains listed in the config below.
Silent (exit 0, no output) when everything is up; prints a compact alert block
only when something is down. Designed for cron every 5 minutes (no_agent mode):
empty stdout = silent, non-empty = alert delivered.
"""
import datetime
import json
import os
import socket
import ssl
import subprocess
import sys
import urllib.request

CHECKS = [
    # (name, kind, target, expected)
    ("hermes_api",  "http",  "http://127.0.0.1:8642/health", 200),
    ("hermes_ui",   "http",  "http://127.0.0.1:3100", 200),
    ("carepilot",   "https", "https://carepilot.nuratech.ai", 200),
    ("nuratech",    "https", "https://nuratech.ai", 200),
]

# Optional VPS-side checks: enabled when this runs ON the VPS or SSH is available.
VPS_HTTP = [
    ("thairis_web", "http://127.0.0.1:8085/", 200),
    ("mirth_api",   "https://127.0.0.1:8443/api/server/version", 200),
]
VPS_PORTS = [6001, 6002, 4242, 8042]


def http_check(url, expected, timeout=6):
    try:
        req = urllib.request.Request(url, headers={"User-Agent": "nura-watchdog/1.0"})
        with urllib.request.urlopen(req, timeout=timeout) as r:
            return (r.status == expected, f"{r.status} (expected {expected})")
    except urllib.error.HTTPError as e:
        return (e.code == expected, f"HTTP {e.code} (expected {expected})")
    except Exception as e:
        return (False, f"{type(e).__name__}: {e}")


def port_check(host, port, timeout=3):
    try:
        with socket.create_connection((host, port), timeout=timeout):
            return (True, "open")
    except Exception as e:
        return (False, f"{type(e).__name__}: {e}")


def main():
    on_vps = os.path.exists("/var/run/docker.sock")
    failures = []

    for name, kind, target, expected in CHECKS:
        ok, detail = http_check(target, expected)
        if not ok:
            failures.append(f"{name}: {target} -> {detail}")

    if on_vps:
        for name, url, expected in VPS_HTTP:
            ok, detail = http_check(url, expected)
            if not ok:
                failures.append(f"{name}: {url} -> {detail}")
        for port in VPS_PORTS:
            ok, detail = port_check("127.0.0.1", port)
            if not ok:
                failures.append(f"port_{port}: {detail}")
        # container health
        try:
            out = subprocess.run(["docker", "ps", "--format", "{{.Names}}:{{.Status}}"],
                                 capture_output=True, text=True, timeout=10).stdout
            for line in out.splitlines():
                if "unhealthy" in line or "Exited" in line or "Restarting" in line:
                    failures.append(f"container: {line}")
        except Exception as e:
            failures.append(f"docker_ps: {e}")

    if failures:
        ts = datetime.datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S UTC")
        print(f"DOWN ALERT ({ts}) — {len(failures)} check(s) failing:")
        for f in failures:
            print(f"  - {f}")
        print("SLA budget note: 99% = <= 7.2h/mo downtime. Track incidents in the SLA log.")
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
