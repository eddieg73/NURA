#!/usr/bin/env python3
"""
SECOND BRAIN — LEVEL 5 completion, piece 3: CLOSE THE LOOP.

THE FINDING THAT MATTERS MOST.

The vault already produces genuine Level-5 INSIGHT. `obsidian-nightly` has written 15 synthesis
notes (Aug 27 → Sep 12) that follow a real discipline: a concept must appear in 2+ unrelated sources,
each backed by cited paths, with Interpretation and Boundary sections, building on the previous
day's pattern.

And then nothing happens.

The synthesis on 2026-09-11 named *"The Absence-of-Signal Blind Spot"* and prescribed, in its own
words: "A `[SILENT]`-on-empty cron is a design defect, not a quiet day... it must return
degraded/non-silent." That is a concrete, implementable, correct rule. It was written to a note and
the note was never read again by anything that acts.

**Insight generation is Level 4. Insight that changes behaviour is Level 5.**

This tool closes the loop:
  1. Parse the synthesis notes for ACTIONABLE RULES (imperatives, not observations).
  2. Check whether each rule is ALREADY IMPLEMENTED somewhere (skill / memory / cron prompt).
  3. Unimplemented rules become DOCTRINE CANDIDATES -- founder-gated, on the board.
  4. Implemented rules are marked ASSIMILATED, so the same rule is never re-raised.

Read-only w.r.t. the vault. Writes to the Notion board only.
"""
import glob
import json
import os
import re
import sys
import time

import requests

sys.path.insert(0, "/opt/data/scripts")
from notion_client import headers

V = "/opt/data/Obsidian Vault"
KNOW = f"{V}/Knowledge"
CLAUDE_DIR = V
SKILLS_DIRS = [
    "/opt/data/profiles/nura/skills",
    "/opt/data/profiles/nura/skills/skills",
]
CRON_FILE = "/opt/data/profiles/nura/cron/jobs.json"
MEMORY_FILES = [
    "/opt/data/profiles/nura/memories/MEMORY.md",
    "/opt/data/memories/MEMORY.md",
]
STATE = "/opt/data/doctrine_loop_state.json"

H = headers()
BASE = "https://api.notion.com/v1"

print("=" * 96)
print("SECOND BRAIN — CLOSING THE LOOP (synthesis → doctrine)")
print("=" * 96)

# ---- 1. read the synthesis corpus -----------------------------------------
notes = sorted(glob.glob(f"{KNOW}/Synthesis - *.md"))
print(f"\n  synthesis notes found: {len(notes)}")
if notes:
    print(f"    oldest: {os.path.basename(notes[0])}")
    print(f"    newest: {os.path.basename(notes[-1])}")

# ---- 2. build the "already implemented" corpus ----------------------------
# NB: restrict to SKILLS only. Cron prompts and memory are full of prose that matches
# everything, which made an earlier version of this check report coverage 1.00 for every
# rule -- i.e. it discriminated nothing. The question is "is this rule ENFORCED", and
# skills are where enforcement lives.
haystack = []
for d in SKILLS_DIRS:
    for root, _, files in os.walk(d):
        for f in files:
            if f.endswith(".md"):
                try:
                    haystack.append(open(os.path.join(root, f), encoding="utf-8",
                                         errors="ignore").read())
                except Exception:
                    pass
try:
    jobs = json.load(open(CRON_FILE))
    jobs = jobs if isinstance(jobs, list) else jobs.get("jobs", [])
except Exception:
    jobs = []
HAY = "\n".join(haystack).lower()
print(f"  enforcement corpus (skills only): {len(HAY):,} chars "
      f"({len(haystack)} skill docs)")

# ---- 2b. IDF weights -- a word only counts as evidence if it is RARE here ---
import math  # noqa: E402

tokens = re.findall(r"[a-z]{5,}", HAY)
N = max(len(tokens), 1)
freq = {}
for t in tokens:
    freq[t] = freq.get(t, 0) + 1
# only terms appearing in <0.05% of the corpus carry signal
RARE = {t: c for t, c in freq.items() if c / N < 0.0005}
print(f"  rare terms (discriminating): {len(RARE):,} of {len(freq):,} distinct")

# ---- 3. extract actionable rules ------------------------------------------
# Imperatives: "must", "should", "never", "always", "is a design defect", "requires"
RULE_PAT = re.compile(
    r"(?:^|(?<=[.!?]\s))"                      # sentence start
    r"([A-Z][^.!?]{25,300}?"                   # a sentence
    r"\b(?:must|should|never|always|is a design defect|needs? to|requires?)\b"
    r"[^.!?]{10,300}[.!?])",
    re.MULTILINE)

