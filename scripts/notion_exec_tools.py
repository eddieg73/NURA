#!/usr/bin/env python3
"""
NURA Executive OS — Custom Notion Tools.

Implements the custom Notion tool surface for the Executive OS. All tools are
NON-PHI by design: they handle companies, projects, tasks, decisions, SOPs,
meeting notes, and de-identified executive metrics. Clinical data NEVER flows
through Notion — it stays in OpenEMR/Orthanc (source of truth).

Tools:
    generateExecutiveBrief        -> a dated executive brief page under an index
    createProjectFromDecision     -> a project page + a project record
    convertMeetingToTasks         -> parse meeting bullets into tasks in the DB
    generateBoardPresentation     -> a board-package page (decision log + metrics)
    auditStalePolicies            -> list SOP/policy pages untouched > N days
    prepareFounderApprovalPacket  -> a gated approval packet for a decision

Run:  python3 notion_exec_tools.py <tool> [args]
Env:  NOTION_API_TOKEN (or NOTION_PAT_NURATECH) + NOTION_VERSION=2022-06-28
"""
import os
import re
import sys
import json
import time
import urllib.request
import urllib.error

# ---- config / auth (external secret source, never hardcoded) ----
def _token():
    """Resolve the Notion token from the integration that OWNS the workspace DBs.
    Priority: auth.json (Notion CLI) > env override > sealed PAT file. The .env
    NOTION_API_TOKEN is the 'Nuratech ai' integration, which 404s on DBs created
    by the Notion CLI integration (verified) — so auth.json wins when present.
    """
    auth_json = "/opt/data/profiles/nura/home/.config/notion/auth.json"
    if os.path.exists(auth_json):
        try:
            d = json.load(open(auth_json))
            if d:
                return list(d.values())[0]
        except Exception:
            pass
    for k in ("NOTION_API_TOKEN", "NOTION_PAT_NURATECH"):
        v = os.environ.get(k)
        if v:
            return v
    for p in ("/opt/data/profiles/nura/home/.secrets/notion-nuratech-coder.env",
              "/opt/data/profiles/nura/.env"):
        if os.path.exists(p):
            for line in open(p, errors="ignore"):
                if line.startswith("NOTION_API_TOKEN=") or line.startswith("NOTION_PAT_NURATECH="):
                    return line.split("=", 1)[1].strip().strip('"').strip("'")
    raise SystemExit("No Notion token — check auth.json or set NOTION_API_TOKEN")

VER = os.environ.get("NOTION_VERSION", "2022-06-28")
TOKEN = _token()
HDR = {"Authorization": f"Bearer {TOKEN}", "Notion-Version": VER,
       "Content-Type": "application/json"}

# Well-known IDs (populated from the actual workspace runs)
MASTER_TASKS_DB = os.environ.get("NURA_TASKS_DB", "3cda9b14-e498-8139-bec7-f0e5d9ce416f")
CTO_SUITE = os.environ.get("NURA_CTO_SUITE", "3bea9b14-e498-816e-84c5-d9cda0497f87")
SECOND_BRAIN = os.environ.get("NURA_SECOND_BRAIN", "3cca9b14-e498-81e4-aa61-f1725f83145c")


def api(path, method="GET", body=None):
    req = urllib.request.Request(f"https://api.notion.com/v1{path}", method=method, headers=HDR)
    data = json.dumps(body).encode() if body else None
    try:
        with urllib.request.urlopen(req, data=data, timeout=30) as r:
            return json.loads(r.read().decode())
    except urllib.error.HTTPError as e:
        return {"error": e.code, "body": e.read().decode()[:400]}


def _t(text):
    return {"type": "text", "text": {"content": text}}


def _heading(text, level):
    key = f"heading_{level}"
    return {"object": "block", "type": key, key: {"rich_text": [_t(text)]}}


def _bullet(text):
    return {"object": "block", "type": "bulleted_list_item",
            "bulleted_list_item": {"rich_text": [_t(text)]}}


