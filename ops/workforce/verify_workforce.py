#!/usr/bin/env python3
"""END-TO-END VERIFICATION of the rebuilt workforce. Reads live state; assumes nothing."""
import glob
import json
import os
import subprocess
import sys

import requests

sys.path.insert(0, "/opt/data/scripts")
from notion_client import headers

H = headers()
BASE = "https://api.notion.com/v1"
OK, FAIL = [], []


def check(name, cond, detail=""):
    (OK if cond else FAIL).append(name)
    print(f"  [{'PASS' if cond else 'FAIL'}] {name}" + (f"  -- {detail}" if detail else ""))


def query_all(db):
    out, cur = [], None
    while True:
        b = {"page_size": 100}
        if cur:
            b["start_cursor"] = cur
        r = requests.post(f"{BASE}/databases/{db}/query", headers=H, json=b, timeout=60)
        if r.status_code >= 300:
            return None, r.status_code
        d = r.json()
        out += d.get("results", [])
        if not d.get("has_more"):
            break
        cur = d.get("next_cursor")
    return out, 200


print("=" * 96)
print("NURA WORKFORCE — END-TO-END VERIFICATION")
print("=" * 96)

ids = json.load(open("/opt/data/workforce_ids.json"))
REG, TASKS, LOG = ids["registry_db"], ids["tasks_db"], ids["checkin_db"]

# ---- 1. the three databases exist and are readable ------------------------
print("\n1. NOTION SURFACES (live reads)")
reg, rs = query_all(REG)
tasks, ts = query_all(TASKS)
log, ls = query_all(LOG)
check("Agent Registry readable", rs == 200, f"HTTP {rs}")
check("Agent Tasks readable", ts == 200, f"HTTP {ts}")
check("Check-in Log readable", ls == 200, f"HTTP {ls}")
check("Registry holds 72 agents", len(reg or []) == 72, f"{len(reg or [])} rows")
check("Tasks holds 148 rows", len(tasks or []) == 148, f"{len(tasks or [])} rows")
print(f"  Check-in Log entries so far: {len(log or [])}")

# ---- 2. migrated content is real, not shells -----------------------------
print("\n2. MIGRATED CONTENT INTEGRITY")


def txt(p, f):
    v = (p.get("properties") or {}).get(f) or {}
    return "".join(x.get("plain_text", "") for x in v.get(v.get("type"), []))


def sel(p, f):
    v = (p.get("properties") or {}).get(f) or {}
    s = v.get(v.get("type")) or {}
    return s.get("name", "") if isinstance(s, dict) else ""


with_desc = sum(1 for t in tasks if len(txt(t, "Description")) > 40)
check("Tasks carry recovered descriptions", with_desc > 100, f"{with_desc}/148 have body text")
with_assignee = sum(1 for t in tasks if (t.get("properties", {}).get("Assignee", {}).get("relation")))
check("Tasks linked to agents", with_assignee > 100, f"{with_assignee}/148 assigned")
prio = {}
for t in tasks:
    prio[sel(t, "Priority")] = prio.get(sel(t, "Priority"), 0) + 1
print(f"  priority spread: {dict(sorted(prio.items(), key=lambda kv: -kv[1]))}")
statuses = {}
for t in tasks:
    statuses[sel(t, "Status")] = statuses.get(sel(t, "Status"), 0) + 1
print(f"  status spread:   {dict(sorted(statuses.items(), key=lambda kv: -kv[1]))}")

runtime = {}
for a in reg:
    runtime[sel(a, "Runtime")] = runtime.get(sel(a, "Runtime"), 0) + 1
print(f"  runtime:         {runtime}")
check("Runtime binding applied", runtime.get("Hermes cron", 0) > 0,
      f"{runtime.get('Hermes cron',0)} STAFFED / {runtime.get('Not staffed',0)} inherited")

# ---- 3. the CLI works ----------------------------------------------------
print("\n3. CHECK-IN / CHECK-OUT CLI")
W = ["/opt/hermes/.venv/bin/python3", "/opt/data/scripts/workforce.py"]
r = subprocess.run(W + ["board"], capture_output=True, text=True, timeout=90)
check("workforce.py board exits 0", r.returncode == 0, f"exit {r.returncode}")
b = r.stdout
check("board reports real counts", "148" in b or "72" in b, b.strip().splitlines()[0][:70] if b.strip() else "no output")

r2 = subprocess.run(W + ["status"], capture_output=True, text=True, timeout=90)
check("workforce.py status exits 0", r2.returncode == 0, f"exit {r2.returncode}")

# ---- 4. cadence jobs exist ----------------------------------------------
print("\n4. SCRUM CADENCE")
jobs = json.load(open("/opt/data/profiles/nura/cron/jobs.json"))
jobs = jobs if isinstance(jobs, list) else jobs.get("jobs", [])
byname = {j.get("name", ""): j for j in jobs}
st = byname.get("daily standup")
check("daily standup scheduled", bool(st), f"id={st.get('job_id')} sched={st.get('schedule')} enabled={st.get('enabled')}" if st else "MISSING")
wk = byname.get("weekly scrum") or byname.get("weekly sprint review")
check("weekly sprint review present", bool(wk), f"id={wk.get('job_id')}" if wk else "MISSING")
total = len(jobs)
check("roster NOT ballooned (consolidation held)", total <= 100, f"{total} jobs total")

# ---- 5. standup actually ran -------------------------------------------
print("\n5. STANDUP EXECUTION EVIDENCE")
outs = sorted(glob.glob("/opt/data/profiles/nura/cron/output/*"), key=os.path.getmtime, reverse=True)
recent = [o for o in outs if os.path.isfile(o)][:6]
hit = None
for o in recent:
    try:
        blob = open(o, errors="ignore").read()
    except Exception:
        continue
    if "standup" in blob.lower() or "Standup" in blob:
        hit = o
        break
check("standup produced output", hit is not None, os.path.basename(hit) if hit else "no standup artifact found yet")
if hit:
    print(f"    artifact: {hit}  ({os.path.getsize(hit)} bytes)")

# ---- 6. source data preserved ------------------------------------------
print("\n6. RECOVERY ARTIFACT PRESERVED")
D = "/opt/data/paperclip_recovery"
for f, n in [("agents.json", 72), ("issues.json", 148), ("companies.json", 2)]:
    p = f"{D}/{f}"
    if os.path.exists(p):
        c = len(json.load(open(p)))
        check(f"{f} = {n}", c == n, f"{c} records")
    else:
        check(f"{f} exists", False, "missing")

print("\n" + "=" * 96)
print(f"RESULT: {len(OK)} passed, {len(FAIL)} failed")
if FAIL:
    for f in FAIL:
        print(f"  FAILED: {f}")
print("=" * 96)
sys.exit(1 if FAIL else 0)
