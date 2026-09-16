#!/usr/bin/env python3
"""Migrate the recovered Paperclip org (72 agents, 148 issues) into the Notion workforce DBs."""
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
REG, TASK = IDS["registry_db"], IDS["tasks_db"]

agents = json.load(open("/opt/data/paperclip_recovery/agents.json"))
issues = json.load(open("/opt/data/paperclip_recovery/issues.json"))
by_id = {a["id"]: a for a in agents}

DIVISION = [
    (("CEO", "Chief", "Advisor", "Board"), "Executive"),
    (("Engineer", "Developer", "Architect", "DevOps", "SRE", "SaaS RIS", "SaaS PACS",
      "SaaS EMR", "MCP", "Platform", "Cloud", "Docker", "Mobile", "Telecom",
      "Edge AI", "Integrations", "Administrator", "QA"), "Engineering"),
    (("Clinical", "Health", "Head of Research", "Reflection"), "Clinical"),
    (("CFO", "Controller", "Bookkeeper", "Accounts", "Revenue", "Midas"), "Revenue / Finance"),
    (("Marketing", "Iris", "Customer Success", "Nova"), "Growth"),
    (("HR", "Legal", "Harmony"), "People / Legal"),
    (("SaaS Division", "SaaS CRM"), "SaaS Division"),
]


def division_for(a):
    blob = f"{a['name']} {a.get('title') or ''}"
    for keys, div in DIVISION:
        if any(k.lower() in blob.lower() for k in keys):
            return div
    return "Engineering"


STATUS_MAP = {"error": "Error", "idle": "Idle", "paused": "Paused",
              "active": "Active", "running": "Active"}
PRIORITY_MAP = {"critical": "P0 Critical", "high": "P1 High",
                "medium": "P2 Medium", "low": "P3 Low"}


def rt(s):
    return {"rich_text": [{"type": "text", "text": {"content": str(s)[:1900]}}]}


def create(db, props, title_field, title_val, parent=None):
    props = dict(props)
    props[title_field] = {"title": [{"type": "text", "text": {"content": str(title_val)[:1900]}}]}
    payload = {"parent": {"type": "database_id", "database_id": db}, "properties": props}
    if parent:
        payload["parent"] = {"type": "page_id", "page_id": parent}
    r = requests.post(f"{BASE}/pages", headers=H, json=payload, timeout=45)
    if r.status_code >= 300:
        return None, r.status_code, r.text[:200]
    time.sleep(0.32)
    return r.json()["id"], 200, None


print("=" * 96)
print("MIGRATING 72 AGENTS -> Agent Registry")
print("=" * 96)
ok = fail = 0
for a in sorted(agents, key=lambda x: x["name"]):
    mgr = by_id.get(a.get("reports_to") or "", {}).get("name") or ""
    props = {
        "Title / Role": rt(a.get("title") or a.get("role") or ""),
        "Division": {"select": {"name": division_for(a)}},
        "Reports To": rt(mgr),
        "Status": {"select": {"name": STATUS_MAP.get(a.get("status"), "Idle")}},
        "Runtime": {"select": {"name": "Not staffed"}},
        "Adapter (legacy)": rt(a.get("adapter_type") or ""),
        "Recovered ID": rt(a["id"]),
        "Notes": rt(f"Recovered from Paperclip 2026-08-03 snapshot. Company {a['company_id'][:8]}. "
                    f"Legacy status: {a.get('status')}. Spend ${int(a.get('spent_monthly_cents') or 0)/100:.2f}"),
    }
    pid, code, err = create(REG, props, "Agent", a["name"])
    if pid:
        ok += 1
    else:
        fail += 1
        if fail <= 3:
            print(f"  !! {a['name']}: {code} {err}")
print(f"  agents migrated: {ok}   failed: {fail}")

print("\n" + "=" * 96)
print("MIGRATING 148 ISSUES -> Agent Tasks")
print("=" * 96)
DONE = {"done", "completed", "cancelled", "closed", "archived"}
ok2 = fail2 = 0
for i in issues:
    raw_status = (i.get("status") or "todo").lower()
    status = "Done" if raw_status in DONE else ("Blocked" if raw_status == "blocked" else "Backlog")
    who = by_id.get(i.get("assignee_agent_id", ""), {}).get("name") or "Unassigned"
    props = {
        "Identifier": rt(i.get("identifier") or ""),
        "Status": {"select": {"name": status}},
        "Priority": {"select": {"name": PRIORITY_MAP.get((i.get("priority") or "").lower(), "P2 Medium")}},
        "Assignee": rt(who),
        "Source": {"select": {"name": "Recovered (Paperclip)"}},
        "Blocked Reason": rt("Recovered as BLOCKED in Paperclip 2026-08-03; needs re-triage"
                             if status == "Blocked" else ""),
        "Founder Gate": {"checkbox": "CEO DIRECTIVE (founder)" in (i.get("title") or "")},
        "Recovered ID": rt(i["id"]),
    }
    pid, code, err = create(TASK, props, "Task", i.get("title") or "(untitled)")
    if pid:
        ok2 += 1
    else:
        fail2 += 1
        if fail2 <= 3:
            print(f"  !! {i.get('identifier')}: {code} {err}")
print(f"  issues migrated: {ok2}   failed: {fail2}")

print("\n" + "=" * 96)
print("VERIFY")
print("=" * 96)
for label, db, expect in (("Agent Registry", REG, len(agents)), ("Agent Tasks", TASK, len(issues))):
    n, cur = 0, None
    while True:
        b = {"page_size": 100}
        if cur:
            b["start_cursor"] = cur
        r = requests.post(f"{BASE}/databases/{db}/query", headers=H, json=b, timeout=45)
        d = r.json()
        n += len(d.get("results", []))
        if not d.get("has_more"):
            break
        cur = d.get("next_cursor")
    print(f"  {label:<16} rows={n:<5} expected={expect:<5} {'OK' if n == expect else 'MISMATCH'}")
