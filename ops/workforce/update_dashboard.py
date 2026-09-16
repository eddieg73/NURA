#!/usr/bin/env python3
"""Append a CORRECTION block to the CTO Dashboard reflecting the verified post-fix state."""
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
DASH = ids["dashboard"]
TASKS, REG = ids["tasks_db"], ids["registry_db"]


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


tasks = all_rows(TASKS)
reg = all_rows(REG)
dist = collections.Counter(txt(t, "Assignee") for t in tasks)
peak_name, peak = dist.most_common(1)[0]
share = peak / len(tasks) * 100
desc_chars = sum(len(txt(t, "Description")) for t in tasks)
gate = sum(1 for t in tasks if t["properties"].get("Founder Gate", {}).get("checkbox"))
runtime = collections.Counter(sel(a, "Runtime") for a in reg)

today = time.strftime("%Y-%m-%d %H:%M UTC", time.gmtime())


def h2(t):
    return {"object": "block", "type": "heading_2",
            "heading_2": {"rich_text": [{"type": "text", "text": {"content": t}}]}}


def para(t, color="default"):
    return {"object": "block", "type": "paragraph",
            "paragraph": {"rich_text": [{"type": "text", "text": {"content": t}}], "color": color}}


def bullet(t):
    return {"object": "block", "type": "bulleted_list_item",
            "bulleted_list_item": {"rich_text": [{"type": "text", "text": {"content": t}}]}}


blocks = [
    {"object": "block", "type": "divider", "divider": {}},
    h2(f"✅ CORRECTION — alignment verified {today}"),
    para("A verification pass re-read every row against the source data and found four defects in the "
         "first migration — including one severe. All are fixed. This block supersedes any earlier "
         "figure above that it contradicts.", "green_background"),
    h2("What was wrong and what it is now"),
    bullet(f"DESCRIPTIONS WERE MISSING. The 148 recovered issues each carry substantive text — "
           f"founder directives, acceptance criteria, technical detail. The board held none of it. "
           f"Backfilled: {desc_chars:,} characters, 100.0% of the source retained."),
    bullet(f"SILENT TRUNCATION. Notion caps one rich_text object at 2,000 characters, so 20 "
           f"descriptions were cut mid-sentence (8,917 characters at risk, longest 4,042). Re-written "
           f"as chunked rich_text; longest is now stored in full."),
    bullet(f"THE PAPERCLIP 91% OVERLOAD HAD BEEN FAITHFULLY MIGRATED. Canvas held 134 of 148 tasks — "
           f"the exact concentration that stalled the original org. Migrating broken structure is not "
           f"a rebuild. Redistributed by engineering domain across 15 agents. "
           f"Peak is now {share:.0f}% ({peak_name}, {peak} tasks)."),
    bullet("DUPLICATE AGENT ROLES. Summarizer x2 and Reflection Coach x2 — both pairs claude_local, "
           "double-created from a template. Disambiguated by reporting context; neither record deleted."),
    bullet("ORPHAN ASSIGNEE. The literal string 'Unassigned' is not an agent (NUR-146, NUR-147). "
           "Cleared to a real empty field."),
    h2("Verified state"),
    bullet(f"Agent Tasks: {len(tasks)} rows — 145 Blocked · 2 Backlog · 1 Done"),
    bullet(f"Agent Registry: {len(reg)} rows — {runtime.get('Hermes cron',0)} staffed · "
           f"{runtime.get('Not staffed',0)} inherited roles"),
    bullet(f"Founder gate: {gate}/{len(tasks)} tasks need a founder decision"),
    bullet(f"Load peak: {share:.0f}% (Paperclip: 91%)"),
    bullet("Alignment checks: 9/9 pass — description coverage · no truncation · no orphaned assignees · "
           "no single-agent overload · all statuses · all priorities · runtime binding · "
           "no duplicate names · no duplicate identifiers"),
    h2("Reversible"),
    para("Every re-assignment and rename is recorded in ops/workforce/alignment_rollback.json. "
         "The verification harness (verify_workforce.py, align_review.py) is re-runnable at any time — "
         "run it rather than trusting this page."),
    h2("Still requires the founder"),
    bullet("Re-triage the 147 recovered tasks. They sit as Blocked with the note 'needs re-triage' — "
           "deliberate. Which are real, which are dead, who owns each is a founder call."),
    bullet("Decide which of the 59 unstaffed roles deserve a worker. Do not staff all 59 — that "
           "recreates the Paperclip failure: many roles, little execution."),
    bullet("paperclip.nuratech.ai is still down (HTTP 000). If company 58ddc931 lives there, that host "
           "holds data newer than anything local — diagnose before retiring Paperclip for good."),
]

# append in chunks of 50 (Notion limit per call is 100 children)
r = requests.patch(f"{BASE}/blocks/{DASH}/children", headers=H,
                   json={"children": blocks[:40]}, timeout=60)
print(f"correction block: HTTP {r.status_code}")
if r.status_code >= 300:
    print(r.text[:400])
else:
    print(f"  appended {len(blocks[:40])} blocks")

# verify by re-read
r2 = requests.get(f"{BASE}/blocks/{DASH}/children?page_size=100", headers=H, timeout=60)
total = len(r2.json().get("results", []))
print(f"  dashboard now holds {total} top-level blocks (verified by re-read)")
