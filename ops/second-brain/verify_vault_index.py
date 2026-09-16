#!/usr/bin/env python3
"""
VERIFY the vault index — not by counting points, but by asking it questions and reading the answers.

A populated collection proves storage. It does NOT prove retrieval. The test is: given a question
whose answer exists somewhere in 643 notes, does the index surface the RIGHT note at the top?

Also checks the playbook filter, since 231 of 643 files are an imported template tree that would
otherwise pollute every result.
"""
import os
import sys

sys.path.insert(0, "/opt/data/lazy-packages")
os.environ.setdefault("PYTHONPATH", "/opt/data/lazy-packages:/opt/data/fastembed-pkgs")

import requests  # noqa: E402
from fastembed import TextEmbedding  # noqa: E402

COLL = "nura-vault"
Q = "http://localhost:6333"

# Each probe: the question, and a filename fragment that SHOULD be in the top hits.
PROBES = [
    ("what is the absence of signal blind spot",
     ["Absence-of-Signal"]),
    ("google sign-in SSO for Perfex and OpenEMR",
     ["SSO", "Perfex", "Google", "openemr"]),
    ("drone LiDAR landing zone sensing gap",
     ["Drone", "LiDAR", "drone", "EMS"]),
    ("DARPA ARES oxygen metrology validation",
     ["ARES", "oxygen", "Oxygen", "ares"]),
    ("memory pressure and swap saturation on the lab node",
     ["swap", "Memory", "memory", "Pressure"]),
    ("Paperclip retirement and the Hermes workforce",
     ["Paperclip", "workforce", "Workforce"]),
    ("MCP stateless core migration",
     ["MCP", "Stateless"]),
    ("what did we decide about the Reg A offering circular",
     ["RegA", "Reg-A", "SEC", "Offering"]),
]

print("=" * 92)
print("VAULT INDEX — RETRIEVAL VERIFICATION")
print("=" * 92)

info = requests.get(f"{Q}/collections/{COLL}", timeout=20).json().get("result", {})
pts = info.get("points_count", 0)
print(f"\n  collection : {COLL}")
print(f"  points     : {pts}")
print(f"  status     : {info.get('status')}")
print(f"  dim        : {info['config']['params']['vectors'].get('size')}")

# payload sanity
r = requests.post(f"{Q}/collections/{COLL}/points/scroll", timeout=30,
                  json={"limit": 3, "with_payload": True}).json()
print(f"\n  sample payloads:")
for p in r.get("result", {}).get("points", []):
    pl = p["payload"]
    print(f"    {pl.get('rel','?')[:64]}")
    print(f"      folder={pl.get('folder')} playbook={pl.get('playbook')} chunk={pl.get('chunk')}")

model = TextEmbedding(model_name="BAAI/bge-base-en-v1.5")
print("\n" + "=" * 92)
print("RETRIEVAL PROBES — does the right note come back?")
print("=" * 92)

hits = 0
for question, expect_frags in PROBES:
    v = list(model.embed([question]))[0].tolist()
    res = requests.post(f"{Q}/collections/{COLL}/points/search", timeout=90, json={
        "vector": v, "limit": 5, "with_payload": True}).json().get("result", [])

    found = None
    for rank, h in enumerate(res, 1):
        rel = h["payload"].get("rel", "")
        if any(f in rel for f in expect_frags):
            found = (rank, rel, h["score"])
            break

    top = res[0] if res else None
    mark = "PASS" if found else "MISS"
    if found:
        hits += 1
    print(f"\n  [{mark}] {question}")
    if top:
        print(f"        top hit  {top['score']:.3f}  {top['payload']['rel'][:70]}")
        print(f"                 {top['payload']['text'][:96].replace(chr(10),' ')}")
    if found:
        print(f"        expected at rank {found[0]}  ({found[2]:.3f})  {found[1][:60]}")
    else:
        print(f"        NO expected source in top 5 (wanted: {expect_frags})")

print("\n" + "=" * 92)
print(f"RETRIEVAL: {hits}/{len(PROBES)} probes surfaced an expected source in the top 5")
print("=" * 92)

# ---- playbook filter check ------------------------------------------------
print("\n  PLAYBOOK FILTER — can retrieval exclude the imported template tree?")
v = list(model.embed(["how to run a sprint retrospective meeting"]))[0].tolist()
filt = requests.post(f"{Q}/collections/{COLL}/points/search", timeout=90, json={
    "vector": v, "limit": 5, "with_payload": True,
    "filter": {"must": [{"key": "playbook", "match": {"value": False}}]}}).json().get("result", [])
print(f"    results with playbook=false: {len(filt)}")
for h in filt[:3]:
    print(f"      {h['score']:.3f}  playbook={h['payload'].get('playbook')}  {h['payload']['rel'][:60]}")
print("    => filter working" if filt and all(not h["payload"].get("playbook") for h in filt)
      else "    => check the filter")

sys.exit(0 if hits >= len(PROBES) * 0.7 else 1)
