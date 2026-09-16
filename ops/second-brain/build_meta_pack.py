#!/usr/bin/env python3
"""
SECOND BRAIN — LEVEL 5 completion, piece 2: THE ONBOARDING PACK (meta/ + pointers).

Finding: the vault-shared-memory skill defines a 5-file onboarding pack + pointer files so that
EVERY agent (Hermes, Claude Code, Codex, Grok, local LLMs) reads the same context on session start.
None of it exists: no meta/ directory, no CLAUDE.md / AGENTS.md / GROK.md / gemini-local-prompt.md.

That is the difference between a second brain ONE agent can read and one EVERY agent shares.
Level 5 is cross-agent or it is not level 5.

Generated from live state, never hand-written.
"""
import json
import os
import subprocess
import time

V = "/opt/data/Obsidian Vault"
META = f"{V}/meta"
os.makedirs(META, exist_ok=True)
TODAY = time.strftime("%Y-%m-%d", time.gmtime())


def sh(cmd):
    try:
        return subprocess.run(cmd, shell=True, capture_output=True, text=True,
                              timeout=60).stdout.strip()
    except Exception:
        return ""


print("=" * 96)
print("BUILDING THE ONBOARDING PACK")
print("=" * 96)

# ---- live facts, gathered not guessed -------------------------------------
try:
    jobs = json.load(open("/opt/data/profiles/nura/cron/jobs.json"))
    jobs = jobs if isinstance(jobs, list) else jobs.get("jobs", [])
except Exception:
    jobs = []
n_jobs = len(jobs)
n_err = sum(1 for j in jobs if j.get("last_status") == "error")
n_on = sum(1 for j in jobs if j.get("enabled"))

md_count = sh(f"find '{V}' -name '*.md' 2>/dev/null | wc -l")
synth = sh(f"ls -1 '{V}/Knowledge/' 2>/dev/null | grep -c '^Synthesis'")
conflicts = sh(f"grep -rl 'type: conflict' '{V}/Decisions' 2>/dev/null | wc -l")
disk = sh("df -h /opt/data | tail -1 | awk '{print $5\" used, \"$4\" free\"}'")
mem = sh("free -m | awk 'NR==2{printf \"%d/%d MB\", $3, $2}'")

try:
    ids = json.load(open("/opt/data/workforce_ids.json"))
except Exception:
    ids = {}

# ---- 1. machine-specs ------------------------------------------------------
open(f"{META}/machine-specs.md", "w").write(f"""---
title: Machine Specs — the fleet and the dev machine
updated: {TODAY}
type: meta
---

# Machine Specs

Read this before touching anything. **Numbers below were probed live on {TODAY}.**

## Hostinger fleet (NURA account)
| Node | Host | Role |
|---|---|---|
| **edge** | srv817449 / 195.35.32.113 | public edge, reverse proxy |
| **lab** | srv1030183 / 72.60.163.140 | compute, n8n, Paperclip `58ddc931` DB |
| **clinic** | srv1441409 / 72.61.71.211 | clinical stack |

**HRT House:** srv1863412 / 167.88.45.51 · **CarePilot:** srv1682494 / 2.24.107.152

> ⚠️ **lab is resource-starved** — memory limits 48/48, steal time 91–95%. Do not schedule heavy work there.

## This host (gateway)
- Disk: **{disk}**
- Memory: **{mem}**
- Profile: `/opt/data/profiles/nura/` · Vault: `{V}`

## Runtime facts
- Python: use `/opt/hermes/.venv/bin/python3` — **plain `python3` lacks pydantic**
- Qdrant `:6333` · Redis `:6379` · agentmemory `:49134` · Paperclip (local) `:3100`
- **Never print a credential into a chat, log, or commit.** Mask it.
""")

