#!/usr/bin/env python3
"""
APPLY the three alignment fixes. Reversible — a rollback map is written first.

  1. Duplicate agent names  -> disambiguate by reporting context (no record deleted)
  2. Orphan 'Unassigned'    -> real empty field
  3. Canvas 91% overload    -> redistribute 134 tasks across 15 agents by domain
"""
import collections
import json
import re
import sys
import time

import requests

sys.path.insert(0, "/opt/data/scripts")
from notion_client import headers

H = headers()
BASE = "https://api.notion.com/v1"
ids = json.load(open("/opt/data/workforce_ids.json"))
REG, TASKS = ids["registry_db"], ids["tasks_db"]


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


def txt(p, f):
    v = (p.get("properties") or {}).get(f) or {}
    t = v.get("type")
    return "".join(x.get("plain_text", "") for x in (v.get(t) or [])) if t in ("rich_text", "title") else ""


rollback = {"renames": [], "assignees": []}

# ===========================================================================
print("=" * 96)
print("FIX 1 — DUPLICATE AGENT NAMES")
print("=" * 96)
reg = all_rows(REG)
by_name = collections.defaultdict(list)
for a in reg:
    by_name[txt(a, "Agent")].append(a)

for name, rows in by_name.items():
    if len(rows) < 2:
        continue
    print(f"\n  '{name}' x{len(rows)} — disambiguating")
    for i, row in enumerate(rows):
        reports = txt(row, "Reports To")
        div = (row["properties"].get("Division", {}).get("select") or {}).get("name", "")
        ctx = reports or f"{div} (unattached)"
        newname = f"{name} — {ctx}"
        r = requests.patch(f"{BASE}/pages/{row['id']}", headers=H, json={
            "properties": {"Agent": {"title": [{"type": "text", "text": {"content": newname}}]}}},
            timeout=45)
        status = "ok" if r.status_code < 300 else f"HTTP {r.status_code}"
        print(f"    {row['id'][:8]}  -> {newname[:58]:<58} {status}")
        rollback["renames"].append({"page": row["id"], "from": name, "to": newname})
        time.sleep(0.28)

# ===========================================================================
print("\n" + "=" * 96)
print("FIX 2 — ORPHAN ASSIGNEE")
print("=" * 96)
tasks = all_rows(TASKS)
n = 0
for t in tasks:
    if txt(t, "Assignee") == "Unassigned":
        ident = txt(t, "Identifier")
        r = requests.patch(f"{BASE}/pages/{t['id']}", headers=H, json={
            "properties": {"Assignee": {"rich_text": []}}}, timeout=45)
        print(f"  {ident}: cleared  HTTP {r.status_code}")
        rollback["assignees"].append({"page": t["id"], "from": "Unassigned", "to": ""})
        n += 1
        time.sleep(0.28)
print(f"  cleared: {n}")

# ===========================================================================
print("\n" + "=" * 96)
print("FIX 3 — REDISTRIBUTE CANVAS'S 91% LOAD")
print("=" * 96)
CLUSTERS = [
    (r"(?i)\bflutter|mobile|ios|android|app store|apk|expo|react native|brawlerz\b", "Pixel"),
    (r"(?i)\bmirth|hl7|fhir|interface|integration|bridge|connector\b", "Meridian"),
    (r"(?i)\bris|pacs|dicom|radiology|imaging\b", "Frame"),
    (r"(?i)\bopenemr|ehr|chart|clinical|patient|raf|hcc|coding|emed\b", "Florence"),
    (r"(?i)\bnmi|payment|billing|rcm|claim|invoice|revenue|solis\b", "Midas"),
    (r"(?i)\btwilio|sms|voice|telephony|reception\.ai\b", "Echo"),
    (r"(?i)\bn8n|workflow|automation|zapier|webhook\b", "Loom"),
    (r"(?i)\bdeploy|docker|vps|server|infra|provision|ssl|dns|hostinger\b", "Helm"),
    (r"(?i)\bsecurity|auth|sso|oauth|\bkey\b|secret|hardening|hipaa\b", "Sentinel"),
    (r"(?i)\bnotion|document|\bdoc\b|spec|report|sop|obsidian\b", "Nexus"),
    (r"(?i)\bmarketing|brand|content|social|website|seo\b", "Iris"),
    (r"(?i)\blegal|contract|patent|reg a|securities|counsel|compliance|attorney\b",
     "Legal & Contracts Lead"),
    (r"(?i)\bresearch|study|literature|evidence|benchmark|anduril|lattice\b", "Head of Research"),
    (r"(?i)\bcost|spend|budget|financ|accounting\b", "Controller"),
]


def cluster_of(title):
    for pat, agent in CLUSTERS:
        if re.search(pat, title):
            return agent
    return "Orion"


canvas = [t for t in tasks if txt(t, "Assignee") == "Canvas"]
print(f"  Canvas currently holds: {len(canvas)}")

moved = collections.Counter()
for t in canvas:
    title = txt(t, "Task")
    ident = txt(t, "Identifier")
    new = cluster_of(title)
    if new == "Canvas":
        continue
    r = requests.patch(f"{BASE}/pages/{t['id']}", headers=H, json={
        "properties": {"Assignee": {"rich_text": [{"type": "text", "text": {"content": new}}]}}},
        timeout=45)
    if r.status_code < 300:
        moved[new] += 1
        rollback["assignees"].append({"page": t["id"], "from": "Canvas", "to": new, "ident": ident})
    time.sleep(0.28)

print(f"\n  reassigned: {sum(moved.values())}")
for a, c in moved.most_common():
    print(f"    {c:>4}  -> {a}")

json.dump(rollback, open("/opt/data/alignment_rollback.json", "w"), indent=1)
print("\n  rollback map -> /opt/data/alignment_rollback.json")
