#!/usr/bin/env python3
"""Build the CTO Dashboard page — the single command view of the workforce."""
import collections
import json
import sys
import time
import requests

sys.path.insert(0, "/opt/data/scripts")
from notion_client import headers

H = headers()
BASE = "https://api.notion.com/v1"
IDS = json.load(open("/opt/data/workforce_ids.json"))
WF = IDS["workforce_page"]
REG, TASK, CHK = IDS["registry_db"], IDS["tasks_db"], IDS["checkin_db"]


def q(db):
    out, cur = [], None
    while True:
        b = {"page_size": 100}
        if cur:
            b["start_cursor"] = cur
        r = requests.post(f"{BASE}/databases/{db}/query", headers=H, json=b, timeout=45)
        d = r.json()
        out += d.get("results", [])
        if not d.get("has_more"):
            break
        cur = d.get("next_cursor")
    return out


def p(page, field):
    v = (page.get("properties") or {}).get(field) or {}
    t = v.get("type")
    if t in ("rich_text", "title"):
        return "".join(x.get("plain_text", "") for x in v.get(t, []))
    if t == "select":
        return (v.get("select") or {}).get("name", "")
    if t == "date":
        return (v.get("date") or {}).get("start", "")
    return ""


tasks = q(TASK)
agents = q(REG)
checks = q(CHK)

by_status = collections.Counter(p(t, "Status") for t in tasks)
by_pri = collections.Counter(p(t, "Priority") for t in tasks)
by_assignee = collections.Counter(p(t, "Assignee") for t in tasks)
reg_status = collections.Counter(p(a, "Status") for a in agents)
founder_gated = sum(1 for t in tasks if (t.get("properties", {}).get("Founder Gate", {}) or {}).get("checkbox"))

last = {}
for c in sorted(checks, key=lambda x: p(x, "When"), reverse=True):
    a = p(c, "Agent")
    if a and a not in last:
        last[a] = (p(c, "Event"), p(c, "When"))


def h2(t):
    return {"object": "block", "type": "heading_2",
            "heading_2": {"rich_text": [{"type": "text", "text": {"content": t}}]}}


def h3(t):
    return {"object": "block", "type": "heading_3",
            "heading_3": {"rich_text": [{"type": "text", "text": {"content": t}}]}}


def para(t):
    return {"object": "block", "type": "paragraph",
            "paragraph": {"rich_text": [{"type": "text", "text": {"content": t}}]}}


def bullet(t):
    return {"object": "block", "type": "bulleted_list_item",
            "bulleted_list_item": {"rich_text": [{"type": "text", "text": {"content": t}}]}}


def link(db_id, label, note=""):
    return {"object": "block", "type": "bulleted_list_item", "bulleted_list_item": {"rich_text": [
        {"type": "mention", "mention": {"type": "database", "database": {"id": db_id}}},
        {"type": "text", "text": {"content": f"  —  {label}" + (f"   {note}" if note else "")}}]}}


# create dashboard page under the workforce page
r = requests.post(f"{BASE}/pages", headers=H, timeout=45, json={
    "parent": {"type": "page_id", "page_id": WF},
    "icon": {"type": "emoji", "emoji": "📊"},
    "properties": {"title": [{"text": {"content": "📊 CTO DASHBOARD — Workforce Command"}}]},
})
DASH = r.json()["id"]
print(f"dashboard page: {DASH}")

blocks = [
    {"object": "block", "type": "callout", "callout": {
        "icon": {"type": "emoji", "emoji": "🎯"},
        "rich_text": [{"type": "text", "text": {"content":
            "Single command view. Notion is the system of record. Every agent checks in and out here. "
            "Built 2026-09-12 after recovering the stalled Paperclip org."}}]}},

    h2("🔴 HEADLINE"),
    para(f"{len(agents)} agents on the register · {len(tasks)} tasks · "
         f"{by_status.get('Blocked',0)} blocked · {by_pri.get('P0 Critical',0)} P0 critical · "
         f"{founder_gated} founder-gated."),
    para("The inherited board was 98% blocked when recovered — one agent (Canvas) held 134 of 147 open "
         "items, and the CEO (Atlas), CTO (Orion) and Mobile Lead (Canvas) were all in an error state. "
         "This rebuild replaces that single-point-of-failure with load-spread Hermes workers."),

    h2("🗂️ THE THREE SURFACES"),
    link(REG, "Agent Registry", "(roster, org chart, runtime)"),
    link(TASK, "Agent Tasks", "(the work board)"),
    link(CHK, "Agent Check-in Log", "(who is in, when, and what they produced)"),

    h2("👥 ROSTER BY STATUS"),
]
for k, v in reg_status.most_common():
    blocks.append(bullet(f"{v}  {k or '(none)'}"))

blocks += [h2("📋 BOARD BY STATUS")]
for k, v in by_status.most_common():
    blocks.append(bullet(f"{v}  {k or '(none)'}"))

blocks += [h2("⚡ BOARD BY PRIORITY")]
for k, v in by_pri.most_common():
    blocks.append(bullet(f"{v}  {k or '(none)'}"))

blocks += [h2("🎯 LOAD — WORK BY ASSIGNEE (top 10)"),
           para("Canvas holding 91% of the board was the original failure. Load is spread on purpose now.")]
for k, v in by_assignee.most_common(10):
    blocks.append(bullet(f"{v}  {k or '(unassigned)'}"))

blocks += [h2("🕒 CHECK-IN / CHECK-OUT")]
if last:
    for a, (ev, wh) in sorted(last.items()):
        blocks.append(bullet(f"{a} — last event {ev} at {wh[:19]}"))
else:
    blocks.append(bullet("No check-ins recorded yet. Run: workforce.py checkin <agent> <task>"))

blocks += [
    h2("📐 OPERATING RULES"),
    bullet("Every worker: check IN before work, check OUT with an outcome. No silent carries."),
    bullet("Blocked is a first-class state — it must name the blocker and the exact next action."),
    bullet("Founder-gated work never auto-executes; it appears on this dashboard and waits."),
    bullet("Evidence required for any claim of done: a command, a path, or a probe result."),
    bullet("Reports and scrum run on cadence; routine status lives on this dashboard, not in chat."),
]

CH = 40
for i in range(0, len(blocks), CH):
    rr = requests.patch(f"{BASE}/blocks/{DASH}/children", headers=H, timeout=45,
                        json={"children": blocks[i:i+CH]})
    print(f"  appended {min(i+CH, len(blocks))}/{len(blocks)}: {rr.status_code}")
    time.sleep(0.4)

json.dump({"dashboard": DASH, **IDS}, open("/opt/data/workforce_ids.json", "w"), indent=1)
print(f"\nDASHBOARD -> https://www.notion.so/{DASH.replace('-','')}")
