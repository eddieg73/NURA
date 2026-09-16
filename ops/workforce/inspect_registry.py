#!/usr/bin/env python3
"""Inspect the Agent Registry schema + the duplicate rows before applying fixes."""
import json
import sys

import requests

sys.path.insert(0, "/opt/data/scripts")
from notion_client import headers

H = headers()
BASE = "https://api.notion.com/v1"
ids = json.load(open("/opt/data/workforce_ids.json"))

r = requests.get(f"{BASE}/databases/{ids['registry_db']}", headers=H, timeout=45)
db = r.json()
print("SCHEMA — Agent Registry")
for n, s in db.get("properties", {}).items():
    print(f"  {n:<24} {s.get('type')}")

r = requests.post(f"{BASE}/databases/{ids['registry_db']}/query", headers=H,
                  json={"page_size": 100}, timeout=60)
rows = r.json().get("results", [])
print(f"\nrows: {len(rows)}")
print("\nFULL DUMP of the first 3 rows (all properties):")
for row in rows[:3]:
    print("  " + "-" * 88)
    for n, v in row["properties"].items():
        t = v.get("type")
        val = v.get(t)
        if t in ("rich_text", "title"):
            val = "".join(x.get("plain_text", "") for x in (val or []))[:70]
        elif isinstance(val, dict):
            val = val.get("name")
        print(f"    {n:<24} {t:<10} {str(val)[:70]}")

print("\nTHE TWO DUPLICATE PAIRS — full detail:")
for row in rows:
    name = "".join(x.get("plain_text", "")
                   for x in row["properties"].get("Agent", {}).get("title", []))
    if name in ("Summarizer", "Reflection Coach"):
        print("  " + "-" * 88)
        print(f"    page_id = {row['id']}")
        for n, v in row["properties"].items():
            t = v.get("type")
            val = v.get(t)
            if t in ("rich_text", "title"):
                val = "".join(x.get("plain_text", "") for x in (val or []))[:80]
            elif isinstance(val, dict):
                val = val.get("name")
            print(f"      {n:<22} {str(val)[:80]}")
