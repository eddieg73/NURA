#!/usr/bin/env python3
"""
CORRECTED audit of two things my first pass got WRONG.

MISTAKE 1: "UNMONITORED SYSTEMS: 0" -- a FALSE ALL-CLEAR.
My first coverage check keyword-matched a blob of every job's name+prompt. At 97 jobs x long prompts
that matched nearly everything: "marine forecast" was credited with monitoring disk/space, and
"self-improvement, evolution review, marine forecast" with monitoring external endpoints. Useless.
A coverage claim is only worth something if a FAILURE would be noticed.

Better question: does a job exist whose name/purpose is to PROBE this system and report when it is
unhealthy? Require the keyword in the job NAME or in a monitor script path, not anywhere in prose.

MISTAKE 2: "monitor-gated: 0" while I had minutes earlier created a monitor-gated job.
The cron schema stores it as `monitor_script`, not `monitor`. Check the real field.

Then: the concrete defects, which are more actionable than a fuzzy coverage score.
"""
import ast
import json
import os
import re
import subprocess
import sys
from collections import Counter, defaultdict

PROFILE = "/opt/data/profiles/nura"
jobs_raw = json.load(open(f"{PROFILE}/cron/jobs.json"))
jobs = jobs_raw if isinstance(jobs_raw, list) else jobs_raw.get("jobs", [])

print("=" * 92)
print("CORRECTION 1 — monitor-gated jobs (the real field is `monitor_script`)")
print("=" * 92)
for key in ("monitor", "monitor_script", "no_agent", "script"):
    n = sum(1 for x in jobs if x.get(key))
    print(f"  jobs with '{key}': {n}")
print("\n  the monitor-gated ones:")
for x in jobs:
    if x.get("monitor_script"):
        print(f"    {x.get('name','?'):<34} monitor={x.get('monitor_script')} "
              f"sched={(x.get('schedule') or {}).get('expr','')}")
    elif x.get("monitor"):
        print(f"    {x.get('name','?'):<34} monitor={str(x.get('monitor'))[:60]}")

print("\n" + "=" * 92)
print("CORRECTION 2 — coverage by PROBE, not by keyword coincidence")
print("=" * 92)
# A system counts as monitored only if a job NAME (or its monitor script) names it.
# Prose mentions do not count -- that is what produced the false all-clear.
named = {x.get("name", "").lower(): x for x in jobs}
monitored_by = defaultdict(list)
for x in jobs:
    nm = (x.get("name") or "").lower()
    ms = (x.get("monitor_script") or "").lower()
    sc = (x.get("script") or "").lower()
    probe = f"{nm} {ms} {sc}"
    monitored_by[nm].append(x)

SYSTEMS = {
    "gateway process":       ["gateway"],
    "tailnet / tailscale":   ["tailscale", "tailnet"],
    "gateway lanes (state)": ["lane state", "lane-state"],
    "qdrant":                ["qdrant", "vector"],
    "redis":                 ["redis"],
    "docker fleet":          ["docker", "fleet"],
    "disk / space":          ["space", "disk"],
    "swap / memory":         ["swap", "memory"],
    "cron roster":           ["cron"],
    "backups":               ["backup", "restic"],
    "MCP lanes":             ["mcp"],
    "clinical stack":        ["openemr", "mirth", "fhir", "medplum", "clinical"],
    "RIS / PACS":            ["pacs", "ris"],
    "proxy / TLS":           ["ssl", "tls", "proxy", "cert"],
    "Notion":                ["notion"],
    "n8n":                   ["n8n"],
    "deploys / drift":       ["drift", "deploy", "upgrade"],
    "email lane":            ["mail", "email", "imap"],
    "external endpoints":    ["endpoint", "uptime", "health probe"],
    "lab intake":            ["lab intake", "provider lab"],
    "incidents":             ["incident"],
    "autonomy / self-heal":  ["autonomy", "self-heal", "self heal"],
}

print(f"{'SYSTEM':<26}{'WATCHER?':<11}watching job (name or monitor match)")
print("-" * 92)
uncovered = []
for sysname, kws in SYSTEMS.items():
    hits = []
    for x in jobs:
        nm = (x.get("name") or "").lower()
        ms = (x.get("monitor_script") or "").lower()
        if any(k in nm or k in ms for k in kws):
            hits.append(x.get("name"))
    covered = bool(hits)
    if not covered:
        uncovered.append(sysname)
    print(f"{sysname:<26}{('YES' if covered else '** NO **'):<11}{', '.join(str(h) for h in hits[:3]) or '-'}")
print("-" * 92)
print(f"\n  GENUINELY UNMONITORED: {len(uncovered)}")
for u in uncovered:
    print(f"    ** {u}")

# ── concrete defects ──────────────────────────────────────────────────────
print("\n" + "=" * 92)
print("CONCRETE DEFECTS")
print("=" * 92)

print("\n  A. crons in error state:")
for x in jobs:
    if x.get("last_status") == "error":
        print(f"    {x.get('name','?'):<34} sched={(x.get('schedule') or {}).get('expr','')}")
        print(f"      err: {str(x.get('last_fire_error') or x.get('last_delivery_error') or '')[:110]}")
        print(f"      last_run: {x.get('last_run_at')}")

print("\n  B. duplicate skill names (real collisions to inspect):")
SK = [f"{PROFILE}/skills", "/opt/data/skills"]
names = defaultdict(list)
for base in SK:
    if not os.path.isdir(base):
        continue
    for root, dirs, files in os.walk(base):
        if "SKILL.md" in files:
            names[os.path.basename(root)].append(os.path.join(root, "SKILL.md"))
dupes = {k: v for k, v in names.items() if len(v) > 1}
print(f"    count: {len(dupes)}")
same_dir_lineage = 0
for k, v in list(dupes.items())[:10]:
    sizes = [os.path.getsize(p) for p in v]
    ident = "IDENTICAL" if len(set(open(p, errors='ignore').read() for p in v)) == 1 else "DIFFERENT"
    print(f"      {k:<40} copies={len(v)} sizes={sizes} {ident}")
    for p in v:
        print(f"          {p}")

# ---- the syntax error -----------------------------------------------------
print("\n  C. the one script that does not compile:")
p = "/opt/data/NURA/scripts/paperclip-product-companies.py"
if os.path.exists(p):
    try:
        compile(open(p).read(), p, "exec")
        print("    now compiles")
    except SyntaxError as e:
        print(f"    {p}:{e.lineno}  {e.msg}")
        lines = open(p).read().splitlines()
        for i in range(max(0, e.lineno - 4), min(len(lines), e.lineno + 2)):
            mark = ">>" if i + 1 == e.lineno else "  "
            print(f"      {mark} {i+1:>4}: {lines[i]}")

json.dump({"uncovered": uncovered, "dupes": {k: v for k, v in dupes.items()}},
          open("/opt/data/estate_audit2.json", "w"), indent=1)
print("\n  -> /opt/data/estate_audit2.json")
