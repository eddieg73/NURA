#!/usr/bin/env python3
"""
Two jobs:
  A. Fix rich_text truncation — Notion caps one rich_text object at 2000 chars, so any longer
     description was silently cut. Chunk into multiple objects so nothing is lost.
  B. ALIGNMENT REVIEW — is the whole Notion workforce surface coherent? Cross-check counts,
     orphans, duplicates, dangling references, and anything that contradicts itself.
"""
import collections
import json
import sys
import time

import requests

sys.path.insert(0, "/opt/data/scripts")
from notion_client import headers

H = headers()
BASE = "https://api.notion.com/v1"
ids = json.load(open("/opt/data/workforce_ids.json"))

print("=" * 96)
print("A. TRUNCATION AUDIT — how much text was cut?")
print("=" * 96)
iss = json.load(open("/opt/data/paperclip_recovery/issues.json"))
by_id = {i["id"]: (i.get("description") or "").strip() for i in iss}
over = {k: len(v) for k, v in by_id.items() if len(v) > 2000}
print(f"  source descriptions >2000 chars: {len(over)}")
if over:
    tot_lost = sum(v - 2000 for v in over.values())
    print(f"  total characters at risk of loss: {tot_lost}")
    print(f"  longest source description:       {max(over.values())} chars")


def all_rows(dbid):
    out, cur = [], None
    while True:
        b = {"page_size": 100}
        if cur:
            b["start_cursor"] = cur
        r = requests.post(f"{BASE}/databases/{dbid}/query", headers=H, json=b, timeout=60)
        d = r.json()
        out += d.get("results", [])
        if not d.get("has_more"):
            break
        cur = d.get("next_cursor")
    return out


def chunks(text):
    return [{"type": "text", "text": {"content": text[i:i + 2000]}}
            for i in range(0, len(text), 2000)][:100]


if over:
    print("\n  repairing truncated rows...")
    rows = all_rows(ids["tasks_db"])
    fixed = 0
    for row in rows:
        p = row["properties"]
        rid = "".join(x.get("plain_text", "") for x in p.get("Recovered ID", {}).get("rich_text", []))
        full = by_id.get(rid, "")
        if len(full) > 2000:
            r = requests.patch(f"{BASE}/pages/{row['id']}", headers=H,
                               json={"properties": {"Description": {"rich_text": chunks(full)}}},
                               timeout=45)
            if r.status_code < 300:
                fixed += 1
            time.sleep(0.28)
    print(f"  rows repaired: {fixed}")

# ---------------------------------------------------------------------------
print("\n" + "=" * 96)
print("B. ALIGNMENT REVIEW — does the workforce surface hang together?")
print("=" * 96)
reg = all_rows(ids["registry_db"])
tasks = all_rows(ids["tasks_db"])
log = all_rows(ids["checkin_db"])
issues = []


def txt(p, f):
    v = (p.get("properties") or {}).get(f) or {}
    t = v.get("type")
    if t == "rich_text":
        return "".join(x.get("plain_text", "") for x in (v.get(t) or []))
    if t == "title":
        return "".join(x.get("plain_text", "") for x in (v.get(t) or []))
    return ""


def sel(p, f):
    v = (p.get("properties") or {}).get(f) or {}
    s = v.get(v.get("type")) or {}
    return s.get("name", "") if isinstance(s, dict) else ""


print(f"\n  Agent Registry rows : {len(reg)}")
print(f"  Agent Tasks rows    : {len(tasks)}")
print(f"  Check-in Log rows   : {len(log)}")

# -- 1. description integrity
lens = [len(txt(t, "Description")) for t in tasks]
have = sum(1 for x in lens if x)
print(f"\n  1. DESCRIPTIONS: {have}/{len(tasks)} present, avg {sum(lens)//max(len(lens),1)} chars, "
      f"max {max(lens) if lens else 0}")
src_lens = [len(v) for v in by_id.values()]
ratio = (sum(lens) / sum(src_lens)) if src_lens else 0
print(f"     source total {sum(src_lens)} chars vs board total {sum(lens)} chars "
      f"= {ratio*100:.1f}% retained")
