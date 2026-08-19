#!/usr/bin/env python3
"""Paperclip board pull for the weekly CEO scrum — issues grouped by assignee/status.
Output: compact digest the scrum agent turns into the founder report."""
import json, urllib.request

def env_file(path, names):
    try:
        for line in open(path):
            for n in names:
                if line.startswith(n + "="):
                    return line.strip().split("=", 1)[1].strip("'\"")
    except OSError:
        pass
    return None

key = env_file("/opt/data/paperclip-runtime/mcp.env", ["PAPERCLIP_API_KEY", "API_KEY"])
base = "http://127.0.0.1:3101"
hdr = {"User-Agent": "NURA-Hermes/1.0", "Content-Type": "application/json",
       "x-api-key": key or "", "Authorization": "Bearer " + (key or "")}
CID = "999ff375-6128-41cf-b6c8-06b98673a29b"

def get(path):
    req = urllib.request.Request(base + path, headers=hdr)
    with urllib.request.urlopen(req, timeout=10) as r:
        return json.loads(r.read())

try:
    issues = get(f"/api/companies/{CID}/issues")
    agents = get(f"/api/companies/{CID}/agents")
except Exception as e:
    print(f"SCRUM PULL FAIL: {str(e)[:120]}"); raise SystemExit

alist = issues if isinstance(issues, list) else issues.get("issues", issues.get("items", []))
agents_l = agents if isinstance(agents, list) else agents.get("agents", agents.get("items", []))
aname = {a.get("id"): a.get("name", "?") for a in agents_l}

print(f"BOARD {CID} | issues: {len(alist)} | agents: {len(agents_l)}")
for st in ["todo", "in_progress", "in_review", "done", "blocked"]:
    grp = [i for i in alist if (i.get("status") or "").lower() == st]
    if grp:
        print(f"\n[{st.upper()}] {len(grp)}")
        for i in sorted(grp, key=lambda x: x.get("priority", "medium") == "high", reverse=True)[:12]:
            assignee = aname.get(i.get("assigneeAgentId"), "unassigned")
            print(f"  - {i.get('title', '?')[:90]} | {assignee} | {i.get('priority','')}")
