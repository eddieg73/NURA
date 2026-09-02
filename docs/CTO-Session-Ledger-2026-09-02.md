# CTO Session Ledger — 2026-09-02

**Date:** 2026-09-02 (02:15 UTC) · **Owner:** Eddie (founder) · **Operator:** Hermes (CTO)
**Scope:** Last 48h work review (08-31 → 09-02) across memory, Obsidian, Notion, GitHub, fleet.
**Mirrored to Notion:** page `CTO Session Ledger — 2026-09-02` under the integration-accessible
OSINT Board + Daily Briefs parent (`6524f4aa-...`). Note: the Master Board page is **not shared with
the integration token** — it returns 404 `object_not_found`. To land future ledgers directly on the
Master Board, that page must be shared with integration id `3afa9b14-e498-8122-8fc5-002767d7f4`.

> This ledger is the consolidated status. It follows the existing `docs/CTO-Session-Ledger-2026-08-28.md`
> format so the series is continuous, not duplicated. **Connects to canonical** doc locations — never duplicates.

---

## Overall Status: STABLE (2 P3 items; no P0/P1/P2)

**Bottom line:** The fleet is healthy — **88/88 containers Up** across the 3-node fleet
(clinic 72.61.71.211 / lab 72.60.163.140 / edge 195.35.32.113), endpoints **8/9 open**.
No SEV-1/SEV-2. Two P3 findings in-flight (Mirth reachability review + the recurring
mem0 memory-engine lock), plus a standing self-signed-cert item. Everything else green.

---

## What was done in the last 48h (verified)

### 1. nura_medical monorepo — committed + pushed (GitHub current)
- HEAD `e18bd7f` on `master` = `origin/master` (no unpushed commits; confirmed via fetch).
  Commit: *"chore(nura-monorepo): pubspec.lock refresh, imaging-stack www, meshtastic db files, weather monitor update."*
- Recent feature history topping the branch:
  - `401c4db` **feat(nura-mobile-ios): TestFlight readiness** — Info.plist usage descriptions, ATS + encryption exemption, iOS16 deployment target, Podfile, Runner.entitlements, PrivacyInfo.xcprivacy.
  - `4584d99` **docs(solis): MRA/RAF report** — 72 recapture candidates, 13 at-risk, 2 fully-V24, +0.212 gap.
  - `5f60676` **feat(agent-os): NURA Agent-OS build plan** + P0 sovereign harness proof (CoreCoder via dock Ollama).
  - `406552d` **feat(raf): V24-vs-V28 reconciliation** + recapture queue (de-identified).
- Secondary branch `nura-platform-builds-2026-08-23` (`5eb13fd`) = Field-Ops standing module (mission charter, claim_chart, executor_control, resilient_uplink).
- **Push auth verified live:** `Hi eddieg73!` via dedicated `id_github` key + `GIT_SSH_COMMAND` (per doctrine).

### 2. Fleet audit (nura-inventory-health, 08-31 02:01 UTC) — DEGRADED only on 1 probe
- **clinic:** 40/40 up · mem 39% · disk 66% · **lab:** 40/40 up · 35% · 65% · **edge:** 8/8 up · 57% · 29%
- **Endpoints 8/9 open; sole `UNHEALTHY: mirth`.**
- **Mirth root-cause (SEV-3→SEV-4, in review):** Mirth/OIE engine Up 41h; published ports `8445→8443, 6669, 6663, 8086`; host-local `:8445` = OPEN; **external egress CLOSED** — while qdrant (`32776`) + openemr (`32777`) on the SAME host are OPEN. Hypothesis: the mirth bridge (`172.30.0.0`) FORWARD path is dropped; the `192.168.144.0` bridge passes. **No firewall change applied in automation** (security-change = approval-gated; Mirth non-redeployable per SOP). Impact pending: if SOLIS_ENSURE_INBOUND + 2 bridges need external ingress → SEV-2; if internal-only → SEV-4.

### 3. Incident report (incident-commander, 08-31 03:11 UTC) — P3 config drift, RESOLVED
- **Root cause:** Mirth MCP lane pointed at stale port `:8444`; actual Admin API is `:8445`.
  → `MIRTH_BASE_URL=https://72.61.71.211:8445` (env correction surfaced; confirmed the container was redeployed 08-29, port moved 8444→8445).
