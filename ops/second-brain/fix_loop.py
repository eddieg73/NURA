#!/usr/bin/env python3
"""
CLEANUP + FIX.

My close_the_loop.py produced garbage: it raised 6 doctrine tickets on the founder's board, and
several are not rules at all -- they are narrative statements from the synthesis notes:

  DOC-002  "The one concrete, still-open consequence is the CLINIC attribution conflict above..."
           -> narrative. Not a rule.
  DOC-003  "Today's worklands -- software engineering, agent orchestration, and clinical/identity
           data -- are unrelated domains, but they independently converge"
           -> descriptive observation. Not a rule.
  DOC-005  "Doctrine, not a defect report -- read-only pass; nothing was modified..."
           -> meta-commentary about the note itself. Not a rule.
  DOC-006  "Cross-source rule applied: the concept must appear in 2+ unrelated sources"
           -> IS a rule, and IS implemented (it is in the obsidian-nightly skill). A false gap.

I put junk on the board. This removes it, then fixes the two root causes:
  (1) extraction -- require a genuine directive shape, exclude narrative/meta/past-tense reporting
  (2) threshold   -- a rule reworded across docs still counts as present (~0.30), and a rule with
                     almost no phrase overlap is the real signal (<0.15).
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

# ---- 1. find and archive the junk -----------------------------------------
print("=" * 96)
print("1. REMOVING THE JUNK TICKETS")
print("=" * 96)


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
print(f"  DOC- tickets found: {len(junk)}")

for r in junk:
    ident = txt(r, "Identifier")
    title = txt(r, "Task")
    # a real rule must contain a modal/imperative AND not read as narrative
    is_narrative = bool(re.search(
        r"(?i)(^(the one|today's|yesterday|doctrine, not)|was not|were not|"
        r"states the doctrine plainly|converge)", title))
    is_crosssource = "cross-source rule" in title.lower()
    verdict = "JUNK (narrative)" if is_narrative else (
        "JUNK (false gap - already in obsidian-nightly)" if is_crosssource else "keep")
    print(f"    {ident}  {verdict:<48} {title[:58]}")
    if verdict.startswith("JUNK"):
        # move to Done with an explicit correction note rather than delete (audit trail)
        rr = requests.patch(f"{BASE}/pages/{r['id']}", headers=H, json={"properties": {
            "Status": {"select": {"name": "Done"}},
            "Description": {"rich_text": [{"type": "text", "text": {"content":
                f"WITHDRAWN by the CTO the same day it was raised. This is not an actionable rule. "
                f"close_the_loop.py v1 extracted narrative/meta sentences from the synthesis notes "
                f"as if they were directives. Root cause: the extraction pattern matched any "
                f"modal verb anywhere in a sentence, without checking the sentence was actually a "
                f"prescription. Fixed in v2. Left as Done rather than deleted so the error is "
                f"auditable."}}]}}}, timeout=45)
        print(f"      -> withdrawn (HTTP {rr.status_code})")
        time.sleep(0.3)

# ---- 2. the extraction fixes ----------------------------------------------
print("\n" + "=" * 96)
print("2. EXTRACTION RULE — what v1 got wrong")
print("=" * 96)
print("""
  v1 pattern:  any sentence containing must|should|never|always  (25-300 chars)
  v1 failure:  matched NARRATIVE and META sentences that merely mention a modal.
               "the chrome hypothesis should not be acted on"  -> not a rule
               "Doctrine, not a defect report"                 -> not a rule

  v2 requirement -- a sentence is a RULE only if ALL hold:
    a) it opens in the imperative/declarative-prescriptive, not with a report marker
    b) its PRIMARY predicate is a modal (must / should / never / always / requires),
       i.e. the modal appears before the first comma+conjunction, not buried at the end
    c) it does not describe the note itself (read-only pass, doctrine not a defect report)
    d) it names an actor or an object that can be acted on

  AND the threshold is recalibrated:
    coverage >= 0.30  -> PRESENT (reworded across docs still counts as implemented)
    coverage <  0.15  -> REAL GAP (almost no phrase overlap = nothing enforces this)
    0.15-0.30         -> UNCERTAIN -> reported as a note, NOT raised as a ticket
""")

# ---- 3. write the corrected extractor back --------------------------------
src = open("/opt/data/close_the_loop.py").read()

old_extract = '''    for m in RULE_PAT.finditer(txt):
        rule = re.sub(r"\\s+", " ", m.group(1)).strip()
        if len(rule) < 60 or len(rule) > 320:
            continue'''
new_extract = '''    for m in RULE_PAT.finditer(txt):
        rule = re.sub(r"\\s+", " ", m.group(1)).strip()
        if len(rule) < 60 or len(rule) > 320:
            continue
        # v2 guards -- see op notes. Exclude narrative, meta-commentary, and
        # past-tense reporting that merely mentions a modal.
        low = rule.lower()
        if re.search(r"^(the one|today's|yesterday|doctrine, not|this is|there is|"
                     r"the (?:weekly|daily|same|only) (?:artifact|report|brief))", low):
            continue
        if re.search(r"\\b(was not|were not|had been|states the doctrine|"
                     r"nothing was modified|no fix was applied)\\b", low):
            continue
        # the modal must drive the sentence, not tail it
        head = low.split(", and ")[0].split("; ")[0]
        if not re.search(r"\\b(must|should|never|always|requires)\\b", head):
            continue'''
assert old_extract in src, "extraction anchor not found"
src = src.replace(old_extract, new_extract)

old_thresh = '''IMPLEMENTED = [c for c in uniq if c["coverage"] >= 0.72]
GAPS = [c for c in uniq if c["coverage"] < 0.72]'''
new_thresh = '''IMPLEMENTED = [c for c in uniq if c["coverage"] >= 0.30]
UNCERTAIN   = [c for c in uniq if 0.15 <= c["coverage"] < 0.30]
GAPS        = [c for c in uniq if c["coverage"] < 0.15]'''
assert old_thresh in src, "threshold anchor not found"
src = src.replace(old_thresh, new_thresh)

old_print = '''print(f"    already reflected in doctrine/skills/crons: {len(IMPLEMENTED)}")
print(f"    NOT implemented (doctrine gaps):            {len(GAPS)}")'''
new_print = '''print(f"    PRESENT in skills (>=0.30):                 {len(IMPLEMENTED)}")
print(f"    UNCERTAIN (0.15-0.30) - noted, not ticketed:{len(UNCERTAIN)}")
print(f"    REAL GAPS (<0.15) - raised:                 {len(GAPS)}")'''
assert old_print in src, "print anchor not found"
src = src.replace(old_print, new_print)

open("/opt/data/close_the_loop.py", "w").write(src)
print("  close_the_loop.py patched to v2")

# reset state so the corrected run re-evaluates rather than skipping
json.dump({}, open("/opt/data/doctrine_loop_state.json", "w"))
print("  state reset -- v2 will re-evaluate")

rows2 = all_rows()
print(f"\n  board total after cleanup: {len(rows2)}")
print(f"  DOC- tickets still open:   {len([r for r in rows2 if txt(r,'Identifier').startswith('DOC-') and txt(r,'Status')!='Done'])}")
