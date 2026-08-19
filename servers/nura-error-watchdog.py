#!/usr/bin/env python3
"""NURA ERROR WATCHDOG — captures fleet errors, diffs against the known baseline,
prints ONLY new errors (repeating known ones stay silent). The cron delivers stdout."""
import subprocess, hashlib, json, os, datetime, re

NODES = ["72.61.71.211", "72.60.163.140", "195.35.32.113"]
KEY = os.path.expanduser("~/.ssh/id_nura_clean")
BASELINE = os.path.expanduser("~/nura-ops/error-baseline.json")
SINCE = "45m"  # look back per run (cron every 1h = 45m overlap for safety)

def ssh(node, cmd, timeout=25):
    try:
        r = subprocess.run(["ssh", "-o", "BatchMode=yes", "-o", "ConnectTimeout=8",
                            "-i", KEY, f"root@{node}", cmd],
                           capture_output=True, text=True, timeout=timeout)
        return r.stdout
    except Exception:
        return ""

def collect():
    events = []
    for node in NODES:
        out = ssh(node, f"docker ps -a --format '{{{{.Names}}}}|{{{{.Status}}}}' | grep -iE 'exited|restarting' | head -12; echo '---LOGS---'; for c in $(docker ps -a --format '{{{{.Names}}}}' | head -30); do docker logs --since {SINCE} $c 2>&1 | grep -iE 'error|traceback|panic|fatal|oom' | tail -2 | sed \"s|^|[$c] |\"; done; echo '---JOURNAL---'; journalctl -p err --since '{SINCE}' --no-pager 2>/dev/null | grep -vE 'audit|apparmor' | tail -8")
        for line in out.splitlines():
            line = line.strip()
            if not line or line.startswith("---"):
                continue
            if "|" in line and ("Exited" in line or "Restarting" in line):
                events.append({"node": node, "type": "container", "msg": line})
            elif line.startswith("[") or line.startswith("ERROR") or "Traceback" in line or "panic" in line.lower():
                events.append({"node": node, "type": "log", "msg": line[:220]})
    return events

def main():
    os.makedirs(os.path.dirname(BASELINE), exist_ok=True)
    seen = set()
    if os.path.exists(BASELINE):
        try:
            seen = set(json.load(open(BASELINE)))
        except Exception:
            seen = set()
    events = collect()
    new = []
    for e in events:
        h = hashlib.md5(f"{e['node']}|{e['type']}|{e['msg'][:160]}".encode()).hexdigest()
        if h not in seen:
            new.append(e)
            seen.add(h)
    json.dump(sorted(seen), open(BASELINE, "w"))
    if new:
        ts = datetime.datetime.utcnow().strftime("%H:%MZ")
        print(f"🚨 NURA NEW ERRORS ({ts}) — {len(new)} new:")
        for e in new[:12]:
            print(f"· [{e['node']}] {e['type']}: {e['msg'][:160]}")
        print(f"(seen total: {len(seen)} — the repeating ones are in the baseline, silent)")

if __name__ == "__main__":
    main()
