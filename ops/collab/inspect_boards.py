#!/usr/bin/env python3
"""Inspect the ChatGPT + Grok collaboration boards before writing to them."""
import json
import sys

import requests

sys.path.insert(0, "/opt/data/scripts")
from notion_client import headers

H = headers()
BASE = "https://api.notion.com/v1"

BOARDS = {
    "Ops Dashboard (ChatGPT lane)": "3c2a9b14-e498-81fb-96db-d4a35ba1eec3",
    "Grok CoS page": "3d6a9b14-e498-8166-a16f-cf5b1b091c02",
    "Master Workspace": "3d8a9b14-e498-8125-a630-f2fcc2bd2354",
    "CTO Dashboard (workforce)": "3d9a9b14-e498-81be-8f95-e1ac9b6d5a34",
}


def blocks(pid, limit=100):
    r = requests.get(f"{BASE}/blocks/{pid}/children?page_size={limit}", headers=H, timeout=45)
    return r.status_code, r.json()


def text_of(b):
    t = b.get("type")
    if t == "divider":
        return "----"
    v = b.get(t) or {}
    rt = v.get("rich_text") or (v.get("title") if t == "child_page" else None) or []
    s = "".join(x.get("plain_text", "") for x in rt)
    if t == "child_page":
        s = f"[PAGE] {v.get('title')}"
    if t == "child_database":
        s = f"[DB] {v.get('title')}"
    return s.strip()


for label, pid in BOARDS.items():
    code, d = blocks(pid)
    print("=" * 92)
    print(f"{label}   {pid}")
    print("=" * 92)
    if code >= 300:
        print(f"  HTTP {code}: {str(d)[:180]}")
        continue
    res = d.get("results", [])
    print(f"  top-level blocks: {len(res)}")
    for b in res[:40]:
        s = text_of(b)
        if not s:
            continue
        kind = b.get("type")
        print(f"    [{kind[:14]:<14}] {s[:100]}")
    if len(res) > 40:
        print(f"    ... +{len(res)-40} more")
    print()