issues.append(("description coverage", have == len(tasks)))
issues.append(("description not truncated", ratio > 0.95))

# -- 2. assignee alignment: every task's assignee must exist in the registry
reg_names = {txt(a, "Agent") for a in reg}
task_assignees = collections.Counter(txt(t, "Assignee") for t in tasks)
orphan = {a: c for a, c in task_assignees.items() if a and a not in reg_names}
print(f"\n  2. ASSIGNEE ALIGNMENT: {len(task_assignees)} distinct assignees")
print(f"     orphaned (assignee not in the registry): {len(orphan)}")
for a, c in list(orphan.items())[:8]:
    print(f"       {a}  ({c} tasks)")
issues.append(("no orphaned assignees", len(orphan) == 0))

# -- 3. work distribution (the Paperclip failure mode)
print(f"\n  3. LOAD DISTRIBUTION (Paperclip's 91%-on-one-agent failure mode)")
top = task_assignees.most_common(6)
for a, c in top:
    bar = "#" * min(int(c / max(task_assignees.values()) * 32), 32)
    print(f"     {c:>4}  {a[:34]:<34} {bar}")
peak = task_assignees.most_common(1)[0][1] if task_assignees else 0
share = peak / len(tasks) * 100 if tasks else 0
print(f"     peak share: {share:.0f}%  (Paperclip was 91%)")
issues.append(("no single-agent overload", share < 50))

# -- 4. status/priority sanity
st = collections.Counter(sel(t, "Status") for t in tasks)
pr = collections.Counter(sel(t, "Priority") for t in tasks)
print(f"\n  4. STATUS:   {dict(st)}")
print(f"     PRIORITY: {dict(sorted(pr.items()))}")
issues.append(("all tasks have a status", "" not in st))
issues.append(("all tasks have a priority", "" not in pr))

# -- 5. founder gate count
gate = sum(1 for t in tasks if t["properties"].get("Founder Gate", {}).get("checkbox"))
print(f"\n  5. FOUNDER GATE: {gate}/{len(tasks)} require the founder")
p0gate = sum(1 for t in tasks
             if t["properties"].get("Founder Gate", {}).get("checkbox")
             and sel(t, "Priority") == "P0 Critical")
print(f"     P0 + founder-gated: {p0gate}")

# -- 6. registry integrity
rt = collections.Counter(sel(a, "Runtime") for a in reg)
div = collections.Counter(sel(a, "Division") for a in reg)
active = collections.Counter(sel(a, "Status") for a in reg)
print(f"\n  6. REGISTRY: runtime={dict(rt)}")
print(f"     divisions={dict(div)}")
print(f"     inherited statuses={dict(active)}")
issues.append(("registry has runtime binding", rt.get("Hermes cron", 0) > 0))
issues.append(("no duplicate agent names", len(reg_names) == len(reg)))

# -- 7. duplicate tasks
idents = [txt(t, "Identifier") for t in tasks]
dupe = [k for k, v in collections.Counter(idents).items() if v > 1 and k]
print(f"\n  7. DUPLICATE TASK IDENTIFIERS: {len(dupe)}  {dupe[:6]}")
issues.append(("no duplicate task identifiers", len(dupe) == 0))

# -- 8. check-in log coherence
logagents = collections.Counter(txt(l, "Agent") for l in log)
print(f"\n  8. CHECK-IN LOG: {len(log)} entries, agents={dict(logagents)}")
badlog = [a for a in logagents if a and a not in reg_names]
print(f"     log entries referencing unknown agents: {len(badlog)}")

print("\n" + "=" * 96)
print("ALIGNMENT VERDICT")
print("=" * 96)
for name, ok in issues:
    print(f"  [{'ALIGNED' if ok else 'MISALIGNED'}]  {name}")
print(f"\n  {sum(1 for _, o in issues if o)}/{len(issues)} checks aligned")
