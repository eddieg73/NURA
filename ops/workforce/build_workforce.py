#!/usr/bin/env python3
"""
BUILD: Hermes-native workforce structure in Notion.

Creates, under the Master Workspace:
  🤖 NURA AGENT WORKFORCE  (page)
    ├── Agent Registry        (DB) - the org chart / roster
    ├── Agent Tasks           (DB) - the work board (recovered + new)
    └── Agent Check-in Log    (DB) - check-in/check-out discipline

Idempotent: if a page already exists with the same title, it is reused.
"""
import json
import sys
import time
import requests

sys.path.insert(0, "/opt/data/scripts")
from notion_client import headers

H = headers()
BASE = "https://api.notion.com/v1"
MASTER = "3d8a9b14-e498-8125-a630-f2fcc2bd2354"


def api(method, path, **kw):
    r = getattr(requests, method)(f"{BASE}{path}", headers=H, timeout=45, **kw)
    if r.status_code >= 300:
        print(f"  !! {method.upper()} {path} -> {r.status_code}: {r.text[:300]}")
        return None
    return r.json()


def find_child_page(parent, title):
    res, cur = [], None
    while True:
        p = {"page_size": 100}
        if cur:
            p["start_cursor"] = cur
        r = requests.get(f"{BASE}/blocks/{parent}/children", headers=H, params=p, timeout=45)
        d = r.json()
        res += d.get("results", [])
        if not d.get("has_more"):
            break
        cur = d.get("next_cursor")
    for b in res:
        if b.get("type") == "child_page" and b["child_page"].get("title") == title:
            return b["id"]
    return None


print("=" * 96)
print("STEP 1 — workforce container page")
print("=" * 96)
WF = find_child_page(MASTER, "🤖 NURA AGENT WORKFORCE")
if WF:
    print(f"  reusing existing page {WF}")
else:
    d = api("post", "/pages", json={
        "parent": {"type": "page_id", "page_id": MASTER},
        "icon": {"type": "emoji", "emoji": "🤖"},
        "properties": {"title": [{"text": {"content": "🤖 NURA AGENT WORKFORCE"}}]},
    })
    WF = d["id"]
    print(f"  created {WF}")

print("\n" + "=" * 96)
print("STEP 2 — the three databases")
print("=" * 96)

REGISTRY = api("post", "/databases", json={
    "parent": {"type": "page_id", "page_id": WF},
    "icon": {"type": "emoji", "emoji": "📋"},
    "title": [{"type": "text", "text": {"content": "Agent Registry"}}],
    "properties": {
        "Agent": {"title": {}},
        "Title / Role": {"rich_text": {}},
        "Division": {"select": {"options": [
            {"name": "Executive", "color": "purple"},
            {"name": "Engineering", "color": "blue"},
            {"name": "Clinical", "color": "green"},
            {"name": "Revenue / Finance", "color": "yellow"},
            {"name": "Growth", "color": "orange"},
            {"name": "People / Legal", "color": "pink"},
            {"name": "SaaS Division", "color": "brown"},
        ]}},
        "Reports To": {"rich_text": {}},
        "Status": {"select": {"options": [
            {"name": "Active", "color": "green"},
            {"name": "Idle", "color": "gray"},
            {"name": "Error", "color": "red"},
            {"name": "Paused", "color": "yellow"},
            {"name": "Retired", "color": "default"},
        ]}},
        "Runtime": {"select": {"options": [
            {"name": "Hermes cron", "color": "green"},
            {"name": "Hermes subagent", "color": "blue"},
            {"name": "Not staffed", "color": "gray"},
        ]}},
        "Adapter (legacy)": {"rich_text": {}},
        "Recovered ID": {"rich_text": {}},
        "Notes": {"rich_text": {}},
    },
})
print(f"  Agent Registry   -> {REGISTRY['id'] if REGISTRY else 'FAILED'}")

TASKS = api("post", "/databases", json={
    "parent": {"type": "page_id", "page_id": WF},
    "icon": {"type": "emoji", "emoji": "✅"},
    "title": [{"type": "text", "text": {"content": "Agent Tasks"}}],
    "properties": {
        "Task": {"title": {}},
        "Identifier": {"rich_text": {}},
        "Status": {"select": {"options": [
            {"name": "Backlog", "color": "gray"},
            {"name": "Ready", "color": "blue"},
            {"name": "In Progress", "color": "yellow"},
            {"name": "Blocked", "color": "red"},
            {"name": "In Review", "color": "orange"},
            {"name": "Done", "color": "green"},
            {"name": "Cancelled", "color": "default"},
        ]}},
        "Priority": {"select": {"options": [
            {"name": "P0 Critical", "color": "red"},
            {"name": "P1 High", "color": "orange"},
            {"name": "P2 Medium", "color": "yellow"},
            {"name": "P3 Low", "color": "gray"},
        ]}},
        "Assignee": {"rich_text": {}},
        "Source": {"select": {"options": [
            {"name": "Recovered (Paperclip)", "color": "brown"},
            {"name": "Founder directive", "color": "purple"},
            {"name": "Hermes", "color": "blue"},
        ]}},
        "Blocked Reason": {"rich_text": {}},
        "Founder Gate": {"checkbox": {}},
        "Evidence": {"rich_text": {}},
        "Recovered ID": {"rich_text": {}},
    },
})
print(f"  Agent Tasks      -> {TASKS['id'] if TASKS else 'FAILED'}")

CHECKIN = api("post", "/databases", json={
    "parent": {"type": "page_id", "page_id": WF},
    "icon": {"type": "emoji", "emoji": "🕒"},
    "title": [{"type": "text", "text": {"content": "Agent Check-in Log"}}],
    "properties": {
        "Entry": {"title": {}},
        "Agent": {"rich_text": {}},
        "Event": {"select": {"options": [
            {"name": "Check-in", "color": "green"},
            {"name": "Check-out", "color": "blue"},
            {"name": "Blocked", "color": "red"},
            {"name": "Handoff", "color": "orange"},
        ]}},
        "When": {"date": {}},
        "Task": {"rich_text": {}},
        "Outcome": {"rich_text": {}},
        "Evidence": {"rich_text": {}},
    },
})
print(f"  Check-in Log     -> {CHECKIN['id'] if CHECKIN else 'FAILED'}")

out = {
    "workforce_page": WF,
    "registry_db": REGISTRY["id"] if REGISTRY else None,
    "tasks_db": TASKS["id"] if TASKS else None,
    "checkin_db": CHECKIN["id"] if CHECKIN else None,
}
json.dump(out, open("/opt/data/workforce_ids.json", "w"), indent=1)
print("\n-> /opt/data/workforce_ids.json")
for k, v in out.items():
    print(f"   {k}: {v}")
