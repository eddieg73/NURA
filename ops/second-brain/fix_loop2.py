#!/usr/bin/env python3
"""
Cleanup v2 -- my previous pass failed because txt(r,"Task") returns "DOCTRINE: The one concrete..."
so a regex anchored ^the one never matched. Strip the prefix, then judge the RULE TEXT.

Re-evaluates all 6 DOC tickets on the actual rule body and withdraws the ones that are not rules.
"""
import json
import re
import sys
import time

import requests

sys.path.insert(0, "/opt/data/scripts")
from notion_client import headers

H = headers()
BASE = "https://api.notion.com/v1"
ids = json.load(open("/opt/data/workforce_ids.json"))
TASKS = ids["tasks_db"]

NARRATIVE = re.compile(
    r"(?i)(^the one |^today's |^yesterday|^doctrine, not|^this is |^there is |"
    r"^the weekly |^the daily |^the same |^the only |"
    r"\bwas not\b|\bwere not\b|\bhad been\b|states the doctrine plainly|"
    r"nothing was modified|no fix was applied)")
CROSSSOURCE = re.compile(r"(?i)cross-source rule applied")


def all_rows():
    out, cur = [], None
    while True:
        b = {"page_size": 100}
        if cur:
            b["start_cursor"] = cur
        r = requests.post(f"{BASE}/databases/{TASKS}/query", headers=H, json=b, timeout=60)
        d = r.json()
        out += d.get("results", [])
        if not d.get("has_more"):
            break
        cur = d.get("next_cursor")
    return out


def txt(p, f):
    v = (p.get("properties") or {}).get(f) or {}
    t = v.get("type")
    return "".join(x.get("plain_text", "") for x in (v.get(t) or [])) if t in ("rich_text", "title") else ""


rows = all_rows()
junk = [r for r in rows if txt(r, "Identifier").startswith("DOC-")]
print("=" * 96)
print(f"RE-EVALUATING {len(junk)} DOC TICKETS ON THE RULE BODY (prefix stripped)")
print("=" * 96)

withdrawn = kept = 0
for r in junk:
    ident = txt(r, "Identifier")
    title = txt(r, "Task")
    body = re.sub(r"^DOCTRINE:\s*", "", title).strip()
    body = re.sub(r"\*\*|`|\*", "", body).strip()      # strip md emphasis

    if CROSSSOURCE.search(body):
        verdict, why = "JUNK", "false gap — the 2+ unrelated-sources rule IS in obsidian-nightly"
    elif NARRATIVE.search(body):
        verdict, why = "JUNK", "narrative/meta sentence, not a prescription"
    else:
        verdict, why = "KEEP", "genuine directive with an actionable subject"

    print(f"\n  {ident}  [{verdict}]  {why}")
    print(f"    \"{body[:120]}\"")

    if verdict == "JUNK":
        rr = requests.patch(f"{BASE}/pages/{r['id']}", headers=H, json={"properties": {
            "Status": {"select": {"name": "Done"}},
            "Description": {"rich_text": [{"type": "text", "text": {"content":
                f"WITHDRAWN by the CTO the same day it was raised. {why}.\n\n"
                f"ROOT CAUSE: close_the_loop.py v1 treated any sentence containing a modal verb "
                f"(must/should/never/always) as a rule. The synthesis notes are prose — they "
                f"contain narrative sentences that merely mention a modal. v1 raised them as "
                f"doctrine tickets.\n\n"
                f"FIXED in v2: a sentence must now (a) not open with a report marker, (b) not be "
                f"past-tense reporting, (c) not describe the note itself, (d) carry its modal in "
                f"the sentence head rather than tailing it. Threshold recalibrated to "
                f">=0.30 present / <0.15 real gap / 0.15-0.30 uncertain-not-ticketed.\n\n"
                f"Marked Done rather than deleted so the error stays auditable."}}]}}}, timeout=45)
        print(f"    -> withdrawn (HTTP {rr.status_code})")
        withdrawn += 1
        time.sleep(0.3)
    else:
        kept += 1

print("\n" + "=" * 96)
print(f"  withdrawn: {withdrawn}   kept as genuine doctrine gaps: {kept}")
print("=" * 96)

rows2 = all_rows()
still = [r for r in rows2 if txt(r, "Identifier").startswith("DOC-") and txt(r, "Status") != "Done"]
print(f"\n  board total: {len(rows2)}")
print(f"  DOC- tickets still open: {len(still)}  (was 6)")
for r in still:
    print(f"    {txt(r,'Identifier')}  {txt(r,'Task')[:88]}")
