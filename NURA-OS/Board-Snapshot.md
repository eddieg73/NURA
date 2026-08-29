# NURA Board Snapshot

**Generated:** 2026-08-29 (cron)
**Source:** SSH → Lab (72.60.163.140 / srv1030183) → paperclip-db (DB fallback — API key empty; local :3100 onboard is empty)
**Company:** 58ddc931-7dbb-44c3-ab34-2652571121fc (Nuratech Ai)

> Note: the cron param company `999ff375` + port `:3101` are stale/archived (phantom instance era). The live board is company `58ddc931`. Snapshot taken via the DB lane (SSH → Lab → `docker exec paperclip-db psql`).

---

## Summary

| Metric | Value |
|--------|-------|
| Total issues | **207** |
| Blocked | 188 (21 critical · 133 high · 34 medium) |
| Todo | 18 (15 high · 3 medium) |
| Done | 1 (1 low) |
| Agents on roster | 54 (39 idle · 9 error · 6 working · 0 running) |
| Issues unassigned | 30 |

## Issues (top 50 by updated_at desc)

| # | Identifier | Title | Status | Priority | Assignee |
|---|-----------|-------|--------|----------|----------|
| 1 | NUR-40 | Recover stalled issue DIRECTIVE — CarePilot RPA review: the text bots | blocked | high | CEO |
| 2 | - | DIRECTIVE — CarePilot RPA review: the text bots | blocked | high | CEO |
| 3 | NUR-39 | Recover stalled issue CEO DIRECTIVE — build the Population Health agent group to run carepilot.nuratech.ai | blocked | high | CEO |
| 4 | NUR-38 | Recover stalled issue SWARM — Doximity clone: the backend lane verification | blocked | high | CEO |
| 5 | NUR-37 | Recover stalled issue SWARM — Doximity clone: the 5-tab QA pass + the Codemagic iOS prep | blocked | high | CEO |
| 6 | NUR-36 | Recover stalled issue SWARM — Doximity clone: the security + compliance review | blocked | high | CEO |
| 7 | - | SWARM — Doximity clone: the 5-tab QA pass + the Codemagic iOS prep | blocked | high | NURA Mobile Dev |
| 8 | - | SWARM — Doximity clone: the backend lane verification | blocked | high | NURA Backend Engineer |
| 9 | - | SWARM — Doximity clone: the security + compliance review | blocked | high | NURA Security Compliance |
| 10 | - | CEO DIRECTIVE — build the Population Health agent group to run carepilot.nuratech.ai | todo | high | CEO |
| 11 | NUR-35 | Recover stalled issue CEO DIRECTIVE — stand up the NURA synthetic law firm (the LEXA division) | blocked | high | CEO |
| 12 | - | CEO DIRECTIVE — stand up the NURA synthetic law firm (the LEXA division) | blocked | high | CEO |
| 13 | - | HIRE: Integration Engineer — continue the Mirth/NextGen Connect (OIE) interface on Docker | blocked | high | CEO |
| 14 | - | Q9 — Atlas: which of the 4 products is the revenue driver and why? | blocked | high | CEO |
| 15 | - | Q20 — Atlas: team health check — who needs training, who is blocked? | blocked | high | CEO |
| 16 | - | Q19 — Atlas: what blockers do you need cleared by the founder this week? | blocked | high | CEO |
| 17 | - | Q10 — Atlas: the 30-day delivery plan | blocked | high | CEO |
| 18 | - | CEO DIRECTIVE — product 4: Personal AI Medical Consultant card (CLINICAL — provider-gated) | blocked | high | CEO |
| 19 | - | CEO DIRECTIVE — product 3: CRAFT 7-Day Client Sprint (solopreneur acquisition system) | blocked | high | CEO |
| 20 | - | CEO DIRECTIVE — build the 8-Role AI Sales Team product AND train the team | blocked | high | CEO |
| 21 | - | CEO DIRECTIVE — product 2: the 8-Role AI Sales Team (100M sales team system) | blocked | high | CEO |
| 22 | - | CEO DIRECTIVE — build the NURA Fitness AI Suite (12-persona program generator) + run the team | blocked | high | CEO |
| 23 | - | Q12 — Coach: the intake fields each fitness persona requires | blocked | medium | Coach |
| 24 | - | Q3 — Coach: which 3 fitness personas get the deepest prompt work first? | blocked | medium | Coach |
| 25 | - | Q4 — Coach: how do we enforce the no-voice-copying guardrail technically? | blocked | medium | Coach |
| 26 | - | Q7 — Signal: top 3 acquisition channels for the CRAFT 7-Day product | blocked | medium | Signal |
| 27 | - | Q8 — Signal: pricing hypothesis for the 8-Role Sales Team product | blocked | medium | Signal |
| 28 | - | Q6 — Judge: required disclaimers for the Medical Consultant card (clinical product) | blocked | medium | Judge |
| 29 | - | Q5 — Judge: what QA gate does the 8-Role Sales Team product need before launch? | blocked | medium | Judge |
| 30 | - | Q13 — Judge: the rollback plan if a product misbehaves in production | blocked | medium | Judge |
| 31 | - | Q11 — Pulse: how does the Medical Consultant card stay provider-gated (no patient-facing claims)? | blocked | medium | Pulse |
| 32 | - | Q15 — Pulse: which product integrates with GHL first and how? | blocked | medium | Pulse |
| 33 | - | Q1 — Pulse: MVP scope for the Fitness AI Suite (how many of the 12 personas ship v1)? | blocked | medium | Pulse |
| 34 | - | Q2 — Pulse: launch sequencing across the 4 products | blocked | medium | Pulse |
| 35 | - | Q17 — Judge: the 5 must-pass tests before the Sales Team product ships | blocked | medium | Judge |
| 36 | - | Q16 — Coach: the system prompt that prevents the sales team from giving medical or financial advice | blocked | medium | Coach |
| 37 | - | Q14 — Signal: the week-1 launch content calendar | blocked | medium | Signal |
| 38 | - | Q18 — Signal: the referral loop for the Fitness AI Suite | blocked | medium | Signal |
| 39 | - | TRAINING — Pulse: own the 2-product roadmap (Fitness AI Suite + 8-Role Sales Team) | blocked | medium | Pulse |
| 40 | - | TRAINING — Judge: define the QA gate for both products | blocked | medium | Judge |
| 41 | - | TRAINING — Signal: launch plan for the 2-product suite | blocked | medium | Signal |
| 42 | - | TRAINING — Coach: master the 8 frameworks + 6-step playbook | blocked | medium | Coach |
| 43 | - | PAPERCLIP: Phase-3/5 — the Flutter-UI (the screens + the dio-client + the dialer!) | todo | high | <unassigned> |
| 44 | - | ATLAS: Phase-2 — the DocsGPT plugins + the API-keys (the DeepSeek-harness-connectors!) | todo | high | <unassigned> |
| 45 | - | CEO: MARKETING-TEAM-SETUP + the 20-hook distribution campaign | todo | high | <unassigned> |
| 46 | - | REVIEW: agency-agents (msitarzewski) — the 311-agent roster | todo | medium | <unassigned> |
| 47 | - | COGNITIVE-1: WorldState + memory contract + goal ledger | todo | high | <unassigned> |
| 48 | - | MCP-1: NuraTech Supervisory MCP (the parent gateway) | todo | high | <unassigned> |
| 49 | - | IMPLEMENT: Agent Graph Orchestration (founder image 08-06) | todo | high | <unassigned> |
| 50 | - | STUDY: gstack (Garry Tan YC virtual tech company) | todo | high | <unassigned> |

---

_Snapshot reflects the live board at query time. Identifier column may be `-` for issues without a NUR-number; the board rotates/reuses identifiers, so match by **title** not identifier. Several "Recover stalled issue" duplicates are present (auto-retry artifacts). No tokens or secrets included._
