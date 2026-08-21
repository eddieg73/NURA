#!/usr/bin/env python3
"""Paperclip CEO SLA watchdog — 99.9% uptime (≤43.8 min/mo budget).
Checks :3100/api/health every 2 min; auto-recovers via the sanctioned manager;
appends to the uptime ledger. Silent when healthy (no_agent cron pattern)."""
import datetime, os, subprocess, sys, time

HEALTH_URL = "http://127.0.0.1:3100/health"  # corrected 2026-08-02: /api/health 404s; /health is live
LEDGER = "/opt/data/profiles/nura/data/uptime/paperclip.log"
os.makedirs(os.path.dirname(LEDGER), exist_ok=True)
MANAGER = "/opt/data/scripts/paperclip_server_manager.py"

def healthy():
    try:
        out = subprocess.run(["curl", "-s", "-m", "5", "-o", "/dev/null", "-w", "%{http_code}", HEALTH_URL],
                             capture_output=True, text=True, timeout=10).stdout.strip()
        return out == "200"
    except Exception:
        return False

def log(line):
    with open(LEDGER, "a") as f:
        f.write(line + "\n")

now = datetime.datetime.utcnow().isoformat(timespec="seconds")
if healthy():
    log(f"UP {now}")
    sys.exit(0)  # silent when healthy

# Down: verify twice before acting (avoid false recovery loops)
time.sleep(3)
if healthy():
    log(f"UP {now} (transient)")
    sys.exit(0)

log(f"DOWN {now} starting-recovery")
try:
    subprocess.run(["python3", MANAGER, "start"], capture_output=True, text=True, timeout=60)
except Exception as e:
    print(f"PAPERCLIP RECOVERY FAILED: {str(e)[:120]}")
    sys.exit(0)

# wait up to 60s for recovery
for _ in range(12):
    time.sleep(5)
    if healthy():
        log(f"UP {now} (recovered)")
        print("PAPERCLIP RECOVERED: server was down, manager restarted it, health OK now")
        sys.exit(0)

print("PAPERCLIP DOWN: server unreachable and recovery did not clear it within 60s — operator intervention needed")
