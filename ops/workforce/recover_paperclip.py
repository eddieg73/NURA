#!/usr/bin/env python3
"""
Extract EVERYTHING from the 2026-08-03 Paperclip snapshot into JSON.

Nothing is written to the live Paperclip instance. This is a read-only recovery so the
org can be rebuilt Hermes-native with no data loss.
"""
import collections
import glob
import gzip
import json
import os
import re

BK = sorted(glob.glob("/opt/data/paperclip-runtime.bak-20260803/instances/default/data/backups/*.sql.gz"),
            key=os.path.getmtime)[-1]
OUT = "/opt/data/paperclip_recovery"
os.makedirs(OUT, exist_ok=True)
print(f"source: {os.path.basename(BK)}  ({os.path.getsize(BK)/1024:.0f} KB)\n")

WANT = {
    "companies", "agents", "issues", "documents", "document_revisions", "folders",
    "projects", "comments", "issue_comments", "agent_config_revisions",
    "agent_runtime_state", "company_skills", "company_memberships",
    "heartbeat_runs", "heartbeat_run_events", "activity_log",
}

data = collections.defaultdict(list)
columns = {}
cur = None
with gzip.open(BK, "rt", encoding="utf-8", errors="replace") as fh:
    for line in fh:
        if line.startswith("COPY "):
            m = re.match(r'COPY\s+"?(\w+)"?\."?(\w+)"?\s*\(([^)]*)\)', line)
            if m:
                table = m.group(2)
                cur = table if table in WANT else None
                if cur:
                    columns[cur] = [c.strip().strip('"') for c in m.group(3).split(",")]
            else:
                cur = None
            continue
        if line.startswith("\\."):
            cur = None
            continue
        if cur:
            data[cur].append(line.rstrip("\n").split("\t"))

print("=" * 92)
print("RECOVERED TABLE INVENTORY")
print("=" * 92)
for t in sorted(data):
    print(f"  {t:<28} {len(data[t]):>6} rows   ({len(columns.get(t, []))} cols)")

# ---- agents (full records) ----
agents = []
if "agents" in data:
    cols = columns["agents"]
    for row in data["agents"]:
        rec = dict(zip(cols, row + [""] * (len(cols) - len(row))))
        agents.append(rec)
    with open(f"{OUT}/agents.json", "w") as f:
        json.dump(agents, f, indent=1)

# ---- issues (full records) ----
issues = []
if "issues" in data:
    cols = columns["issues"]
    for row in data["issues"]:
        rec = dict(zip(cols, row + [""] * (len(cols) - len(row))))
        issues.append(rec)
    with open(f"{OUT}/issues.json", "w") as f:
        json.dump(issues, f, indent=1)

# ---- companies ----
comps = []
if "companies" in data:
    cols = columns["companies"]
    for row in data["companies"]:
        comps.append(dict(zip(cols, row + [""] * (len(cols) - len(row)))))
    with open(f"{OUT}/companies.json", "w") as f:
        json.dump(comps, f, indent=1)

# ---- documents / folders ----
for t in ("documents", "folders", "company_skills"):
    if t in data:
        cols = columns[t]
        recs = [dict(zip(cols, r + [""] * (len(cols) - len(r)))) for r in data[t]]
        with open(f"{OUT}/{t}.json", "w") as f:
            json.dump(recs, f, indent=1)

print(f"\n  agents extracted:    {len(agents)}")
print(f"  issues extracted:    {len(issues)}")
print(f"  companies extracted: {len(comps)}")
print(f"\n  agent columns ({len(columns.get('agents', []))}):")
print(f"    {columns.get('agents', [])}")
print(f"\n  issue columns ({len(columns.get('issues', []))}):")
print(f"    {columns.get('issues', [])}")
print(f"\n-> {OUT}/")
