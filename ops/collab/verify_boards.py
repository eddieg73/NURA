#!/usr/bin/env python3
"""
Verify the Grok board append WITH PAGINATION.

The naive re-read showed '100 -> 100' which looks like a no-op but is actually the page_size=100 cap.
This is the same class of error as everything else tonight: the instrument, not the write.
Count properly, and confirm the NEW content is actually there.
"""
import sys

import requests

sys.path.insert(0, "/opt/data/scripts")
from notion_client import headers

H = headers()
GROK = "3d6a9b14-e498-8166-a16f-cf5b1b091c02"
OPS = "3c2a9b14-e498-81fb-96db-d4a35ba1eec3"


def all_blocks(pid):
    out, cur = [], None
    while True:
        url = f"https://api.notion.com/v1/blocks/{pid}/children?page_size=100"
        if cur:
            url += f"&start_cursor={cur}"
        d = requests.get(url, headers=H, timeout=60).json()
        out += d.get("results", [])
        if not d.get("has_more"):
            break
        cur = d.get("next_cursor")
    return out


def text_of(b):
    t = b.get("type")
    v = b.get(t) or {}
    rt = v.get("rich_text") or []
    return "".join(x.get("plain_text", "") for x in rt)


for label, pid, marker in [
    ("Grok CoS board", GROK, "Hermes → Chief of Staff · CHECK-IN"),
    ("Ops Dashboard", OPS, "HERMES CTO — SESSION WORK RECORD"),
]:
    blocks = all_blocks(pid)
    txts = [text_of(b) for b in blocks]
    found = [t for t in txts if marker.split("·")[0].strip()[:28] in t and "2026-09-13" in t]
    print("=" * 84)
    print(f"{label}")
    print("=" * 84)
    print(f"  TRUE total blocks (paginated): {len(blocks)}")
    print(f"  marker '{marker[:44]}': {'FOUND' if found else 'NOT FOUND'}")
    if found:
        print(f"    -> {found[0][:96]}")
    # show the last few blocks, which is what we appended
    print("  last 6 blocks:")
    for b in blocks[-6:]:
        s = text_of(b)
        if s:
            print(f"    [{b.get('type')[:14]:<14}] {s[:88]}")
    print()
