#!/usr/bin/env python3
"""
NURA GitHub → Task Sync Worker.

Deterministic sync: pull recent GitHub activity (commits/PRs/issues) from the
NURA monorepo and create/update rows in the Master Tasks & Commitments Notion DB.
Non-PHI by design (software source of truth only). Dedupes on a stable key so
re-runs never create duplicate tasks.

Run: python3 github_task_sync.py [--since N]   (N = hours back, default 24)
Env: GITHUB_PAT_NURATECH_CODER + NOTION auth.json token
"""
import os
import sys
import json
import time
import urllib.request
import urllib.error

# ---- config ----
REPO = "eddieg73/NURA"
BRANCH = "master"
SINCE_H = 24
MASTER_TASKS_DB = "3cda9b14-e498-8139-bec7-f0e5d9ce416f"
STATE_FILE = "/opt/data/profiles/nura/cache/github_task_sync.state"

# ---- auth ----
def _gh_token():
    p = "/opt/data/profiles/nura/home/.secrets/github-nuratech-coder.env"
    if os.path.exists(p):
        for line in open(p, errors="ignore"):
            line = line.strip().rstrip(";")
            if line.startswith("export "):
                line = line[len("export "):]
            if "=" in line and "GITHUB" in line.split("=", 1)[0] and "PAT" in line.split("=", 1)[0]:
                return line.split("=", 1)[1].strip().strip('"').strip("'")
    for k in ("GITHUB_PAT_NURATECH_CODER", "GITHUB_TOKEN", "GITHUB_PAT"):
        v = os.environ.get(k)
        if v:
            return v
    raise SystemExit("No GitHub token")


def _notion_token():
    ap = "/opt/data/profiles/nura/home/.config/notion/auth.json"
    if os.path.exists(ap):
        d = json.load(open(ap))
        if d:
            return list(d.values())[0]
    for k in ("NOTION_API_TOKEN", "NOTION_PAT_NURATECH"):
        v = os.environ.get(k)
        if v:
            return v
    raise SystemExit("No Notion token")


def gh(url):
    req = urllib.request.Request(url)
    req.add_header("Authorization", "Bearer " + _gh_token())
    try:
        with urllib.request.urlopen(req, timeout=20) as r:
            return json.load(r)
    except urllib.error.HTTPError as e:
        return {"err": e.code, "body": e.read().decode()[:200]}


def notion(method, path, body=None, ver="2022-06-28"):
    req = urllib.request.Request(f"https://api.notion.com/v1{path}", method=method)
    req.add_header("Authorization", "Bearer " + _notion_token())
    req.add_header("Notion-Version", ver)
    req.add_header("Content-Type", "application/json")
    data = json.dumps(body).encode() if body else None
    try:
        with urllib.request.urlopen(req, data=data, timeout=30) as r:
            return json.load(r)
    except urllib.error.HTTPError as e:
        return {"err": e.code, "body": e.read().decode()[:200]}


# ---- dedupe state ----
def load_state():
    if os.path.exists(STATE_FILE):
        try:
            return json.load(open(STATE_FILE))
        except Exception:
            return {}
    return {}


def save_state(st):
    os.makedirs(os.path.dirname(STATE_FILE), exist_ok=True)
    json.dump(st, open(STATE_FILE, "w"))


# ---- core ----
def fetch_recent_commits(since_h):
    cutoff = time.time() - since_h * 3600
    url = f"https://api.github.com/repos/{REPO}/commits?sha={BRANCH}&per_page=30"
    data = gh(url)
    commits = []
    if isinstance(data, list):
        for c in data:
            msg = c.get("commit", {}).get("message", "").splitlines()[0]
            sha = c.get("sha", "")
            date = c.get("commit", {}).get("author", {}).get("date", "")
            # parse date to epoch
            try:
                epoch = time.mktime(time.strptime(date[:19], "%Y-%m-%dT%H:%M:%S")) - time.timezone
            except Exception:
                epoch = 0
            if epoch >= cutoff - 60:
                commits.append({"sha": sha, "message": msg, "date": date[:10]})
    return commits


def existing_tasks():
    q = notion("POST", f"/databases/{MASTER_TASKS_DB}/query", {"page_size": 100})
    tasks = []
    for r in q.get("results", []):
        p = r.get("properties", {})
        t = " ".join(x.get("plain_text", "") for x in p.get("Task", {}).get("title", []))
        tasks.append(t)
    return tasks


def add_task(title, status="To Do", priority="P2", owner="Hermes", source="Decision",
             project=None):
    body = {"parent": {"database_id": MASTER_TASKS_DB}, "properties": {
        "Task": {"title": [{"type": "text", "text": {"content": title}}]},
        "Status": {"select": {"name": status}},
        "Priority": {"select": {"name": priority}},
        "Owner": {"select": {"name": owner}},
        "Source": {"select": {"name": source}},
        "Commitment": {"checkbox": False},
    }}
    if project:
        body["properties"]["Project"] = {"rich_text": [{"type": "text", "text": {"content": project}}]}
    r = notion("POST", "/pages", body)
    return r.get("id") is not None, r


def run(since_h=SINCE_H):
    state = load_state()
    commits = fetch_recent_commits(since_h)
    existing = set(existing_tasks())
    created = 0
    skipped = 0
    for c in commits:
        # build a task title from the commit (truncate, strip "feat/docs/..." prefix)
        msg = c["message"]
        # dedupe key: short sha
        key = c["sha"][:7] + "|" + msg[:40]
        if state.get(key):
            skipped += 1
            continue
        title = msg[:100]
        if title in existing:
            skipped += 1
            continue
        ok, r = add_task(title, source="Decision", project="GitHub/NURA")
        if ok:
            state[key] = {"msg": msg, "date": c["date"]}
            existing.add(title)
            created += 1
    save_state(state)
    return {"commits_seen": len(commits), "created": created, "skipped": skipped}


if __name__ == "__main__":
    since_h = SINCE_H
    if "--since" in sys.argv:
        since_h = int(sys.argv[sys.argv.index("--since") + 1])
    result = run(since_h)
    print(json.dumps(result, indent=2))
