#!/usr/bin/env python3
"""Inspect the CANONICAL Master Tasks board (d3ff0c00) — schema + existing rows.
Purpose: find the right properties and check for pre-existing RATCHET/GR00T/GitHub-token tasks
so I migrate WITHOUT creating duplicates (connect-to-canonical, never two)."""
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
def req(m,p,b=None,t=30):
    r=requests.request(m,API+p,headers=H,json=b,timeout=t); return r.status_code,r.json()

DB="d3ff0c00-c629-43dc-b82c-06a28866fcb1"
st,d=req("GET",f"/databases/{DB}")
print("=== CANONICAL BOARD SCHEMA (properties) ===")
props=d.get("properties",{})
for k,v in props.items():
    print(f"  {k} : {v.get('type')}")

st2,d2=req("POST",f"/databases/{DB}/query",{"page_size":100})
rows=d2.get("results",[]) if st2<400 else []
print(f"\n=== ROWS: {len(rows)} — check for pre-existing RATCHET/GR00T/GitHub-token ===")
title_key = None
for k,v in props.items():
    if v.get("type")=="title":
        title_key=k; break
def val(prop):
    t=prop.get("title",[]) if isinstance(prop,dict) else []
    return "".join(x.get("plain_text","") for x in t) if t else ""
for r in rows:
    title=val(r.get("properties",{}).get(title_key,{})) if title_key else ""
    lower=title.lower()
    if any(k in lower for k in ("ratchet","gr00t","github","token","gpu","spike","pat")):
        print(f"  MATCH: {title[:80]}")