def _para(text):
    return {"object": "block", "type": "paragraph", "paragraph": {"rich_text": [_t(text)]}}


def _callout(text, emoji="🧠", color="blue_background"):
    return {"object": "block", "type": "callout",
            "callout": {"icon": {"type": "emoji", "emoji": emoji},
                        "rich_text": [_t(text)], "color": color}}


def _create_page(parent_page_id, title, blocks):
    chunks = [blocks[i:i + 90] for i in range(0, len(blocks), 90)]
    body = {"parent": {"page_id": parent_page_id},
            "properties": {"title": {"title": [_t(title)]}},
            "children": chunks[0]}
    r = api("/pages", "POST", body)
    if r.get("error"):
        return r
    pid = r["id"]
    for c in chunks[1:]:
        api(f"/blocks/{pid}/children", "PATCH", {"children": c})
    return {"id": pid, "url": r.get("url")}


def _add_task(title, status="To Do", priority=None, owner=None, source="Manual",
              project=None, commitment=False):
    body = {"parent": {"database_id": MASTER_TASKS_DB}, "properties": {
        "Task": {"title": [_t(title)]},
        "Status": {"select": {"name": status}},
    }}
    if priority:
        body["properties"]["Priority"] = {"select": {"name": priority}}
    if owner:
        body["properties"]["Owner"] = {"select": {"name": owner}}
    if source:
        body["properties"]["Source"] = {"select": {"name": source}}
    if project:
        body["properties"]["Project"] = {"rich_text": [_t(project)]}
    if commitment:
        body["properties"]["Commitment"] = {"checkbox": True}
    r = api("/pages", "POST", body)
    return r.get("error") and {"error": r} or {"id": r["id"], "url": r.get("url")}


# --------------------------------------------------------------------------
# TOOL 1: generateExecutiveBrief
# --------------------------------------------------------------------------
def generate_executive_brief(topic, highlights=None, parent=None):
    parent = parent or SECOND_BRAIN
    highlights = highlights or ["No highlights provided."]
    blocks = [
        _callout(f"Executive brief — {topic}. Generated {time.strftime('%Y-%m-%d')}.", "📊"),
        _heading("Summary", 2),
        _para("Auto-generated executive summary for leadership review."),
    ]
    for h in highlights:
        blocks.append(_bullet(h))
    blocks.append(_heading("Next Actions", 2))
    blocks.append(_bullet("Review and approve in the CTO Decision Log."))
    r = _create_page(parent, f"Executive Brief — {topic}", blocks)
    return r


# --------------------------------------------------------------------------
# TOOL 2: createProjectFromDecision
# --------------------------------------------------------------------------
def create_project_from_decision(decision, name, owner="Hermes", priority="P2"):
    blocks = [
        _callout(f"Project created from decision: {decision}", "🏗"),
        _heading("Origin Decision", 2),
        _para(decision),
        _heading("Ownership", 2),
        _bullet(f"Owner: {owner}"),
        _bullet(f"Priority: {priority}"),
        _heading("Status", 2),
        _bullet("Scoping — awaiting kickoff"),
    ]
    r = _create_page(CTO_SUITE, f"Project — {name}", blocks)
    if r.get("error"):
        return r
    # also record a task
    t = _add_task(f"Execute {name} (from decision)", priority=priority, owner=owner,
                  source="Decision", project=name, commitment=True)
    return {"project": r, "task": t}


# --------------------------------------------------------------------------
# TOOL 3: convertMeetingToTasks
# --------------------------------------------------------------------------
def convert_meeting_to_tasks(meeting_title, bullets, owner="Hermes"):
    """Parse a list of ('task', priority) tuples into task DB rows.
    Accepts either tuples/pairs or plain strings; normalizes JSON arrays."""
    created = []
    for b in bullets:
        if isinstance(b, (list, tuple)) and len(b) >= 2:
            task, pri = str(b[0]), str(b[1])
        elif isinstance(b, (list, tuple)) and len(b) == 1:
            task, pri = str(b[0]), "P3"
        else:
            task, pri = str(b), "P3"
        t = _add_task(task, status="To Do", priority=pri, owner=owner,
                      source="Meeting→Task", commitment=False)
        created.append({"task": task, "priority": pri, "result": t})
    return {"meeting": meeting_title, "tasks_created": created}


