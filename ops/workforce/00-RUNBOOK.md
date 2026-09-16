# NURA WORKFORCE — RUNBOOK
Hermes-native agent organisation. Built 2026-09-12 by the CTO (Hermes) at the founder's direction,
replacing the stalled Paperclip control plane.

---

## 1. WHAT THIS REPLACED, AND WHY

**The inherited state.** Paperclip ran a 72-agent org at `paperclip.nuratech.ai`. When the local
control plane was inspected it was **empty** — a fresh install with 5 tables and 186 rows
(user/roles/settings only). The public board returned HTTP 000. The last complete copy of the org
was a **2026-08-03 snapshot**, 160 MB.

**Diagnosis of that org (from the recovered data — real numbers, not impressions):**

| Metric | Value |
|---|---|
| Companies | 2 (`999ff375` Nuratech.ai · `425ddbd7` NURA Imaging SaaS Division) |
| Agents | 72 |
| Issues | 148 — **145 blocked, 1 done, 2 todo, 0 in progress** |
| Agents in `error` state | **22** (incl. Atlas the CEO, Orion the CTO, Canvas the Mobile Lead) |
| Load concentration | **Canvas held 134 of 147 open items (91%)** |
| Heartbeat runs recorded | 849 — so agents *were* being driven |
| Adapter breakdown | **47 `hermes_gateway`** · 21 `process` · 4 `claude_local` |

**Two conclusions:**

1. **The org design was good; the execution was stalled.** Real roles, sensible hierarchy. But 98% of
   the board was blocked and the three most senior technical agents were all erroring.
2. **Hermes was already the engine.** 47 of 72 agents were `hermes_gateway` adapters. Paperclip was a
   ledger and a UI wrapped around Hermes executors — never a separate source of work.

**And the backup system lied.** The live Paperclip instance reported `databaseBackup.status: ok` with
163 backups. **Every recent backup was 37 KB / 5 tables — empty.** Green across the board while the org
was gone. That is the "lying watchdog" failure mode, and it is why this rebuild puts health on the
board rather than in a status field nobody checks.

---

## 2. THE OPERATING MODEL

**Execution → Hermes. Board of record → Notion. One source of truth.**

| Layer | Mechanism | Properties |
|---|---|---|
| Standing workers | **Hermes cron** | Durable, survive restarts, monitor-gated |
| Parallel bursts | **Hermes `delegate_task`** | Isolated contexts, up to 10 parallel, **ephemeral** |
| Board of record | **Notion** | Persistent, visible to founder + ChatGPT |
| Paperclip | **Retired** | Kept only as an 2026-08-03 recovery artifact |

**Standing workers check in and out. Subagents do not persist** — they are called in for a specific
push and are gone when the session ends. Being explicit about this prevents the expectation that a
subagent is a staffed employee.

---

## 3. THE NOTION SURFACES

Parent page: **🤖 NURA AGENT WORKFORCE** — `3d9a9b14-e498-814f-a7df-f415d625fbf5`

| Surface | ID | Contents |
|---|---|---|
| **CTO Dashboard** | `3d9a9b14-e498-81be-8f95-e1ac9b6d5a34` | Command view — headline, roster, board, load, check-ins, operating rules |
| Agent Registry | `3d9a9b14-e498-81c3-b70c-ee66dd81f8be` | 72 agents — role, division, reports-to, status, **runtime binding** |
| Agent Tasks | `3d9a9b14-e498-8157-9fda-fef9682a5031` | 148 tasks — recovered + new, with assignee/priority/gate |
| Agent Check-in Log | `3d9a9b14-e498-81c9-bde7-d7b81bd463dc` | Every check-in, check-out, block, handoff |

All 72 agents and 148 issues were migrated **verified** (72/72, 148/148, zero failures).

### Verification state — 9/9 alignment checks pass

`ops/workforce/verify_workforce.py` and `ops/workforce/align_review.py` are re-runnable at any time.

| Check | Result |
|---|---|
| Description coverage | 148/148 — **213,519 source chars vs 213,519 board chars = 100.0% retained** |
| No truncation | longest description stored in full at 4,042 chars |
| No orphaned assignees | 19 distinct assignees, 0 missing from the registry |
| No single-agent overload | **peak 29%** (Paperclip was 91%) |
| All tasks have a status | Blocked 145 · Backlog 2 · Done 1 |
| All tasks have a priority | P0 21 · P1 114 · P2 12 · P3 1 |
| Runtime binding applied | 14 staffed · 58 inherited |
| No duplicate agent names | resolved |
| No duplicate task identifiers | 0 |

### Four defects the verification found and fixed (they were mine, caught by re-reading)

1. **Descriptions were not migrated at all** — the severe one. All 148 issues carry substantive text
   (founder directives, acceptance criteria), 213,519 characters, and the board held none of it.
   Backfilled; 100% retained by character count.
2. **Silent truncation** — Notion caps one rich_text object at 2,000 chars, so 20 descriptions were
   cut (8,917 characters at risk). Re-written as chunked multi-object rich_text.
3. **The Paperclip 91% overload was faithfully migrated.** Canvas held 134/148 tasks. Migrating broken
   structure is not a rebuild — redistributed across 15 agents by engineering domain. **91% → 29%.**
4. **Duplicate agent roles** — `Summarizer ×2` and `Reflection Coach ×2`, both pairs `claude_local`,
   double-created from a template. Disambiguated by reporting context; neither record deleted.

Plus: the literal string `Unassigned` was not an agent (NUR-146, NUR-147) → real empty field.

**Every change is reversible** — `alignment_rollback.json` maps each re-assignment and rename.

---

