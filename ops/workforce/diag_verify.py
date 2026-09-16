#!/usr/bin/env python3
"""Diagnose the 3 verification failures: real property names, real content, standup output."""
import glob
import json
import os
import sys

import requests

sys.path.insert(0, "/opt/data/scripts")
from notion_client import headers

H = headers()
BASE = "https://api.notion.com/v1"
ids = json.load(open("/opt/data/workforce_ids.json"))

print("=" * 96)
print("A. ACTUAL SCHEMA — Agent Tasks")
print("=" * 96)
r = requests.get(f"{BASE}/databases/{ids['tasks_db']}", headers=H, timeout=45)
db = r.json()
props = db.get("properties", {})
for name, spec in props.items():
    print(f"  {name:<28} {spec.get('type')}")

print("\n" + "=" * 96)
print("B. SAMPLE ROW — raw properties, first task")
print("=" * 96)
r = requests.post(f"{BASE}/databases/{ids['tasks_db']}/query", headers=H,
                  json={"page_size": 2}, timeout=45)
rows = r.json().get("results", [])
if rows:
    for name, v in rows[0]["properties"].items():
        t = v.get("type")
        val = v.get(t)
        if t == "rich_text":
            val = "".join(x.get("plain_text", "") for x in (val or []))[:120]
        elif t == "relation":
            val = f"{len(val or [])} relation(s)"
        elif t == "title":
            val = "".join(x.get("plain_text", "") for x in (val or []))[:90]
        elif isinstance(val, dict):
            val = val.get("name")
        print(f"  {name:<28} {t:<10} {str(val)[:110]}")

print("\n" + "=" * 96)
print("C. RECOVERED SOURCE — did the raw data actually have bodies/assignees?")
print("=" * 96)
iss = json.load(open("/opt/data/paperclip_recovery/issues.json"))
print(f"  issues recovered: {len(iss)}")
sample = iss[0]
print(f"  keys present: {sorted(sample.keys())[:24]}")
for k in ("description", "body", "assignee_agent_id", "assignee_id", "identifier",
          "issue_number", "title", "priority", "status"):
    if k in sample:
        v = str(sample[k])
        print(f"    {k:<20} = {v[:90]}")
withdesc = sum(1 for i in iss if i.get("description") and len(str(i["description"])) > 40)
withass = sum(1 for i in iss if i.get("assignee_agent_id"))
print(f"\n  source issues with a real description: {withdesc}/{len(iss)}")
print(f"  source issues with an assignee_agent_id: {withass}/{len(iss)}")

print("\n" + "=" * 96)
print("D. STANDUP OUTPUT — where did it go?")
print("=" * 96)
for pat in ("/opt/data/profiles/nura/cron/output/*", "/opt/data/profiles/nura/cron/**/*"):
    g = sorted(glob.glob(pat, recursive=True), key=os.path.getmtime, reverse=True)[:8]
    if g:
        print(f"  {pat}")
        for f in g:
            if os.path.isfile(f):
                age = (os.path.getmtime(f))
                import time
                print(f"    {time.strftime('%m-%d %H:%M', time.localtime(age))}  "
                      f"{os.path.getsize(f):>8}  {f}")