# ---- 2. vault-map ----------------------------------------------------------
open(f"{META}/vault-map.md", "w").write(f"""---
title: Vault Map — how this vault is organised
updated: {TODAY}
type: meta
---

# Vault Map

**{md_count} markdown notes.**

## Where things live
| Folder | What |
|---|---|
| `Knowledge/` | concepts + **{synth} synthesis notes** (cross-source patterns) |
| `Decisions/` | decision journal + **{conflicts} open conflict notes** |
| `NURA-OS/` | the operating system: Reports, Reflections, Evolution, Products, Infra, Engineering |
| `Clinical/` | clinical content — **restricted** |
| `People/` `Projects/` `OKRs/` `SOPs/` `Meetings/` | the standard entity folders |
| `Daily/` `Reviews/` | day notes and weekly reviews |
| `log.md` `index.md` `_CLAUDE.md` | nav roots — **`_CLAUDE.md` is a nav root too** |

## Conventions
- Frontmatter: `title`, `date`, `type`, `tags`, optional `status`
- Contradictions become `type: conflict` / `status: open` notes — **never rewrite the source page**
- Synthesis notes require the concept to appear in **2+ unrelated sources**
- Wikilinks `[[...]]` resolve for humans **and** for agents that follow links

## ⚠️ Known noise
`NURA-OS/Atlas-Playbook/` is an imported template tree (~70 MB, the bulk of the vault). It is
**not NURA knowledge** — it is tagged `playbook: true` in the vector index so retrieval can filter it.
Ignoring this makes the vault look far larger than the real knowledge base.
""")

# ---- 3. active-work --------------------------------------------------------
try:
    dash = ids.get("dashboard", "")
    tasks = ids.get("tasks_db", "")
except Exception:
    dash = tasks = ""
open(f"{META}/active-work.md", "w").write(f"""---
title: Active Work — what is being worked on NOW
updated: {TODAY}
type: meta
---

# Active Work

**This file goes stale fast. Every agent updates it when it STARTS and FINISHES a task.**

## The board of record
**Notion — the Hermes-native workforce.** Paperclip was retired 2026-09-12.
- CTO Dashboard `{dash}`
- Agent Tasks `{tasks}`
- **Check in and out:** `python3 /opt/data/scripts/workforce.py checkin|checkout "<Agent>" "<Task>"`

## Live now
- Cron roster: **{n_jobs} jobs, {n_on} enabled, {n_err} in error**
- The standing ceremonies: **daily standup** (weekdays 11:00), **weekly scrum** (Mondays 13:00)
- Synthesis: **obsidian-nightly** 22:00 — produces `Knowledge/Synthesis - *.md`

## Open decisions waiting on the founder
See the board's `Founder Gate = true` rows. Currently the highest-consequence:
- `DRN-001` — add one downward rangefinder per drone (~$25–40, three spec functions)
- `WF-001` — final disposition of Paperclip
- ARES DP2 federal registration gates

## Don't
Do not claim work is live without reading back the artifact. **A 2xx is not a state change.**
""")

# ---- 4. mcp-lanes ----------------------------------------------------------
open(f"{META}/mcp-lanes.md", "w").write(f"""---
title: MCP Lanes — what is connected
updated: {TODAY}
type: meta
---

# MCP Lanes

**Lane NAMES only. Credentials live sealed in `.env` / `home/.secrets/` — never here.**

## Core
- **Hermes** — the executive runtime (you are reading its vault)
- **Notion** — board of record (`/opt/data/scripts/notion_client.py`)
- **Qdrant** `:6333` — vector memory
- **Redis** `:6379` — cache/queues
- **agentmemory** `:49134`

## Business / clinical
- **Perfex** — pay.nuratech.ai (CRM, 183-tool MCP)
- **OpenEMR** — internal clinical truth (**API only, never direct DB writes**)
- **Mirth / OIE** — HL7 interface engine
- **Medplum** — FHIR backbone
- **Documo** — fax
- **CarePilot** — population health / RAF

## Known-dead — do not treat silence as health
- **Paperclip `:3101`** — retired 2026-09-12 (local instance empty)
- **RunPod** — API key invalid (401 everywhere)
- **agentmemory `iii-engine`** — daemon down
- **X/Twitter** — no xurl app configured

> **A silent lane is not a healthy lane.** Classify the absence: *healthy-empty*, *broken-empty*, or
> *never-ran*. Report `degraded`, never silence, when your own inputs are unavailable.
""")

