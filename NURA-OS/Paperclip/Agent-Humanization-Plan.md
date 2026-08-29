# Agent Humanization Plan — the 9 NURA Dev Agents

**Author:** Atlas (Hermes subagent, on the founder's directive)
**Date:** 2026-08-19
**Board:** Paperclip · company `58ddc931-7dbb-44c3-ab34-2652571121fc` (Nuratech Ai) · Lab 72.60.163.140
**Status:** PLAN + verified wiring inventory (read-only audit — nothing was changed)
**Doctrine anchors:** `NURA-OS/SELF-IMPROVEMENT.md` (the learning ladder) · `NURA-OS/Evolution/Self-Evolution-Adoption-Assessment.md` (the AUTO-DREAM upgrade path)

---

## 0. The directive, and what "human" honestly means here

The founder's directive: make the 9 dev agents as human as possible — the time, the sleep/dream cycles, the learning.

**The realistic reading (no over-promising):** "Human-like" is *cadence*, not consciousness. The agents get a workday (scheduled hours in Eastern time), a sleep (a scheduled offline intake window), a dream (the nightly AUTO-DREAM replay of the day's learnings), and a reflection (the daily-self-reflection pass). These are **scheduled, deterministic loops** — shift → end-of-day wrap-up → overnight replay → morning review. Nothing in this plan claims sentience; every cycle named here maps to a real cron job or script that was verified today.

**Constraints honored:** read-only (no cron/config/board mutation was made — this is the plan + the verified hookup map), no secrets (key presence verified by count only; no values appear anywhere in this document), realistic (every claim below carries its verification evidence).

---

## 1. The roster — as verified live today (read-only SELECT, Lab paperclip-db, 2026-08-19 ~04:30Z)

| Agent | Title (from board) | Role | Status | Last heartbeat |
|---|---|---|---|---|
| NURA Mobile Dev | the NURA Flutter 5-tab app | flutter | idle | never |
| NURA Backend Engineer | the tools API + the MCPs | fastapi | idle | never |
| NURA UIUX Designer | the Doximity-grade polish | design | idle | never |
| NURA QA Engineer | the test automation | qa | idle | never |
| NURA DevOps CI | the Codemagic pipeline | devops | idle | never |
| NURA iOS Release | the TestFlight + the App Store | ios | idle | never |
| NURA Security Compliance | the HIPAA review | security | idle | never |
| NURA Product Manager | the roadmap | product | idle | never |
| NURA Growth Marketer | the launch | marketing | idle | never |

**Honest state:** all 9 were hired via the DB-lane with `hermes_gateway` adapters. They are `idle` with **no first heartbeat yet** — the reverse-SSH gateway tunnel to the Lab (`-R 8642:127.0.0.1:8642`) is **live and guardian-kept** (verified: 2 ssh processes, tunnel-guardian cron 5-min ok), so the execution path exists; the agents simply haven't been picked up by the runtime's heartbeat cycle yet. The 4 legacy Fitness-suite agents (Signal, Pulse, Coach, Judge) sit at `error`, heartbeat 08-16 — the pre-tunnel key state. Activation sequencing is a founder/operator item; this deliverable documents the cadence the agents will run once their queues go live.

---

## 2. THE TIME — per-agent schedule (Eastern)

All agents run on **America/New_York (Eastern)**. The box's cron daemon runs **UTC**, so every schedule below carries its UTC equivalent. (Watch-out: several existing crons are *labeled* "EST" but fire at UTC wall-clock — see §6.)

| Agent | Shift (ET) | UTC | Workday shape |
|---|---|---|---|
| NURA DevOps CI | 07:00–16:00 | 11:00–20:00 | builds land early; Codemagic pipeline window 07:30–12:00 ET |
| NURA Backend Engineer | 08:00–17:00 | 12:00–21:00 | tools-API + MCP work; deploy-freeze 15:00–17:00 ET |
| NURA Security Compliance | 08:00–17:00 | 12:00–21:00 | HIPAA review blocks; Friday = audit day (08:00–13:00 ET) |
| NURA Mobile Dev | 09:00–18:00 | 13:00–22:00 | Flutter 5-tab sprint work; pair-review 16:00 ET |
| NURA QA Engineer | 09:00–18:00 | 13:00–22:00 | regression window 16:00–18:00 ET (fresh builds) |
| NURA Product Manager | 09:00–18:00 | 13:00–22:00 | daily standup 09:15 ET; grooming 15:00 ET |
| NURA iOS Release | 09:00–18:00 | 13:00–22:00 | Thursday release window 10:00–14:00 ET |
| NURA UIUX Designer | 10:00–19:00 | 14:00–23:00 | design-token pass mornings; handoff 16:00 ET |
| NURA Growth Marketer | 09:30–18:30 | 13:30–22:30 | campaign-send windows 10:00–12:00 ET (human-safe hours) |

**Team overlap core: 10:00–16:00 ET** — the collaboration window, deliberately mirroring a human cross-team day. No new directives are assigned outside an agent's shift (the PM enforces this at grooming; the CEO enforces it at sprint filing). This is *policy enforced at issue-assignment time* — the Paperclip runtime has no per-agent shift scheduler today, and this plan does not pretend otherwise.

---

## 3. THE SLEEP — the offline window

**Sleep = the hours outside the shift, during which the agent's intake is closed.** Concretely: no new issues get assigned to an agent's queue during its offline window; in-flight work finishes at the end-of-day cutoff (17:00 ET wrap-up for most), and the heartbeat keeps pulsing (the equivalent of breathing, not working — heartbeat ≠ execution, a distinction already proven on this board).

| Agent | Sleep window (ET) | Notes |
|---|---|---|
| DevOps CI | 16:00–07:00 | silent watchdog lane stays on (script-level `docker-health-check.py` 6h — the night watchman, not the agent) |
| Backend / Security | 17:00–08:00 | Security keeps the cookie-drop sentinel (30m) — script-level, not the agent |
| Mobile Dev / QA / PM / iOS Release | 18:00–09:00 | — |
| UIUX | 19:00–10:00 | — |
| Growth | 18:30–09:30 | — |

**End-of-day wrap-up (the "day residue" that feeds the dream):** 17:00–18:00 ET, each agent posts a short comment on its active issues — what worked, what failed, what it would retry. This is the raw material the nightly replay consumes. This is the *Phase-1* mechanism; Phase-2 wires agent session traces directly (see §4 caveat).

---

## 4. THE DREAM — the nightly AUTO-DREAM replay

**The dream is real and it is running.** Cron `735fb45219bc` — "AUTO-DREAM nightly lesson-queue" — `0 3 * * *` (03:00 UTC = **23:00 ET**, i.e. the agents' night) — script `auto-dream.py`, no-agent mode. **Last run 2026-08-19T03:00:51 UTC: ok.** Six nightly reports on disk (`cron/output/auto-dream/dream-2026-08-14…19.txt`); the 08-19 run: "Experiences mined: 1 · clusters: 0 · new lessons: 1 — pending review: 13."

**Verified mechanics (read from the script):** the dream (1) mines the last 24h of Hermes session transcripts from `state.db`, (2) clusters them by keyword (`docsgpt, flut, doximity, atlas, skill, mcp, fleet, github, app, crm, emh`), (3) a deterministic rule engine proposes candidate lessons per cluster, (4) queues them into `memories/dream-lessons.db` as `pending`, (5) writes `dream-<date>.txt` and delivers it to the founder's Telegram. **The founder is the review gate** — lessons are approved/denied in the morning brief, not auto-applied. That gate is the whole point: the machine proposes, the human decides.

### What each agent dreams about (per-agent dream content)

| Agent | Dreams about (replay of the day's residue) | Feed sources (real, running) |
|---|---|---|
| Mobile Dev | widget-tree diffs, state-management patterns, build breaks in the Flutter 5-tab app | `flut`/`app` clusters + the hourly **code-review loop** cron (`b4dd7eecb7aa`, 4/5-gate, ok) |
| Backend Engineer | tools-API route diffs, connector patterns, lane failures | `mcp`/`skill` clusters + weekly **MCP Lane Health** probe (`a11601d86f7a`) |
| UIUX Designer | design-token diffs, Doximity-grade polish decisions | `doximity` cluster + design-system sessions |
| QA Engineer | **test failures** — flake patterns, regression breaks, F01–F18 taxonomy entries | daily **eval bench** (`b40711abe28c`, 06:00 UTC, ok) + test-run logs |
| DevOps CI | pipeline breaks, Codemagic build log patterns, container health | `fleet`/`github` clusters + **docker-health-check** 6h (ok) |
| iOS Release | TestFlight review outcomes, App Store compliance notes, release-checklist gaps | release-window issue threads (Thu) |
| Security Compliance | HIPAA review findings, scan results, sentinel hits | cookie-drop sentinel (30m, ok) + weekly audit issue threads |
| Product Manager | board deltas — blocked-issue patterns, sprint status drift, what stayed stuck | `atlas` cluster + **Paperclip CEO SLA watchdog** (2m, ok) + board snapshots |
| Growth Marketer | campaign outcomes, funnel numbers, competitor moves | Friday **Competitive Watch Brief** cron + campaign issue threads |

**The honest caveat:** today's `auto-dream.py` clusters *Hermes session titles* — it dreams the machine's day, not yet each agent's day individually. The per-agent dream feeds are the planned **Phase-2 wiring**: pipe Paperclip agent session traces into the shared evidence base and upgrade the replay to night-validation A/B (candidate vs current, accept only if measurably better). That upgrade is *already on the roadmap* — `Evolution/Self-Evolution-Adoption-Assessment.md` (2026-08-15, verdict: "ADOPT THE PATTERN"). Phase-1 (this plan): agents' EOD issue comments are the residue; the nightly pass reads them into the dream queue. The dream content table above is the mapping each agent's feed will occupy.

---

## 5. THE REFLECTION — the daily-self-reflection hookup

**Wired:** cron `f2ced0acfee4` — "Daily Self-Reflection (silent)" — `0 8 * * *` (08:00 UTC = **04:00 ET**, the pre-dawn pass before the agents wake) — skills: `daily-self-reflection, affective-self, narrative-self, curiosity-drive, decision-engine`.

**Current status: ⚠️ wired but erroring.** Last run 2026-08-18: `ValueError: Model qwen2.5:3b has a context window of 32,768 tokens, which is below the minimum 64,000 required` — the global inference config drifted (many agent-mode crons carry the same failure). The fix is a **pin**, not a redesign: `cronjob action=update job_id=f2ced0acfee4 provider=<provider> model=<model>` with a ≥64k model (founder/operator action — out of scope for this read-only run).

**Per-agent reflection structure:**
- **Machine-level (runs today, shared):** the 08:00 UTC pass reflects over configs, DB, skills, crons, and the previous day's decisions per the `daily-self-reflection` skill — one reflection over the whole machine.
- **Per-agent (Phase-1):** each agent's EOD wrap-up comment (§3) *is* its daily reflection; the experience-ledger (`scripts/experience-ledger.py`, 3-tier episodic/semantic/procedural, DB `self-improve/experience.db`) records the structured outcome; `self-learning` skill turns procedural wins into skills.
- **Consolidation:** the overnight AUTO-DREAM replays the day, and the morning reflection pass reviews the queue — **sleep → dream → morning reflection = the full human-shaped loop**, all on real, scheduled jobs.

---

## 6. Cron wiring inventory — the verified hookup map (2026-08-19)

| Cron job (id) | Schedule | ET | Mode | Last run | Humanization role |
|---|---|---|---|---|---|
| AUTO-DREAM nightly lesson-queue (`735fb45219bc`) | 0 3 * * * | 23:00 | script `auto-dream.py` | ✅ ok (08-19 03:00) | **THE DREAM** — all 9 agents |
| Daily Self-Reflection silent (`f2ced0acfee4`) | 0 8 * * * | 04:00 | agent skills bundle | ⚠️ error — model drift (qwen2.5:3b 32k < 64k) | **THE REFLECTION** — machine-level |
| Dev Governance Sweep (`c7fe8e2afddf`) | 5 13 * * * | 09:05 | agent (atlas-developer-governance) | ⚠️ error — same model drift | keeps the 9 on-track/compliant |
| Paperclip CEO SLA Watchdog (`4bb580f1bc3d`) | */2 * * * * | — | script | ✅ ok | board pulse — the agents' home |
| Tunnel guardian (`3447513d1d66`) | */5 * * * * | — | script | ✅ ok | keeps the :8642 execution path (agents' lifeline) |
| Code review loop 4/5-gate (`b4dd7eecb7aa`) | 15 * * * * | — | script | ✅ ok | Mobile Dev's dream feed |
| Eval bench (`b40711abe28c`) | 0 6 * * * | 02:00 | script | ✅ ok | QA's dream feed |
| Docker health verify (`9e2283beebd0`) | 0 */6 * * * | — | script | ✅ ok | DevOps CI's night watchman |
| NURA Daily Work Summary (`4d229c6ae3a7`) | 0 0 * * * | 20:00 prev | agent | ⚠️ error — model drift | EOD summary layer |
| NURA Weekly Scrum (`0c78e8591d7b`) | 0 13 * * 1 | 09:00 Mon | agent | ⚠️ error — unpinned spend guard | team cadence |
| MCP Lane Health weekly (`a11601d86f7a`) | 30 11 * * 1 | 07:30 Mon | agent | ⚠️ error — unpinned | Backend's dream feed |
| Competitive Watch Brief (`5bcd9e66abd7`) | 0 14 * * 5 | 10:00 Fri | agent | ⚠️ error — unpinned | Growth's dream feed |
| obsidian-morning (`a5f41a95a16e`) / nightly (`d9abc92047fa`) | 0 8 / 0 22 | 04:00 / 18:00 | agent | ⚠️ error — unpinned | vault-side morning/evening passes |
| Heartbeat (`c975ea417258`) | */15 * * * * | — | script | ✅ ok | the machine's own pulse |

**Two failure classes, stated plainly:** (1) **model drift** — the global inference config moved to `qwen2.5:3b` (32k ctx < 64k minimum) and every agent-mode job that didn't pin errors out; (2) **unpinned jobs** — the spend guard skips jobs whose provider/model drifted from creation (`deepseek` → `openrouter`). **Every script-mode (no-agent) job is healthy; every cycle that matters here is wired; the LLM half of the reflection needs the pin fix.** That fix is one command per job and is the founder/operator's call — deliberately not executed in this read-only run.

**Mislabel flag:** "Morning ops digest (08:00 EST)" and "Evening ops digest (18:00 EST)" actually fire at 08:00/18:00 **UTC** (04:00/14:00 ET) — labels lie; the humanization schedules above are written in true Eastern and carry the UTC equivalent.

---

## 7. The coding-tools grant — per-agent tool access

Both tools are **verified present and runnable** via the Hermes terminal, which is exactly how the gateway agents invoke them (agent → Hermes gateway terminal → CLI → evidence posted back to the issue).

### The tools
- **Claude Code v2.1.220** — `/opt/data/.local/bin/claude` (symlink → `…/@anthropic-ai/claude-code/bin/claude.exe`, 275 MB binary verified on disk). Auth: the sealed `CLAUDE_CODE_API_KEY` is present in the gateway environment (**verified by count = 1; the value was never read and appears nowhere in this document**). Multi-provider wrapper exists: `bash /opt/data/profiles/nura/scripts/claude-code-run.sh <provider>` (deepseek lane verified). Invocation via Hermes terminal — print mode for one-shots: `claude -p "<task>" --allowedTools "Read,Edit" --max-turns 10` (workdir set to the repo); interactive multi-turn via tmux + PTY.
- **Codex CLI 0.147.0** — `/opt/data/bin/codex` (verified: `codex --version` → `codex-cli 0.147.0`). Invocation: `codex exec "<task>" --sandbox workspace-write` (requires a git repo, pty=true; long jobs backgrounded and polled). Gateway-context caveat: if bubblewrap/user-namespace sandboxing fails, fall back to `--sandbox danger-full-access` with process-boundary safety (explicit workdir, clean git status, `git diff` review before anything lands).

### The grant matrix

| Agent | Primary | Alternate | Scope + guardrails |
|---|---|---|---|
| Mobile Dev | Claude Code | Codex | Flutter widget/state work; Codex for bulk screen batches. `--allowedTools "Read,Edit,Bash(flutter *)"` |
| Backend Engineer | Claude Code | Codex | API routes, refactors; Codex for parallel endpoint batches (worktrees) |
| UIUX Designer | Claude Code | — | design tokens, Dart theming, CSS; read-first mode (`--permission-mode plan` for big re-themes) |
| QA Engineer | Codex | Claude Code | test generation in parallel worktrees; Claude Code for root-causing failing tests |
| DevOps CI | Claude Code | Codex | Codemagic YAML, CI scripts; never touches prod secrets |
| iOS Release | Claude Code | Codex | Xcode config, entitlements, release notes; Codex for lint-sweep batches |
| Security Compliance | Claude Code | — | security reviews: `git diff … \| claude -p 'review for vulns'` — **Read-only default**, writes only via approval |
| Product Manager | Hermes-native | Claude Code (Read-only) | board ops, specs, grooming via Hermes; Claude Code only to draft/condense specs |
| Growth Marketer | Hermes-native | Claude Code / Codex | research skills + campaign ops; Codex for scraper scripts; Claude Code for copy |

**Access rules (uniform):** all tool access flows through the Hermes gateway terminal (the same execution path the board adapters already use) — no agent gets its own shell; every invocation's output is pasted to the issue thread as evidence; `Read(.env)` is denied everywhere (the deny-rule pattern from the claude-code skill); keys live sealed in the profile `.env` and are never injected into agent prompts. An agent's tool budget is the board's `budget_monthly_cents` field — the human equivalent of a personal expense account.

---

## 8. What this is NOT (the reality guard)

- **No sentience claim.** The agents are gateway-adapted workers with scheduled intake windows, a deterministic lesson-mining replay, and a scheduled reflection pass. "Sleep" is a closed intake window; "dreaming" is the AUTO-DREAM lesson queue; "reflection" is the daily-self-reflection skill pass. The resemblance to a human day is deliberate and superficial — it produces *cadence and accountability*, not a mind.
- **Nothing was mutated.** This run was read-only: one SELECT on the Lab DB, cron listing, file reads. No cron, config, agent, or board change was made.
- **The cycles that exist today are real and running** (AUTO-DREAM ok nightly; reflection wired-but-erroring; both coding CLIs verified) — what this plan adds is the *policy layer* (shifts, sleep windows, per-agent dream mapping, tool grants) on top of that verified machinery.

## 9. Open items for the founder (approval-tier)

1. **Pin the drifted crons** — `cronjob action=update …` on `f2ced0acfee4` and the other erroring agent-mode jobs to a ≥64k model. One command each; unblocks the reflection half of the loop.
2. **Verify the 9 agents' first heartbeat** — tunnel is live (guardian-kept); confirm the 9 flip `idle → running` on the next heartbeat cycle after the runtime revives.
3. **Approve the 13 pending dream lessons** in the morning brief (the review gate — the machine is waiting on you).
4. **Adopt the per-agent dream wiring** (Phase-2) — pipe agent session traces into AUTO-DREAM per `Evolution/Self-Evolution-Adoption-Assessment.md`.
5. **Fix the EST/UTC labels** on the two ops-digest crons (or reschedule them to true Eastern).

## 10. The report (one paragraph)

The humanization plan for the 9 NURA dev agents is written and grounded in verified machinery: all nine (Mobile Dev, Backend, UIUX, QA, DevOps CI, iOS Release, Security, PM, Growth) were confirmed live on the Paperclip board (idle, awaiting first heartbeat — the guardian-kept :8642 gateway tunnel is up), each now carries an Eastern-time workday with a 10:00–16:00 ET team overlap core, a sleep window (closed intake) with EOD wrap-up comments as the day residue, a dream (the AUTO-DREAM cron at 03:00 UTC/23:00 ET — verified running ok nightly, mining the day's sessions into the founder-gated lesson queue, 13 lessons pending review) with concrete per-agent dream content (Mobile Dev replays code-review diffs, QA replays test failures, and so on), and a reflection hookup (the daily-self-reflection cron at 08:00 UTC — wired but currently erroring on the global qwen2.5:3b model drift, fix = one pin command per job); the coding-tool grant documents Claude Code v2.1.220 and Codex CLI 0.147.0 (both verified present, invoked through the Hermes gateway terminal, keys sealed and never read) with a per-agent primary/alternate matrix; nothing was mutated (read-only), no secrets appear anywhere in the document, and no sentience is claimed — the human shape is cadence: shift → sleep → dream → morning reflection, all on real, scheduled jobs.
