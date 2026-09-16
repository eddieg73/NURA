#!/usr/bin/env python3
"""
FIX the 3 misalignments the review found:

  1. ORPHAN ASSIGNEE  - the literal string "Unassigned" isn't an agent. Use a real empty field.
  2. SINGLE-AGENT OVERLOAD - Canvas holds 134/148 (91%). This is the exact Paperclip pathology the
     rebuild exists to eliminate. Faithfully migrating broken structure is not a rebuild.
  3. DUPLICATE AGENT NAMES - the registry has name collisions. Real agents need unambiguous identity.
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


def sel(p, f):
    v = (p.get("properties") or {}).get(f) or {}
    s = v.get(v.get("type")) or {}
    return s.get("name", "") if isinstance(s, dict) else ""


# ---- 3. FIND the duplicate agent names -----------------------------------
print("=" * 96)
print("3. DUPLICATE AGENT NAMES")
print("=" * 96)
reg = all_rows(REG)
names = collections.Counter(txt(a, "Agent") for a in reg)
dupes = {n: c for n, c in names.items() if c > 1}
print(f"  duplicate names: {len(dupes)}")
for n, c in dupes.items():
    print(f"\n  '{n}' x{c}:")
    for a in reg:
        if txt(a, "Agent") == n:
            print(f"      id={a['id'][:8]}  title={txt(a,'Title')[:46]:<46} "
                  f"division={sel(a,'Division'):<18} company={txt(a,'Company')[:28]}")

# ---- 1. orphan assignees -------------------------------------------------
print("\n" + "=" * 96)
print("1. ORPHAN ASSIGNEE ('Unassigned' is not an agent)")
print("=" * 96)
tasks = all_rows(TASKS)
orphans = [t for t in tasks if txt(t, "Assignee") == "Unassigned"]
print(f"  rows with the literal 'Unassigned': {len(orphans)}")
for t in orphans:
    print(f"    {txt(t,'Identifier')}  {txt(t,'Task')[:64]}")

# ---- 2. measure the overload --------------------------------------------
print("\n" + "=" * 96)
print("2. LOAD OVERLOAD — Canvas holds 91%")
print("=" * 96)
canvas = [t for t in tasks if txt(t, "Assignee") == "Canvas"]
print(f"  Canvas tasks: {len(canvas)}/{len(tasks)}")
canvas_titles = [txt(t, "Task") for t in canvas]

# Cluster Canvas's load into real workstreams so it can be REDISTRIBUTED to
# agents who actually exist and are staffed.
CLUSTERS = [
    (r"(?i)\bflutter|mobile|ios|android|app store|apk|expo|react native\b", "Pixel",
     "Mobile / Flutter engineering"),
    (r"(?i)\bmirth|hl7|fhir|interface|integration|bridge|connector\b", "Meridian",
     "Integration & interface engineering"),
    (r"(?i)\bris|pacs|dicom|radiology|imaging\b", "Frame",
     "RIS/PACS & imaging"),
    (r"(?i)\bopenemr|ehr|chart|clinical|patient|raf|hcc|coding\b", "Florence",
     "EHR & clinical platform"),
    (r"(?i)\bnmi|payment|billing|rcm|claim|invoice|revenue\b", "Midas",
     "Revenue cycle & payments"),
    (r"(?i)\btwilio|sms|voice|telephony|call\b", "Echo",
     "Telephony & messaging"),
    (r"(?i)\bn8n|workflow|automation|zapier|webhook\b", "Loom",
     "Workflow automation"),
    (r"(?i)\bdeploy|docker|vps|server|infra|provision|ssl|dns\b", "Helm",
     "Infrastructure & deployment"),
    (r"(?i)\bsecurity|auth|sso|oauth|key|secret|hardening\b", "Sentinel",
     "Security & access"),
    (r"(?i)\bnotion|document|doc|spec|report|sop\b", "Nexus",
     "Documentation & knowledge"),
    (r"(?i)\bmarketing|brand|content|social|website|seo\b", "Iris",
     "Marketing & brand"),
    (r"(?i)\blegal|contract|patent|reg a|securities|counsel|compliance\b",
     "Legal & Contracts Lead", "Legal & compliance"),
    (r"(?i)\bresearch|study|literature|evidence|benchmark\b", "Head of Research",
     "Research"),
    (r"(?i)\bcost|spend|budget|financ|accounting\b", "Controller",
     "Finance & cost"),
]
import re

def cluster_of(title):
    for pat, agent, label in CLUSTERS:
        if re.search(pat, title):
            return agent, label
    return "Orion", "Engineering (default to CTO)"


buckets = collections.Counter()
for title in canvas_titles:
    a, _ = cluster_of(title)
    buckets[a] += 1
print(f"\n  proposed redistribution of Canvas's {len(canvas)} tasks:")
for a, c in buckets.most_common():
    print(f"    {c:>4}  -> {a}")
print(f"\n  agents receiving work: {len(buckets)}  (was effectively 1)")
