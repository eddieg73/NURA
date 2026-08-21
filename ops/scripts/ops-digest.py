#!/usr/bin/env python3
"""OPS DIGEST — the twice-daily human summary: fleet + brain + keys + yesterday's issues. (The outage-alerts stay on the 15-min heartbeat!)"""
import subprocess, os, datetime

def sh(cmd, timeout=30):
    try:
        r = subprocess.run(cmd, shell=True, capture_output=True, text=True, timeout=timeout)
        return r.stdout.strip()
    except Exception:
        return "ERR"

def main():
    lines = ["📋 NURA OPS — " + datetime.datetime.now().strftime("%a %b %d, %H:%M EST")]
    # the fleet
    for ip, name in [("72.61.71.211", "Clinic"), ("72.60.163.140", "Lab"), ("195.35.32.113", "Edge")]:
        r = sh(f"ssh -o BatchMode=yes -o ConnectTimeout=6 -i ~/.ssh/id_nura_clean root@{ip} \"df -h / | tail -1 | awk '{{print \\$5}}'; docker ps -q 2>/dev/null | wc -l\" 2>&1")
        parts = r.split("\n")
        lines.append(f"· {name}: disk {parts[0] if parts else '?'} · {parts[1] if len(parts) > 1 else '?'} containers")
    # the brain
    b = sh("curl -s -m 6 -o /dev/null -w '%{http_code}' http://72.61.71.211:7091/api/health")
    lines.append(f"· Brain: HTTP {b}")
    # the keys
    missing = []
    for k in ["PERFEX_API_TOKEN", "TAVUS_API_KEY", "GROK_API_KEY"]:
        if sh(f"grep -c '^{k}=' /opt/data/profiles/nura/.env") == "0":
            missing.append(k.replace("_API", "").replace("_TOKEN", ""))
    if missing:
        lines.append(f"· Keys missing: {', '.join(missing)} (founder drops!)")
    # the recent errors (the heartbeat log, last 24h)
    log = os.path.expanduser("~/cron/output/heartbeat.log")
    errs = []
    if os.path.exists(log):
        for line in open(log).readlines()[-40:]:
            if "ISSUES" in line:
                errs.append(line.strip().split("] ")[-1])
    if errs:
        lines.append(f"· Recent issues: {errs[-2:]}")
    else:
        lines.append("· Recent 24h: no issues reported")
    print("\n".join(lines))

if __name__ == "__main__":
    main()
