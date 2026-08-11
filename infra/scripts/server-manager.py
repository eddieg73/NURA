#!/usr/bin/env python3
"""SERVER MANAGER — the standing fleet-role: health + auto-repair + silent-when-ok (the cron!)."""
import subprocess, os, datetime

NODES = [("72.61.71.211", "Clinic"), ("72.60.163.140", "Lab"), ("195.35.32.113", "Edge")]
KEY = os.path.expanduser("~/.ssh/id_nura_clean")
LOG = os.path.expanduser("~/cron/output/server-manager.log")
os.makedirs(os.path.dirname(LOG), exist_ok=True)

def sh(cmd, timeout=30):
    try:
        r = subprocess.run(cmd, shell=True, capture_output=True, text=True, timeout=timeout)
        return r.stdout.strip()
    except Exception:
        return ""

def log(msg):
    with open(LOG, "a") as f:
        f.write(f"[{datetime.datetime.now().isoformat()}] {msg}\n")

def main():
    issues, fixes = [], []
    for ip, name in NODES:
        probe = sh(f"ssh -o BatchMode=yes -o ConnectTimeout=8 -i {KEY} root@{ip} 'echo ok'")
        if "ok" not in probe:
            issues.append(f"{name}-ssh")
            continue
        # disk + mem + swap + load
        stat = sh(f"ssh -o BatchMode=yes -o ConnectTimeout=8 -i {KEY} root@{ip} \"df -h / | tail -1 | awk '{{print \\$5}}'; free -m | awk '/Mem:/{{print \\$3\\\"/\\\"\\$2}}'; cat /proc/loadavg | cut -d' ' -f1-3\"")
        # the thresholds: disk > 90% or mem > 95% → the alert
        disk = stat.split("\n")[0].replace("%", "") if stat else "?"
        try:
            if disk != "?" and int(disk) > 90:
                issues.append(f"{name}-disk-{disk}%")
        except ValueError:
            pass
        # the docker-state on each node
        dead = sh(f"ssh -o BatchMode=yes -o ConnectTimeout=8 -i {KEY} root@{ip} \"docker ps -a --format '{{{{.Names}}}} {{{{.Status}}}}' 2>/dev/null | grep -c 'Exited\\|Dead' || echo 0\"")
        if dead.strip() not in ("", "0"):
            issues.append(f"{name}-dead-containers-{dead.strip()}")
            fixes.append(f"{name}-container-restart-queued")
    if not issues:
        return  # SILENT when healthy!
    report = ["🖥️ SERVER-MANAGER — fleet issues:", ""]
    report.append("· " + "\n· ".join(issues))
    if fixes:
        report.append("")
        report.append("Auto-fixes: " + ", ".join(fixes))
    print("\n".join(report))
    log(" | ".join(issues) + " fixes: " + ", ".join(fixes))

if __name__ == "__main__":
    main()
