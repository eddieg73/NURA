#!/usr/bin/env python3
"""
BRIDGE: bind the EXISTING Hermes cron workforce to the recovered agent registry.

The 95 live cron jobs ARE the workforce. This maps each cron job to the agent identity
that performs it, then marks the registry so the dashboard shows who is actually staffed
versus who exists only as an inherited role.

No new jobs are created here (scrum doctrine: consolidate, don't grow the roster).
"""
import collections
import json
import re
import sys
import time
import requests

sys.path.insert(0, "/opt/data/scripts")
from notion_client import headers

H = headers()
BASE = "https://api.notion.com/v1"
IDS = json.load(open("/opt/data/workforce_ids.json"))
REG = IDS["registry_db"]

JOBS = json.load(open("/opt/data/profiles/nura/cron/jobs.json"))
jobs = JOBS if isinstance(JOBS, list) else JOBS.get("jobs", [])
print(f"live cron jobs: {len(jobs)}")

# ---- map a cron job to an agent identity via its name/goal ----------------
RULES = [
    (r"scrum|sprint|review|standup", "Atlas"),
    (r"fleet|docker|server|tunnel|connectivity|load", "Helm"),
    (r"swap|health|incident|self-heal|watchdog|drift|e2e", "Sentinel"),
    (r"backup|snapshot|space|storage|pacs storage", "Helm"),
    (r"cost|billing|accounts", "Controller"),
    (r"mail|legal|inbox|contract", "Legal & Contracts Lead"),
    (r"clinical|drug|literature|lab|emed|cme|license|carepilot|coding",
     "Clinical Trends Analyst"),
    (r"mcp|lane|connector|integration|notion|zapier|n8n", "MCP Servers & Connections Developer"),
    (r"blog|social|moltbook|x check|marketing|competitive|content", "Iris"),
    (r"osint|disclosure|uap|threat|intel|competitor", "Head of Research"),
    (r"weather|hurricane|marine|noaa", "Probe"),
    (r"memory|vault|obsidian|session|context|skill", "Nexus"),
    (r"build|code|deploy|upgrade|hermes image|hermes update", "Orion"),
    (r"self-improvement|evolution|self-reflect|auto-dream|idle work", "Advisor"),
    (r"morning|evening|digest|briefing|ops report|work summary|command-center",
     "Summarizer"),
]


def agent_for(name, prompt):
    blob = f"{name} {prompt[:400]}".lower()
    for pat, agent in RULES:
        if re.search(pat, blob):
            return agent
    return None


mapping = collections.defaultdict(list)
unmapped = []
for j in jobs:
    if not j.get("enabled"):
        continue
    a = agent_for(j.get("name", ""), j.get("prompt_preview", "") or "")
    if a:
        mapping[a].append(j)
    else:
        unmapped.append(j.get("name", "?"))

print(f"\nmapped agents: {len(mapping)}   unmapped jobs: {len(unmapped)}")
for a, js in sorted(mapping.items(), key=lambda kv: -len(kv[1])):
    print(f"  {len(js):>3}  {a:<42} e.g. {js[0].get('name')}")

print(f"\nunmapped (kept visible): {unmapped[:12]}")

# ---- write Runtime + note back onto the registry --------------------------
def q_registry():
    out, cur = [], None
    while True:
        b = {"page_size": 100}
        if cur:
            b["start_cursor"] = cur
        r = requests.post(f"{BASE}/databases/{REG}/query", headers=H, json=b, timeout=45)
        d = r.json()
        out += d.get("results", [])
        if not d.get("has_more"):
            break
        cur = d.get("next_cursor")
    return out


def txt(page, field):
    v = (page.get("properties") or {}).get(field) or {}
    return "".join(x.get("plain_text", "") for x in v.get(v.get("type"), []))


print("\n" + "=" * 96)
print("UPDATING AGENT REGISTRY with live runtime bindings")
print("=" * 96)
ok = 0
for row in q_registry():
    name = txt(row, "Agent")
    js = mapping.get(name)
    if js:
        runtime = "Hermes cron"
        note = (f"STAFFED — bound to {len(js)} live cron job(s): "
                f"{', '.join(j.get('name','?') for j in js[:5])}")
        if len(js) > 5:
            note += f" (+{len(js)-5} more)"
    else:
        runtime = "Not staffed"
        note = "Inherited role from Paperclip 2026-08-03. No live worker bound yet."
    props = {
        "Runtime": {"select": {"name": runtime}},
        "Notes": {"rich_text": [{"type": "text", "text": {"content": note[:1900]}}]},
    }
    r = requests.patch(f"{BASE}/pages/{row['id']}", headers=H, json={"properties": props}, timeout=45)
    if r.status_code < 300:
        ok += 1
    time.sleep(0.3)
print(f"  registry rows updated: {ok}")

staffed = len(mapping)
print(f"\n  STAFFED agents (have live cron workers): {staffed}")
print(f"  UNSTAFFED inherited roles:               {72 - staffed}")
json.dump({k: [j.get("job_id") for j in v] for k, v in mapping.items()},
          open("/opt/data/agent_cron_bindings.json", "w"), indent=1)
print("-> /opt/data/agent_cron_bindings.json")