## 4. CHECK-IN / CHECK-OUT DISCIPLINE

The only writer is `/opt/data/scripts/workforce.py`. Every worker uses it.

```bash
# before starting work
python3 /opt/data/scripts/workforce.py checkin  "<Agent>" "<Task>" --note "<what you're doing>"

# when finished — --outcome is REQUIRED (no silent carries)
python3 /opt/data/scripts/workforce.py checkout "<Agent>" "<Task>" \
      --outcome "<what happened>" --evidence "<command / path / probe result>"

# when stuck — --reason is REQUIRED
python3 /opt/data/scripts/workforce.py blocked  "<Agent>" "<Task>" --reason "<blocker + next action>"

# who is in right now / board summary
python3 /opt/data/scripts/workforce.py status
python3 /opt/data/scripts/workforce.py board
```

**Rules:**
- Check in **before** work, check out **with an outcome**. No silent carries.
- **Blocked** is a first-class state and must name the blocker *and* the exact next action.
- **Evidence** is mandatory for any claim of done — a command, a path, or a probe result.
- Founder-gated work never auto-executes. It shows on the dashboard and waits.

---

## 5. WHO IS ACTUALLY STAFFED

The registry's **Runtime** column is the truth:

- **`Hermes cron` — STAFFED.** Bound to live cron jobs. **13 agents** currently hold **82 live jobs**.
- **`Not staffed` — 59 inherited roles.** Exist on the register with no worker bound. Real titles, no
  execution. Do not report these as operating.

**The 13 staffed agents and their load:**

| Agent | Jobs | Covers |
|---|---|---|
| Sentinel | 14 | health, swap, incident, self-heal, drift, e2e watchdogs |
| Helm | 10 | fleet, docker, server, tunnel, connectivity, backups, space |
| Iris | 8 | blog, social, Moltbook, X, marketing, competitive |
| Clinical Trends Analyst | 7 | clinical, drug safety, literature, lab, CME, licences |
| Advisor | 7 | self-improvement, evolution, reflection |
| Nexus | 7 | memory, vault, obsidian, session, context, skills |
| Summarizer | 6 | morning/evening digests, ops report, work summary, standup |
| Probe | 6 | weather, hurricane, marine, NOAA |
| Atlas | 5 | scrum, sprint review, governance ceremonies |
| Orion | 4 | build, code, deploy, upgrades |
| Legal & Contracts Lead | 3 | mail triage, legal inbox, contracts |
| Head of Research | 3 | OSINT, disclosure watch, intel |
| Controller | 1 | cost digest |

Bindings: `/opt/data/agent_cron_bindings.json`

---

## 6. CADENCE (scrum, per the nura-scrum-review skill)

**Consolidation doctrine: read existing artifacts. Do NOT re-run heavy pipelines. Do NOT grow the
cron roster to satisfy "review everything."**

### Daily Standup — `6ebf34eac6f2`, weekdays 11:00 UTC
Five sections, one screen: yesterday's wins (verified) · shipped (with hashes) · blocked/at-risk
(exact next action each) · system health (numbers) · today's top 3 (deadline-ranked, naming what is
deferred). Writes a check-in + check-out to the log as a required side effect.

### Weekly Sprint Review — `0c78e8591d7b`, Mondays 13:00 UTC
Already existed (dan-martell-operating-system skill). Delivered · metrics · lesson learned · sprint
health · next sprint goals.

### Supporting artifacts (already running — the standup reads these, it does not duplicate them)
`work summary` (daily EOD) · `daily ops report` · `autonomy audit` · `morning digest` ·
`evening digest` · `status board` · `incident audit`.

---

## 7. HEALTH

Runpod-lane-watchdog pattern applies to everything: **state changes are reported, steady states are
silent** (anti-flood doctrine).

- **Cron roster health:** `status board` job, daily 07:00. Also: `cronjob list` → count `last_status: error`.
- **RunPod lane:** `11bf62b0b2ef`, monitor-gated on `runpod-lane-state.py`.
- **The lesson from Paperclip:** a backup status field is not health. **Verify by reading the data,
  not the flag.** The instance that lost the org reported backups healthy the whole time.

---

## 8. WHAT STILL NEEDS THE FOUNDER

1. **Re-triage the 147 recovered tasks.** They came back as `Blocked` with the honest note
   *"needs re-triage"* — that is deliberate. The inherited state was 98% blocked with one agent
   holding 91% of the load. Which are real, which are dead, and who owns each is a founder call.
2. **The 59 unstaffed roles.** Decide which deserve a worker. Do not staff all 59 — that recreates the
   Paperclip failure (many roles, little execution).
3. **`paperclip.nuratech.ai`** — still down (HTTP 000). If the newer company `58ddc931` lives there,
   that host holds data newer than anything local. Diagnose before retiring Paperclip for good.
4. **Paperclip `58ddc931`** appears in **no local backup**. Its 207 issues / 54 agents were never in
   this instance.

---

## 9. FILES

| Path | Purpose |
|---|---|
| `/opt/data/scripts/workforce.py` | Check-in/out CLI — the only writer to the log |
| `/opt/data/workforce_ids.json` | Notion IDs for all surfaces |
| `/opt/data/paperclip_recovery/` | Recovered agents.json, issues.json, companies.json, documents |
| `/opt/data/agent_cron_bindings.json` | Agent → cron job bindings |
| `/opt/data/recover_paperclip.py` | Re-run the recovery from the snapshot |
| `/opt/data/bind_crons.py` | Re-run the cron→agent binding |
| `/opt/data/build_workforce.py` · `migrate_org.py` · `build_dashboard.py` | The build, in order |