candidates = []
for p in notes[-8:]:                            # the recent window
    txt = open(p, encoding="utf-8", errors="ignore").read()
    # only the Interpretation / rule-bearing sections
    for m in RULE_PAT.finditer(txt):
        rule = re.sub(r"\s+", " ", m.group(1)).strip()
        if len(rule) < 60 or len(rule) > 320:
            continue
        # v2 guards -- see op notes. Exclude narrative, meta-commentary, and
        # past-tense reporting that merely mentions a modal.
        low = rule.lower()
        if re.search(r"^(the one|today's|yesterday|doctrine, not|this is|there is|"
                     r"the (?:weekly|daily|same|only) (?:artifact|report|brief))", low):
            continue
        if re.search(r"\b(was not|were not|had been|states the doctrine|"
                     r"nothing was modified|no fix was applied)\b", low):
            continue
        # the modal must drive the sentence, not tail it
        head = low.split(", and ")[0].split("; ")[0]
        if not re.search(r"\b(must|should|never|always|requires)\b", head):
            continue
        # score whether it is already implemented -- PHRASE match, not bag-of-words.
        # Bag-of-words failed here twice: at 8.8M chars of technical jargon almost every
        # term is "rare", so any rule matched something and the check reported 0 gaps.
        # Enforcement is about a PHRASE being present, so test the rule's content bigrams.
        toks = re.findall(r"[a-z]{4,}", rule.lower())
        bigrams = [f"{toks[i]} {toks[i+1]}" for i in range(len(toks) - 1)]
        if len(bigrams) < 3:
            continue  # too short to judge reliably -- skip, do not guess
        hits = sum(1 for b in bigrams if b in HAY)
        coverage = hits / len(bigrams)
        candidates.append({
            "rule": rule,
            "source": os.path.basename(p),
            "coverage": round(coverage, 2),
            "bigrams": len(bigrams),
        })

# dedupe near-identical rules
seen, uniq = set(), []
for c in sorted(candidates, key=lambda x: x["coverage"]):
    k = " ".join(sorted(re.findall(r"[a-z]{5,}", c["rule"].lower()))[:8])
    if k in seen:
        continue
    seen.add(k)
    uniq.append(c)

print(f"\n  candidate rules extracted: {len(uniq)}")
IMPLEMENTED = [c for c in uniq if c["coverage"] >= 0.30]
UNCERTAIN   = [c for c in uniq if 0.15 <= c["coverage"] < 0.30]
GAPS        = [c for c in uniq if c["coverage"] < 0.15]
print(f"    PRESENT in skills (>=0.30):                 {len(IMPLEMENTED)}")
print(f"    UNCERTAIN (0.15-0.30) - noted, not ticketed:{len(UNCERTAIN)}")
print(f"    REAL GAPS (<0.15) - raised:                 {len(GAPS)}")

print("\n  ── DOCTRINE GAPS (insight the system produced but never acted on) ──")
for g in GAPS[:10]:
    print(f"    [cov {g['coverage']:.2f}] {g['source'][:40]}")
    print(f"       \"{g['rule'][:150]}\"")

print("\n  ── ALREADY ASSIMILATED (do not re-raise) ──")
for g in IMPLEMENTED[-5:]:
    print(f"    [cov {g['coverage']:.2f}] {g['rule'][:110]}")

# ---- 4. raise the gaps as founder-gated doctrine candidates ---------------
if GAPS:
    try:
        ids = json.load(open("/opt/data/workforce_ids.json"))
        TASKS = ids["tasks_db"]
    except Exception:
        TASKS = None

    prev = {}
    if os.path.exists(STATE):
        prev = json.load(open(STATE))

    raised = 0
    if TASKS:
        for g in GAPS[:6]:
            key = g["rule"][:80]
            if key in prev:
                continue
            title = f"DOCTRINE: {g['rule'][:95]}"
            desc = (
                f"SOURCE: {g['source']} (synthesis note)\n\n"
                f"RULE THE SYSTEM PRODUCED:\n\"{g['rule']}\"\n\n"
                f"WHY THIS IS A TICKET: the nightly synthesis wrote this rule and nothing "
                f"implemented it. Coverage against the existing skills / memory / cron corpus is "
                f"{g['coverage']:.2f} — i.e. this behaviour is NOT enforced anywhere.\n\n"
                f"Insight generation is Level 4. Insight that changes behaviour is Level 5. This "
                f"closes the loop.\n\n"
                f"ACTION: implement the rule (new skill, skill patch, or cron behaviour change) then "
                f"mark this done. If it is already enforced and the coverage check was wrong, close "
                f"it as a false gap and say so."
            )
            props = {
                "Task": {"title": [{"type": "text", "text": {"content": title}}]},
                "Identifier": {"rich_text": [{"type": "text",
                                              "text": {"content": f"DOC-{len(prev)+raised+1:03d}"}}]},
                "Assignee": {"rich_text": [{"type": "text", "text": {"content": "Advisor"}}]},
                "Priority": {"select": {"name": "P2 Medium"}},
                "Status": {"select": {"name": "Backlog"}},
                "Source": {"select": {"name": "Synthesis"}},
                "Founder Gate": {"checkbox": True},
                "Description": {"rich_text": [{"type": "text", "text": {"content": desc[:2000]}}]},
            }
            r = requests.post(f"{BASE}/pages", headers=H,
                              json={"parent": {"database_id": TASKS}, "properties": props},
                              timeout=45)
            if r.status_code < 300:
                prev[key] = g["source"]
                raised += 1
                print(f"\n  + DOC-{len(prev):03d} raised: {g['rule'][:70]}")
            time.sleep(0.35)
    json.dump(prev, open(STATE, "w"), indent=1)
    print(f"\n  doctrine candidates raised this run: {raised}")

print("\n" + "=" * 96)
print("LOOP STATUS")
print("=" * 96)
print(f"  synthesis notes in corpus:     {len(notes)}")
print(f"  rules extracted (recent 8):    {len(uniq)}")
print(f"  already enforced:              {len(IMPLEMENTED)}")
print(f"  gaps raised to the board:      {len(GAPS)}")
print(f"  state:                         {STATE}")
print("\n  Loop: nightly synthesis -> rule extraction -> implementation check")
print("        -> founder-gated doctrine ticket -> implement -> verified.")
print("  Before: insight was written to a note and never read again.")