# --------------------------------------------------------------------------
# TOOL 4: generateBoardPresentation
# --------------------------------------------------------------------------
def generate_board_presentation(title="Board Package", sections=None, parent=None):
    parent = parent or SECOND_BRAIN
    sections = sections or [
        ("Executive Summary", ["Company on track", "Key metrics stable"]),
        ("Metrics", ["De-identified operational KPIs"]),
        ("Decisions", ["Logged in CTO Decision Log"]),
    ]
    blocks = [_callout(f"Board package — {title}. {time.strftime('%Y-%m-%d')}.", "📈")]
    for name, items in sections:
        blocks.append(_heading(name, 2))
        for it in items:
            blocks.append(_bullet(it))
    r = _create_page(parent, f"Board Package — {title}", blocks)
    return r


# --------------------------------------------------------------------------
# TOOL 5: auditStalePolicies
# --------------------------------------------------------------------------
def audit_stale_policies(days=90, parent=None):
    """Find pages under the CTO Suite not edited in > days."""
    parent = parent or CTO_SUITE
    ch = api(f"/blocks/{parent}/children?page_size=100")
    now = time.time()
    stale = []
    for b in ch.get("results", []):
        if b.get("type") == "child_page":
            pid = b["id"]
            title = b["child_page"]["title"]
            pg = api(f"/pages/{pid}")
            last = pg.get("last_edited_time")
            if last:
                age = (now - time.mktime(time.strptime(last[:19], "%Y-%m-%dT%H:%M:%S"))) / 86400
                if age > days:
                    stale.append({"title": title, "age_days": round(age, 1)})
    return {"stale_docs": stale, "threshold_days": days}


# --------------------------------------------------------------------------
# TOOL 6: prepareFounderApprovalPacket
# --------------------------------------------------------------------------
def prepare_founder_approval_packet(decision, context, approval_type="infra"):
    blocks = [
        _callout(f"Founder approval — {decision}", "✋"),
        _heading("What is being decided", 2),
        _para(decision),
        _heading("Context", 2),
        _para(context),
        _heading("Requested approval", 2),
        _bullet(f"Type: {approval_type}"),
        _bullet("Decision is GATED — awaits founder authorisation. Hermes NEVER auto-executes."),
        _heading("Approve / Deny", 2),
        _bullet("Reply 'approve' or 'deny' to this packet."),
    ]
    r = _create_page(CTO_SUITE, f"Approval Packet — {decision[:40]}", blocks)
    return r


# --------------------------------------------------------------------------
# CLI dispatch
# --------------------------------------------------------------------------
TOOLS = {
    "generateExecutiveBrief": generate_executive_brief,
    "createProjectFromDecision": create_project_from_decision,
    "convertMeetingToTasks": convert_meeting_to_tasks,
    "generateBoardPresentation": generate_board_presentation,
    "auditStalePolicies": audit_stale_policies,
    "prepareFounderApprovalPacket": prepare_founder_approval_packet,
}

if __name__ == "__main__":
    if len(sys.argv) < 2 or sys.argv[1] not in TOOLS:
        print("Usage: python3 notion_exec_tools.py <tool> [args]")
        print("Tools: " + ", ".join(TOOLS))
        sys.exit(1)
    tool = sys.argv[1]
    args = sys.argv[2:]
    # simple: run with raw args or a JSON blob
    if args and args[0].startswith("{"):
        result = TOOLS[tool](**json.loads(args[0]))
    else:
        result = TOOLS[tool](*args)
    print(json.dumps(result, indent=2, default=str))
