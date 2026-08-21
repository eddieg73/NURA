#!/usr/bin/env python3
"""The nightly build-queue triage: the audit the standing queue against the pre-build-triage gates.
Silent when clean; the drift/duplicate findings → the vault log + the one-line alert.
"""
import os
import re
from datetime import datetime

DASHBOARD = "/opt/data/Obsidian Vault/NURA-OS/Status-Dashboard.md"
LOG = "/opt/data/Obsidian Vault/NURA-OS/Infra/Build-Queue-Triage-Log.md"
SCRIPTS_DIRS = ["/opt/data/scripts", "/opt/data/profiles/nura/scripts"]

def main():
    findings = []

    # Gate 1: the dashboard's the queue section exists + the items are tracked
    if os.path.exists(DASHBOARD):
        txt = open(DASHBOARD).read()
        m = re.search(r"## The build queue\n(.*?)(\n## |\Z)", txt, re.S)
        queue = m.group(1) if m else ""
        items = [l.strip("- ").strip() for l in queue.split("\n") if l.strip().startswith("-")]
        # Gate 2: the queue items that have gone stale (the same item listed for >7 days is flagged by the log review, not here)
    else:
        findings.append("the Status-Dashboard is missing — the queue has no home")

    # Gate 3: the obvious duplicate-signal scan — the new scripts named like the existing ones
    names = set()
    for d in SCRIPTS_DIRS:
        if os.path.isdir(d):
            for f in os.listdir(d):
                if f.endswith((".py", ".sh")):
                    base = re.sub(r"[-_v0-9]+\.(py|sh)$", "", f)
                    if base in names:
                        findings.append(f"the duplicate-signal: the {f} vs the earlier {base}*")
                    names.add(base)

    if findings:
        ts = datetime.utcnow().strftime("%Y-%m-%d %H:%M")
        with open(LOG, "a") as f:
            f.write(f"\n## {ts}\n" + "\n".join(f"- {x}" for x in findings) + "\n")
        print("⚠️ the build-queue triage found: " + "; ".join(findings[:3]))
    # else: silent — the queue is clean

if __name__ == "__main__":
    main()
