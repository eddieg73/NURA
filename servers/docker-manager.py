#!/usr/bin/env python3
"""DOCKER MANAGER — the standing container-role: health + orphans + auto-restart + silent-when-ok (the cron!)."""
import subprocess, os, datetime

NODES = [("72.61.71.211", "Clinic"), ("72.60.163.140", "Lab"), ("195.35.32.113", "Edge")]
KEY = os.path.expanduser("~/.ssh/id_nura_clean")
LOG = os.path.expanduser("~/cron/output/docker-manager.log")
os.makedirs(os.path.dirname(LOG), exist_ok=True)

def sh(cmd, timeout=40):
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
        # the container census
        census = sh(f"ssh -o BatchMode=yes -o ConnectTimeout=8 -i {KEY} root@{ip} \"docker ps -a --format '{{{{.Names}}}}|{{{{.Status}}}}' 2>/dev/null | head -40\"")
        dead = [l for l in census.splitlines() if "Exited" in l or "Dead" in l or "Restarting" in l]
        # THE AUTO-PRUNE (the founder's mandate — the stale NEVER re-alerts, it gets REMOVED!)
        if dead:
            for l in dead:
                name = l.split()[0]
                sh(f"ssh -o BatchMode=yes -i ~/.ssh/id_nura_clean root@{ip} 'docker rm {name} 2>/dev/null; docker system prune -f >/dev/null 2>&1'")
                fixes.append(f"{ip}: removed {name}")
        # the known-good containers must be UP (the critical-list!)
        critical = {"docsgpt-oss-backend-1", "docsgpt-oss-postgres-1", "mirth-connect-mirth-connect-1", "n8n"}
        for c in critical:
            hit = [l for l in census.splitlines() if c in l]
            if hit and "Up" not in hit[0]:
                issues.append(f"{name}-{c}-DOWN")
                fixes.append(f"restart-{c}")
                sh(f"ssh -o BatchMode=yes -o ConnectTimeout=8 -i {KEY} root@{ip} \"docker start {c.split('-')[0]} 2>/dev/null || docker restart $(docker ps -aq --filter name={c}) 2>/dev/null\"")
        if len(dead) > 3:
            issues.append(f"{name}-dead-{len(dead)}")
    if not issues:
        return  # SILENT when healthy!
    report = ["🐳 DOCKER-MANAGER — container issues:", ""]
    report.append("· " + "\n· ".join(issues[:10]))
    if fixes:
        report.append("")
        report.append("Auto-restarts attempted: " + ", ".join(set(fixes)))
    print("\n".join(report))
    log(" | ".join(issues) + " fixes: " + ", ".join(fixes))

if __name__ == "__main__":
    main()
