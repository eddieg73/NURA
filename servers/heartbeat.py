#!/usr/bin/env python3
"""HEARTBEAT — the 15-minute pulse: the machine is NEVER inactive. Silent when healthy."""
import subprocess, os, datetime

LOG = os.path.expanduser("~/cron/output/heartbeat.log")
os.makedirs(os.path.dirname(LOG), exist_ok=True)

def sh(cmd, timeout=15):
    try:
        r = subprocess.run(cmd, shell=True, capture_output=True, text=True, timeout=timeout)
        return r.stdout.strip()
    except Exception:
        return ""

def main():
    issues = []
    # the brain-pulse
    # 2026-09-10 (incident-commander): retargeted from stale :7091 — no
    # listener exists for :7091 anywhere on the ai node (verified 23:09Z:
    # connection refused; no container/unit/config references it). The live
    # brain endpoint is hermes-gateway :8642/health -> 200 OK.
    b = sh("curl -s -m 6 -o /dev/null -w '%{http_code}' http://72.61.71.211:8642/health")
    if b != "200":
        issues.append(f"brain-{b}")
    # the gateway-pulse (the local hermes!)
    g = sh("pgrep -fc 'hermes' || echo 0")
    if g.strip() in ("", "0"):
        issues.append("hermes-gateway-down")
    # the fleet-pulse
    for ip in ["72.61.71.211", "72.60.163.140"]:
        r = sh(f"ssh -o BatchMode=yes -o ConnectTimeout=5 -i ~/.ssh/id_nura_clean root@{ip} 'echo ok'")
        if "ok" not in r:
            issues.append(f"node-{ip}")
    # the tunnel-pulse
    # 2026-09-10 (incident-commander): the `ss` binary is NOT installed in this
    # container, so `ss -tln | grep -c ':11434 '` always evaluated to 0 and
    # produced a permanent FALSE "tunnel-down" (~96/day). Probe the ollama
    # endpoint directly instead. Label kept as "tunnel-down" to preserve the
    # existing alert taxonomy.
    t = sh("curl -s -m 6 -o /dev/null -w '%{http_code}' http://127.0.0.1:11434/api/tags")
    if t.strip() != "200":
        issues.append("tunnel-down")
    if not issues:
        with open(LOG, "a") as f:
            f.write(f"[{datetime.datetime.now().isoformat()}] PULSE-OK\n")
        return  # SILENT!
    print(f"🫀 HEARTBEAT — issues: {' · '.join(issues)}")
    with open(LOG, "a") as f:
        f.write(f"[{datetime.datetime.now().isoformat()}] ISSUES: {' '.join(issues)}\n")

if __name__ == "__main__":
    main()