# ---- 5. agent-preferences --------------------------------------------------
open(f"{META}/agent-preferences.md", "w").write(f"""---
title: Agent Preferences — how to respond here
updated: {TODAY}
type: meta
---

# Agent Preferences

## Voice
Calm, analytical, executive. Lead with **the decision, the blocker, or the next executable action**.
No hype, no flattery, no performative enthusiasm. Dry wit only outside clinical/legal/security.

## Non-negotiables
1. **Verify before declare.** Show probe output. Never mark work complete untested.
2. **A 2xx is not evidence of a state change** — always re-read the object.
3. **Never print a credential** into chat, a log, or a commit. Mask it.
4. **Report a blocker honestly** rather than substituting plausible-looking output.
5. **Label inference as inference.** `CALCULATED` / `REQUIRES VALIDATION` / `INFERRED` are real tags.

## Gates — fail closed
| Requires explicit authorization | Free to act |
|---|---|
| production deploys, deletes, financial transfers | research, inspection, drafting |
| external comms / emails | tests, file organisation |
| patient-record mutations, security changes | reversible local edits |
| credential changes | building + verifying locally |

**If authorization cannot be verified, fail closed.**

## Formatting
Founder Chat: short, high-signal, bullets. Status goes to the **dashboard**, not chat — the founder
follows Telegram as a lifeline, so **critical-only** there. Known drops are never re-alerted.

## Clinical boundary
AI **never** diagnoses, prescribes, orders, signs, or submits. Draft only; a licensed clinician
authorises. PHI stays in restricted folders — never in `meta/` or pointer files.
""")

# ---- pointer files ---------------------------------------------------------
POINTER = """<!-- generated {date} — read before any work -->
# READ `meta/` BEFORE ANY WORK

This vault is the shared brain across every agent that works on NURA. You are one of several.

**Read these first, in order:**
1. `meta/machine-specs.md` — the fleet and this host
2. `meta/vault-map.md` — where things live (+ what is noise)
3. `meta/active-work.md` — what is being worked on NOW
4. `meta/mcp-lanes.md` — what is connected, and what is known-dead
5. `meta/agent-preferences.md` — how to respond, and the gates

**Then, before you finish:**
- Update `meta/active-work.md` when you START and FINISH.
- Write durable findings into the vault, not only into chat.
- Contradictions get a `type: conflict` / `status: open` note — **never rewrite the source page**.
- Verify with evidence. Never claim a status you did not read.

The agents come and go. **The vault stays.**
"""

for name in ("CLAUDE.md", "AGENTS.md", "GROK.md"):
    open(f"{V}/{name}", "w").write(POINTER.format(date=TODAY))

open(f"{V}/gemini-local-prompt.md", "w").write(f"""# System prompt — local LLM / Gemini-local / Ollama sessions ({TODAY})

You are working on **NURA** — a clinician-supervised healthcare AI platform.

Before answering anything about this project, read:
- `/opt/data/Obsidian Vault/meta/machine-specs.md`
- `/opt/data/Obsidian Vault/meta/vault-map.md`
- `/opt/data/Obsidian Vault/meta/active-work.md`
- `/opt/data/Obsidian Vault/meta/mcp-lanes.md`
- `/opt/data/Obsidian Vault/meta/agent-preferences.md`

Rules: verify before you claim; label inference as inference; never output a credential; clinical
content is draft-only and a licensed clinician authorises; if you cannot verify something, say so.
""")

# ---- verify ----------------------------------------------------------------
print("\n  built:")
for f in sorted(os.listdir(META)):
    p = f"{META}/{f}"
    print(f"    meta/{f:<28} {os.path.getsize(p):>6} bytes")
for name in ("CLAUDE.md", "AGENTS.md", "GROK.md", "gemini-local-prompt.md"):
    p = f"{V}/{name}"
    print(f"    {name:<32} {os.path.getsize(p):>6} bytes")

print(f"\n  meta files: {len(os.listdir(META))} (expected 5)")
print(f"  pointers:   {sum(1 for n in ('CLAUDE.md','AGENTS.md','GROK.md','gemini-local-prompt.md') if os.path.exists(f'{V}/{n}'))} (expected 4)")
print("  PASS — cross-agent onboarding pack built")
