#!/usr/bin/env python3
"""UPGRADE LOOP — the constant-improvement engine: version-checks + repo-pulls + dependency-scans.
The founder's mandate: a way to CONSTANTLY upgrade the system for optimal performance."""
import subprocess, os, datetime, json, urllib.request

LOG = "/opt/data/profiles/nura/cron/output/upgrade-loop.log"
os.makedirs(os.path.dirname(LOG), exist_ok=True)
HOME = os.path.expanduser("~")

def sh(cmd, timeout=120):
    try:
        r = subprocess.run(cmd, shell=True, capture_output=True, text=True, timeout=timeout)
        return r.stdout.strip()
    except Exception:
        return "ERR"

def log(msg):
    with open(LOG, "a") as f:
        f.write(f"[{datetime.datetime.now().isoformat()}] {msg}\n")

def main():
    updates = []
    # 1. THE REPO-PULLS (the ecosystem + the app + the MCP-installs!)
    for repo in [f"{HOME}/hermes-ecosystem", f"{HOME}/nura_medical", f"{HOME}/mcp-installs"]:
        if os.path.isdir(repo):
            r = sh(f"cd {repo} && git pull --quiet 2>&1 | head -2")
            if r and "Already up to date" not in r and "ERR" not in r:
                updates.append(f"{os.path.basename(repo)}: {r[:60]}")
    # 2. THE NPM-OUTDATED (the wrapper-lanes!)
    n = sh("cd /opt/data/profiles/nura && npm outdated --json 2>/dev/null | head -c 200")
    if n and n != "ERR" and "{}" not in n:
        updates.append(f"npm-outdated: {n[:80]}")
    # 3. THE HERMES-VERSION (the GitHub-latest vs the local!)
    try:
        req = urllib.request.Request("https://api.github.com/repos/NousResearch/hermes-agent/releases/latest",
                                     headers={"User-Agent": "hermes-agency"})
        with urllib.request.urlopen(req, timeout=15) as r:
            latest = json.loads(r.read()).get("tag_name", "?")
        local = sh("hermes --version 2>/dev/null | head -1" if False else "/opt/hermes/bin/hermes --version 2>/dev/null | head -1")
        if latest and local and latest not in local:
            updates.append(f"hermes: local {local[:20]} vs latest {latest}")
    except Exception:
        pass
    # 4. THE FLEET-APT-CHECK (the read-only! — no unattended upgrades!)
    for ip, name in [("72.61.71.211", "Clinic"), ("72.60.163.140", "Lab")]:
        r = sh(f"ssh -o BatchMode=yes -o ConnectTimeout=6 -i ~/.ssh/id_nura_clean root@{ip} 'apt list --upgradable 2>/dev/null | wc -l' 2>&1")
        try:
            n = int(r.strip())
            if n > 1:
                updates.append(f"{name}: {n-1} apt-updates pending")
        except Exception:
            pass
    if updates:
        log(" | ".join(updates))
        print(f"🔄 UPGRADE-LOOP: {' | '.join(updates)}")
    # else: SILENT — the system's current!

if __name__ == "__main__":
    main()
