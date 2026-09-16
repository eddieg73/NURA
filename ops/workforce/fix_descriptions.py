#!/usr/bin/env python3
"""
FIX the real migration gap found by verification: the recovered DESCRIPTION bodies were not
carried into Notion. 148/148 source issues have substantive text -- founder directives, acceptance
criteria, technical detail -- and the board held none of it.

Also adds a proper Created date so the recovered work can be aged.
"""
import json
import sys
import time

import requests

sys.path.insert(0, "/opt/data/scripts")
from notion_client import headers

H = headers()
BASE = "https://api.notion.com/v1"
ids = json.load(open("/opt/data/workforce_ids.json"))
TASKS = ids["tasks_db"]

# ---- 1. add the missing property -----------------------------------------
print("=" * 96)
print("1. ADD 'Description' property to Agent Tasks")
print("=" * 96)
r = requests.patch(f"{BASE}/databases/{TASKS}", headers=H, json={
    "properties": {"Description": {"rich_text": {}}}}, timeout=45)
print(f"  HTTP {r.status_code}  {r.text[:160] if r.status_code >= 300 else 'added'}")

# ---- 2. map recovered id -> description ----------------------------------
iss = json.load(open("/opt/data/paperclip_recovery/issues.json"))
by_id = {i["id"]: (i.get("description") or "").strip() for i in iss}
print(f"\n  source issues: {len(iss)}   with text: {sum(1 for v in by_id.values() if v)}")

# ---- 3. read every row, patch the description in --------------------------
print("\n" + "=" * 96)
print("2. BACKFILL the 148 descriptions")
print("=" * 96)


def all_rows(dbid):
    out, cur = [], None
    while True:
        b = {"page_size": 100}
        if cur:
            b["start_cursor"] = cur
        r = requests.post(f"{BASE}/databases/{dbid}/query", headers=H, json=b, timeout=60)
        d = r.json()
        out += d.get("results", [])
        if not d.get("has_more"):
            break
        cur = d.get("next_cursor")
    return out


rows = all_rows(TASKS)
print(f"  rows on board: {len(rows)}")

# Notion rich_text caps a single object at 2000 chars; chunk if needed.
def rich(text):
    return [{"type": "text", "text": {"content": text[:2000]}}]


ok = skip = 0
for row in rows:
    p = row["properties"]
    rid = "".join(x.get("plain_text", "") for x in p.get("Recovered ID", {}).get("rich_text", []))
    ident = "".join(x.get("plain_text", "") for x in p.get("Identifier", {}).get("rich_text", []))
    desc = by_id.get(rid, "")
    if not desc:
        skip += 1
        continue
    # keep the existing re-triage note as a separate concern; the description is the body
    patch = {"properties": {"Description": {"rich_text": rich(desc)}}}
    r = requests.patch(f"{BASE}/pages/{row['id']}", headers=H, json=patch, timeout=45)
    if r.status_code < 300:
        ok += 1
    else:
        print(f"    FAIL {ident}: HTTP {r.status_code} {r.text[:110]}")
    time.sleep(0.28)

print(f"\n  descriptions written: {ok}   no text in source: {skip}")

# ---- 4. verify by re-reading --------------------------------------------
print("\n" + "=" * 96)
print("3. VERIFY BY RE-READ (a 2xx is not evidence)")
print("=" * 96)
rows2 = all_rows(TASKS)
lens = []
empty = 0
for row in rows2:
    d = "".join(x.get("plain_text", "")
                for x in row["properties"].get("Description", {}).get("rich_text", []))
    if d:
        lens.append(len(d))
    else:
        empty += 1
print(f"  rows re-read:        {len(rows2)}")
print(f"  with description:    {len(lens)}")
print(f"  still empty:         {empty}")
if lens:
    print(f"  avg length:          {sum(lens)//len(lens)} chars")
    print(f"  longest:             {max(lens)} chars")
print(f"\n  {'PASS' if len(lens) >= 140 else 'FAIL'} — description backfill")
