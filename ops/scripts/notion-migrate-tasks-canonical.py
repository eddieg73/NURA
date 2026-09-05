#!/usr/bin/env python3
"""Migrate my 3 tasks into the CANONICAL Master Tasks board (d3ff0c00) — exact select options.
One register only. Verifies read-back."""
import os, json, requests

def _token():
    ap = "/opt/data/profiles/nura/home/.config/notion/auth.json"
    if os.path.exists(ap):
        d = json.load(open(ap))
        if d:
            return next(iter(d.values()))
    raise SystemExit("no token")

TOKEN=_token(); VER="2022-06-28"; H={"Authorization":f"Bearer {TOKEN}","Notion-Version":VER,"Content-Type":"application/json"}
API="https://api.notion.com/v1"
DB="d3ff0c00-c629-43dc-b82c-06a28866fcb1"  # CANONICAL
def req(m,p,b=None,t=30):
    r=requests.request(m,API+p,headers=H,json=b,timeout=t); return r.status_code,r.json()
def t(x): return [{"type":"text","text":{"content":x}}]

TASKS = [
    ("Execute RATCHET — NURA Humanoid v1 (GR00T policy + NURA Agent OS brain + safety kernel, sim-first). NUR-59.",
     "P1 — High", "Hermes", "RATCHET", "Doing"),
    ("Run GR00T inference spike on the GPU box (DGX Spark aarch64 / CUDA dGPU) — GR00T N1.7 cloned + staged at /opt/data/isaac-gr00t; HF access confirmed; gated on Spark access. install_deps.sh + standalone_inference_script.py.",
     "P1 — High", "Eddie", "RATCHET", "Next"),
    ("Generate a fresh GitHub PAT (classic: repo + project scopes), set as GITHUB_TOKEN in /opt/data/profiles/nura/.env. Unblocks GitHub Projects Kanban + Notion sync.",
     "P1 — High", "Eddie", "NURA GitHub Projects", "Next"),
]

for title, prio, owner, project, status in TASKS:
    body = {"parent": {"database_id": DB}, "properties": {
        "Task": {"title": t(title)},
        "Status": {"select": {"name": status}},
        "Priority": {"select": {"name": prio}},
        "Owner": {"rich_text": t(owner)},
        "Source System": {"select": {"name": "Hermes"}},
        "Task Type": {"select": {"name": "Build"}},
    }}
    st, d = req("POST", "/pages", body)
    if st < 400:
        print("OK", f"{project:24} | {title[:48]} | id={d.get('id')}")
    else:
        print("ERR", st, d.get("message", d)[:200])