- **Mirth engine NOT down** — `restart=0`, "server successfully started," SOLIS inbound + NURA bridge UP. The `VT not detected` MLLP log noise is normal probe traffic, not engine failure.
- **Learnings banked:** don't page on <5 min load spikes (MCP boot storm); swap-full with 0 swap-in is benign; Mirth "VT not detected" = noise.

### 4. Obsidian vault (authoritative daily record) — consolidated nightly
- `Daily/2026-08-31.md` — memory hygiene done (MEMORY.md 97→98%), skill `nura-raf-reconciliation` anchored to the CY2026 V28 full phase-in (100% 2024 CMS-HCC, 5.90% coding adj → CarePilot RAF must be V28-normalized).
- Standings documented (unchanged, not re-alerted): api.nuratech.ai Traefik **default self-signed cert** · lab-intake `provider_labs→Med42→OpenEMR` drop since 08-26 (gws OAuth + DOCUMO_KEY unset) · Mirth admin-plane SEV-3 · off-site R2/B2 backup not running (missing tokens).

### 5. Board snapshot (Paperclip company 58ddc931, 54 agents) — 207 issues
- **206 open / 1 done** · blocked 188 / todo 18 · critical 21 / high 148.
- Agent roster: NURA DevOps CI, Growth Marketer, Product Manager, QA, UIUX, iOS Release = **working**; CEO, Coach, Judge, Pulse, Signal, NURA Backend/Mobile/Security = **error** status (needs attention).

---

## What is BLOCKED / needs your call (P2/P3)

| # | Item | Status | Needs |
|---|------|--------|-------|
| 1 | **mem0 memory-engine lock** (Pattern-14) | P3, recurring | Gateway restart clears it. Stale `.lock` backed up + removed this session (partially mitigated). This is the recurring "memory issues" — see Fix log. |
| 2 | **Mirth external-reachability** | P3→SEV-2? | Confirm whether SOLIS_ENSURE_INBOUND + 2 bridges need external ingress. If yes → review clinic host FORWARD/NAT for `172.30.0.0` + raise firewall change for approval. **No auto-change.** |
| 3 | **api.nuratech.ai self-signed cert** | P3, standing | Replace TRAEFIK DEFAULT cert with Let's Encrypt (not expiring until 08-2027, but untrusted). |
| 4 | **Off-site R2/B2 backup** | P3, standing | Missing tokens — durable deliverable. Local daily chain healthy Aug 24→30. |
| 5 | **Lab-intake lab pipeline drop** | P3, known drop | gws OAuth + DOCUMO_KEY unset; cron SILENT until verified healed. |

---

## Metrics (48h)

| Metric | Value |
|---|---|
| Fleet containers | 88/88 Up |
| Endpoints | 8/9 open (mirth the one) |
| GitHub push | Verified (eddieg73/NURA) |
| Notion mirror | Verified (token set, parent 3cca9b14) |
| Incidents P0/P1/P2 | 0 |
| Incidents P3 | 2 active (mem0 lock, Mirth reachability) + 3 standing |
| MEMORY.md | ~98% |

---

## Next actions (2 highest priority)
1. **Crack the mem0 / episodic-memory reliability** — this is the root of "I keep correcting you / you don't remember." Plan: point mem0 at the **Qdrant server** (`http://127.0.0.1:6333`, already running) instead of the embedded `/opt/data/profiles/nura/home/.hermes/mem0_qdrant` local path, so it never hits the single-instance file lock again. (Founder-directed fix.)
2. **Mirth reachability decision** — confirm ingress need; if external, approve the firewall/FORWARD change (I will not touch it unattended).

---

*Evidence verified this session: git fetch/log + push auth (`Hi eddieg73!`); nura-inventory-health output `clinic:40/40up | lab:40/40up | edge:8/8up | endpoints: 8/9 open | UNHEALTHY: mirth`; incident-report-2026-08-31; Obsidian Daily + daily-operations report; board snapshot 207 issues; mem0 lock lsof (no holder) + `.lock` cleared.*
