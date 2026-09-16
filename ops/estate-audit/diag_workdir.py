#!/usr/bin/env python3
"""
Can `evolution review`'s TERMINAL_CWD lock timeout be fixed by config?

Its 2026-09-01 failure:
  TimeoutError: Timed out waiting for the TERMINAL_CWD read lock after 660s — another cron job
  (a workdir writer, or long-running readers) has held it for longer than the cron inactivity limit.
  (#79768)

The named remedy: stagger the schedule, or remove the workdir from the contending job.
This finds which jobs hold a workdir and what else runs in the same window, before changing anything.
"""
import json
from collections import defaultdict

PROFILE = "/opt/data/profiles/nura"
j = json.load(open(f"{PROFILE}/cron/jobs.json"))
jobs = j if isinstance(j, list) else j.get("jobs", [])

print("=" * 92)
print("JOBS THAT DECLARE A workdir (these are the potential lock holders)")
print("=" * 92)
holders = [x for x in jobs if x.get("workdir")]
print(f"  count: {len(holders)} of {len(jobs)}")
for x in holders:
    sc = (x.get("schedule") or {})
    print(f"    {x.get('name','?'):<34} enabled={str(x.get('enabled')):<5} "
          f"expr={sc.get('expr',''):<16} workdir={x.get('workdir')}")

print("\n" + "=" * 92)
print("THE TWO BROKEN JOBS")
print("=" * 92)
for x in jobs:
    if x.get("name") in ("evolution review", "emos gap audit"):
        print(f"\n  ── {x.get('name')} ──")
        print(f"     id            : {x.get('id')}")
        print(f"     workdir       : {x.get('workdir')!r}")
        print(f"     script        : {x.get('script')!r}")
        print(f"     no_agent      : {x.get('no_agent')}")
        print(f"     enabled       : {x.get('enabled')}")
        print(f"     schedule      : {(x.get('schedule') or {}).get('expr')}")
        print(f"     next_run_at   : {x.get('next_run_at')}")

print("\n" + "=" * 92)
print("WHAT ELSE FIRES IN THE 09:00 HOUR (the contended window)")
print("=" * 92)
for x in jobs:
    sc = x.get("schedule") or {}
    expr = sc.get("expr", "")
    f = expr.split()
    if len(f) == 5 and f[1] in ("9", "*/1", "*"):
        if not x.get("enabled"):
            continue
        print(f"    {x.get('name','?'):<34} expr={expr:<16} workdir={x.get('workdir')!r}")

print("\n" + "=" * 92)
print("VERDICT LOGIC")
print("=" * 92)
er = next((x for x in jobs if x.get("name") == "evolution review"), None)
if er:
    if er.get("workdir"):
        print("  evolution review HAS a workdir -> it is itself a lock claimant.")
        print("  Removing its workdir is the #79768 remedy and is low-risk for a reporting job")
        print("  that reads files by absolute path (it does not need a cwd).")
    else:
        print("  evolution review has NO workdir -> the holder is ANOTHER job.")
        print("  Fix = stagger the schedule away from the contended window, not to touch this job.")
