#!/usr/bin/env python3
"""
Diagnose the two crons in error state found by the estate audit.

`evolution review`  - monthly, ENABLED, last_status=error since 2026-09-01
`emos gap audit`    - daily, DISABLED, last ran 2026-09-06

Neither raised anything. This looks at:
  - the job definition (prompt head, script, toolsets, deliver target)
  - executions.db rows for real error text
  - the output dir for the last artifact (a job can "run" and write nothing)
"""
import json
import os
import sqlite3
import time
from datetime import datetime, timezone

PROFILE = "/opt/data/profiles/nura"
JOBS = f"{PROFILE}/cron/jobs.json"
DB = f"{PROFILE}/cron/executions.db"

j = json.load(open(JOBS))
jobs = j if isinstance(j, list) else j.get("jobs", [])

TARGETS = ("evolution review", "emos gap audit")

print("=" * 92)
print("DEFINITIONS")
print("=" * 92)
for x in jobs:
    if x.get("name") in TARGETS:
        print(f"\n  ── {x.get('name')} ──")
        for k in ("job_id", "enabled", "state", "deliver", "script", "monitor_script",
                  "repeat", "created_at", "next_run_at", "last_run_at", "last_status",
                  "last_fire_error", "last_delivery_error", "enabled_toolsets"):
            if x.get(k) is not None:
                print(f"     {k:<20}: {str(x.get(k))[:110]}")
        sc = x.get("schedule")
        print(f"     {'schedule':<20}: {sc}")
        pr = (x.get("prompt") or "")
        print(f"     {'prompt_len':<20}: {len(pr)}")
        print(f"     prompt head        : {pr[:150].replace(chr(10),' / ')}")

print("\n" + "=" * 92)
print("EXECUTION HISTORY (real error text)")
print("=" * 92)
if os.path.exists(DB):
    c = sqlite3.connect(DB)
    c.row_factory = sqlite3.Row
    cols = [r[1] for r in c.execute("PRAGMA table_info(executions)")]
    print(f"  executions columns: {cols}")
    for x in jobs:
        if x.get("name") not in TARGETS:
            continue
        print(f"\n  ── {x.get('name')} ──")
        # match by job_id if present, else by name column if it exists
        rows = []
        for key in ("job_id", "job_name", "name"):
            if key in cols:
                val = x.get("job_id") if key == "job_id" else x.get("name")
                if val:
                    try:
                        rows = list(c.execute(
                            f"SELECT * FROM executions WHERE {key}=? ORDER BY rowid DESC LIMIT 6", (val,)))
                    except Exception as e:
                        rows = []
                    if rows:
                        break
        if not rows:
            print("     (no rows matched)")
            continue
        for r in rows:
            d = dict(r)
            out = []
            for k in ("status", "started_at", "finished_at", "duration_ms",
                      "error", "error_message", "output_path", "exit_code"):
                if k in d and d[k] not in (None, ""):
                    out.append(f"{k}={str(d[k])[:150]}")
            print("     " + " | ".join(out))

print("\n" + "=" * 92)
print("LAST OUTPUT ARTIFACTS (did it actually write anything?)")
print("=" * 92)
for x in jobs:
    if x.get("name") not in TARGETS:
        continue
    jid = x.get("job_id") or "?"
    d = f"{PROFILE}/cron/output/{jid}"
    print(f"\n  ── {x.get('name')}  (dir {d}) ──")
    if not os.path.isdir(d):
        print("     NO OUTPUT DIR")
        continue
    files = sorted(os.listdir(d))
    print(f"     files: {len(files)}")
    for f in files[-4:]:
        p = os.path.join(d, f)
        st = os.stat(p)
        age_h = (time.time() - st.st_mtime) / 3600
        print(f"       {f:<44} {st.st_size:>8} B  {age_h/24:.1f} d old")
        try:
            head = open(p, errors="ignore").read()[:200].replace("\n", " ")
            print(f"         head: {head}")
        except Exception:
            pass
