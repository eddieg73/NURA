#!/usr/bin/env python3
"""Find the real job-id field and pull execution history for the two erroring jobs."""
import json
import sqlite3

PROFILE = "/opt/data/profiles/nura"
j = json.load(open(f"{PROFILE}/cron/jobs.json"))
jobs = j if isinstance(j, list) else j.get("jobs", [])

print("ALL keys present on a job entry:")
keys = {}
for x in jobs:
    for k in x:
        keys[k] = keys.get(k, 0) + 1
for k, n in sorted(keys.items()):
    print(f"  {k:<24} on {n}/{len(jobs)} jobs")

print("\nID-BEARING FIELDS for the two targets:")
for x in jobs:
    if x.get("name") in ("evolution review", "emos gap audit"):
        print(f"\n  {x.get('name')}:")
        for k, v in x.items():
            if "id" in k.lower():
                print(f"    {k} = {v}")

c = sqlite3.connect(f"{PROFILE}/cron/executions.db")
c.row_factory = sqlite3.Row
print("\nDISTINCT job_ids in executions.db (with counts):")
rows = list(c.execute(
    "SELECT job_id, COUNT(*) n, MAX(started_at) last, "
    "SUM(CASE WHEN status='error' THEN 1 ELSE 0 END) errs "
    "FROM executions GROUP BY job_id ORDER BY last DESC LIMIT 30"))
for r in rows:
    print(f"  {str(r['job_id'])[:40]:<42} n={r['n']:<4} errs={r['errs']:<4} last={str(r['last'])[:19]}")

# map by name if the db stores one
print("\nLooking for the two jobs by any id match:")
targets = {x.get("name"): x for x in jobs if x.get("name") in ("evolution review", "emos gap audit")}
for name, x in targets.items():
    ids = [v for k, v in x.items() if "id" in k.lower() and v]
    print(f"\n  ── {name} ids={ids} ──")
    for jid in ids:
        for r in c.execute("SELECT * FROM executions WHERE job_id=? ORDER BY rowid DESC LIMIT 5", (jid,)):
            d = dict(r)
            print("    ", {k: str(v)[:120] for k, v in d.items() if v not in (None, "")})
