#!/usr/bin/env python3
"""
Is the 'Notion AI cleanup instructions' page still alive, and is it intact?

My earlier state read reported 0 blocks for id 3d8a9b14-e498-8116-b952c676eebc0e0b, which Notion
rejects as an invalid UUID. Two possibilities: (a) the recorded id is malformed, (b) the page is gone.
Find out, do not guess. Search by title and by content, and report what is actually there.
"""
import sys

import requests

sys.path.insert(0, "/opt/data/scripts")
from notion_client import headers

H = headers()


def search(q, n=25):
    r = requests.post("https://api.notion.com/v1/search", headers=H, timeout=60,
                      json={"query": q, "page_size": n})
    return r.status_code, r.json()


def title_of(obj):
    if obj.get("object") == "page":
        for k, v in (obj.get("properties") or {}).items():
            if v.get("type") == "title":
                return "".join(x.get("plain_text", "") for x in v.get("title", []))
    return obj.get("title") or ""


def blocks(pid):
    out, cur = [], None
    while True:
        u = f"https://api.notion.com/v1/blocks/{pid}/children?page_size=100"
        if cur:
            u += f"&start_cursor={cur}"
        r = requests.get(u, headers=H, timeout=60)
        if r.status_code >= 300:
            return None, r.status_code
        d = r.json()
        out += d.get("results", [])
        if not d.get("has_more"):
            break
        cur = d.get("next_cursor")
    return out, 200


print("=" * 88)
print("1. DOES THE RECORDED PAGE ID RESOLVE?")
print("=" * 88)
RECORDED = "3d8a9b14-e498-8116-b952c676eebc0e0b"
b, code = blocks(RECORDED)
print(f"  {RECORDED}")
print(f"  -> HTTP {code}, {0 if b is None else len(b)} blocks")
print("  (400 = malformed/unknown uuid, not an empty page)")

print("\n" + "=" * 88)
print("2. SEARCH BY TITLE — 'CLEANUP'")
print("=" * 88)
code, d = search("cleanup")
print(f"  HTTP {code}, {len(d.get('results', []))} results")
for r in d.get("results", []):
    t = title_of(r)
    if t:
        print(f"    [{r.get('object'):<7}] {t[:70]:<70} trash={r.get('in_trash')}")

print("\n" + "=" * 88)
print("3. SEARCH BY TITLE — 'NOTION AI'")
print("=" * 88)
code, d = search("Notion AI")
print(f"  HTTP {code}, {len(d.get('results', []))} results")
for r in d.get("results", []):
    t = title_of(r)
    if t:
        print(f"    [{r.get('object'):<7}] {t[:70]:<70} trash={r.get('in_trash')}")

print("\n" + "=" * 88)
print("4. SEARCH — 'MASTER WORKSPACE' children (the page should be a child of it)")
print("=" * 88)
MASTER = "3d8a9b14-e498-8125-a630-f2fcc2bd2354"
b, code = blocks(MASTER)
print(f"  master HTTP {code}, {0 if b is None else len(b)} blocks")
if b:
    for x in b:
        if x.get("type") == "child_page":
            print(f"    [child_page] {x['child_page'].get('title','')[:70]}  {x['id']}")
        elif x.get("type") == "child_database":
            print(f"    [child_db]   {x['child_database'].get('title','')[:70]}  {x['id']}")
