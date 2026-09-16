#!/usr/bin/env python3
"""
NURA Meeting → Tasks Webhook / Worker.

Consumes meeting-notes sources (primary: CTO Decision Log; secondary: any page
holding "decided to/action/owner" bullets) and creates assigned tasks in the
Master Tasks & Commitments DB via convertMeetingToTasks semantics. Deduped.

Non-PHI by design. Re-runnable.

Run: python3 meeting_to_tasks.py [--source <page_id>] [--dry-run]
"""
import os
import sys
import json
import time
import urllib.request
import urllib.error

VER = "2022-06-28"
MASTER_TASKS_DB = "3cda9b14-e498-8139-bec7-f0e5d9ce416f"
# Genuine decisions source: the Decision Records (ADR) page, not the status ledger.
# (Granola key is unset so the meeting lane isn't reachable; ADR is the canonical
#  structured decisions record. Set GRANOLA_API_KEY later for true meeting capture.)
ADR_PAGE = "3bea9b14-e498-8161-8440-e04b5cc79458"
STATE = "/opt/data/profiles/nura/cache/meeting_to_tasks.state"

# decision/action keywords -> priority heuristic. Decision lines start with
# "Decision:" — the strongest signal. Avoid status noise (verified/fixed/green).
DECISION_WORDS = ["decision:", "decision -", "decided to", "we decided", "adr-",
                  "resolve to", "will use", "will adopt", "standardize on"]
ACTION_WORDS = ["action", "owner", "must", "implement", "build", "ship", "fix",
                "wire", "deploy", "tasks", "follow-up"]


def _notion_token():
    ap = "/opt/data/profiles/nura/home/.config/notion/auth.json"
    if os.path.exists(ap):
        d = json.load(open(ap))
        if d:
            return list(d.values())[0]
    raise SystemExit("No Notion token")


def api(method, path, body=None):
    req = urllib.request.Request(f"https://api.notion.com/v1{path}", method=method)
    req.add_header("Authorization", "Bearer " + _notion_token())
    req.add_header("Notion-Version", VER)
    req.add_header("Content-Type", "application/json")
    data = json.dumps(body).encode() if body else None
    try:
        with urllib.request.urlopen(req, data=data, timeout=30) as r:
            return json.load(r)
    except urllib.error.HTTPError as e:
        return {"err": e.code, "body": e.read().decode()[:200]}


def load_state():
    if os.path.exists(STATE):
        try:
            return json.load(open(STATE))
        except Exception:
            return {}
    return {}


def save_state(st):
    os.makedirs(os.path.dirname(STATE), exist_ok=True)
    json.dump(st, open(STATE, "w"))


def walk_blocks(page_id, limit=200):
    """Collect bullet/paragraph/todo text from a page (and its child pages)."""
    texts = []
    cur = None
    while True:
        path = f"/blocks/{page_id}/children?page_size=100"
        if cur:
            path += f"&start_cursor={cur}"
        d = api("GET", path)
        for b in d.get("results", []):
            t = b.get("type")
            if t == "child_page":
                texts.extend(walk_blocks(b["id"], limit - len(texts)))
            elif t in ("bulleted_list_item", "paragraph", "to_do"):
                txt = " ".join(p.get("plain_text", "") for p in b.get(t, {}).get("rich_text", []))
                if txt.strip():
                    texts.append(txt.strip())
        if d.get("has_more") and len(texts) < limit:
            cur = d["next_cursor"]
        else:
            break
        if len(texts) >= limit:
            break
    return texts


def is_action(text):
    tl = text.lower()
    return any(w in tl for w in DECISION_WORDS) or any(w in tl for w in ACTION_WORDS)


def priority_for(text):
    tl = text.lower()
    if any(w in tl for w in ["p1", "urgent", "critical", "must", "deadline", "asap", "p0"]):
        return "P1"
    if any(w in tl for w in ["p2", "important", "should", "this week", "need"]):
        return "P2"
    return "P3"


def add_task(title, priority="P2", owner="Hermes"):
    body = {"parent": {"database_id": MASTER_TASKS_DB}, "properties": {
        "Task": {"title": [{"type": "text", "text": {"content": title}}]},
        "Status": {"select": {"name": "To Do"}},
        "Priority": {"select": {"name": priority}},
        "Owner": {"select": {"name": owner}},
        "Source": {"select": {"name": "Meeting→Task"}},
        "Commitment": {"checkbox": False},
    }}
    r = api("POST", "/pages", body)
    return r.get("id") is not None


def existing_tasks():
    q = api("POST", f"/databases/{MASTER_TASKS_DB}/query", {"page_size": 100})
    return {" ".join(x.get("plain_text", "") for x in r.get("properties", {}).get("Task", {}).get("title", []))
            for r in q.get("results", [])}


def run(source_id=ADR_PAGE, dry_run=False):
    state = load_state()
    texts = walk_blocks(source_id)
    existing = existing_tasks()
    created = 0
    skipped = 0
    actions = []
    for text in texts:
        if not is_action(text):
            continue
        key = text[:60]
        if state.get(key) or key in existing:
            skipped += 1
            continue
        pri = priority_for(text)
        actions.append((text[:110], pri))
        if dry_run:
            continue
        if add_task(text[:110], pri):
            state[key] = True
            created += 1
    if not dry_run:
        save_state(state)
    return {"source": source_id, "bullets_seen": len(texts), "action_lines": len(actions),
            "created": created, "skipped": skipped, "dry_run": dry_run, "actions": actions[:8]}


if __name__ == "__main__":
    dry = "--dry-run" in sys.argv
    src = ADR_PAGE
    if "--source" in sys.argv:
        src = sys.argv[sys.argv.index("--source") + 1]
    print(json.dumps(run(src, dry), indent=2, default=str))
