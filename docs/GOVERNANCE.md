# NURA Mission Control — Governance Layer

> **Status:** implemented & verified (branch `nura-command-center-2026-08-23`) · **owner:** Hermes (CTO) · **reviewers:** open to all devs — comment on this PR or open an issue.

This document is the **design + rationale** for the governance layer added to Mission Control. It is written so an engineer landing from any background can understand *what* was built, *why*, *how it's enforced*, and *how to contribute*. If you're reviewing, the place to comment is this PR's thread or a GitHub Issue — every consequential question below is an open one.

---

## 1. Problem statement

Mission Control's control plane (`lib/control-plane.ts`) already had the **policy** — a change-policy gate ladder (`BUILD → UNIT → INTEGRATION → SECURITY → CLINICAL → QA → MERGE`) that a mission must walk. What it did **not** have was **evidence**. Three gaps, each a real risk if you're routing work to devops/clinical/security agents:

1. **No audit trail.** Every gate pass/fail and mission status change mutated state with **zero record of who did it, when, under what policy, or why.** A control plane that can't replay "why did mission X reach MERGE" is not governance — it's a demo.
2. **Approvals weren't governed.** `awaiting_approval` was a *status flag* with no approver identity, no rationale, no decision record, no idempotency. You could not prove *who approved* a merge, or that an approved mission actually re-entered execution.
3. **Gates passed with no proof.** You could mark `security`/`merge` = `pass` with an **empty evidence list**. "No evidence = no pass" was not a rule.

This is exactly the class of gap the 2026 control-plane literature flags: Microsoft's Agent Governance Toolkit, Aegis, Preloop, and GitHub's own Enterprise AI Controls all converge on the same primitives — **policy enforcement + tamper-evident audit log + governed approvals + identity**. GitHub's production audit log even records `actor_is_agent` and `agent_session.task` events, confirming the direction. GitLab lives here too.

---

## 2. What was built

### 2.1 The audit trail (immutable)

New table `mission_events` (plus index on `mission_id, at DESC`). Every consequential write on a mission emits one `MissionEvent`:

```
{ id, missionId, actor, action, gate?, detail, at }
```

Actions: `mission_created` · `command_queued` · `command_dispatched` · `status_changed` · `gate_change` · `gate_waiting` · `approval_requested` · `approval_decided` · `evidence_attached` · `gate_pass_denied_no_evidence` · `mission_complete`.

**Invariant:** an `actor` is mandatory. `lib/governance.ts#logEvent` **throws on an anonymous write** — an unowned write is not auditable. (This follows DeepSeek Harness's "model-visible means logged": anything that changed state must be reconstructable.)

### 2.2 Evidence-before-pass

A gate may only be set to `pass` when the mission carries at least one non-empty evidence handle (build id / test run / review / commit SHA). This is enforced **at the domain layer** (`lib/governance.ts#advanceGateGoverned`), not merely in the route, and **the denial is itself audited** as `gate_pass_denied_no_evidence`.

### 2.3 Governed approvals

When a gate goes `waiting`, it arms an `Approval` (`approvals` table):

```
{ id, missionId, gate, requestedBy, requestedAt, status: open|approved|rejected, decidedBy, rationale, decidedAt }
```

- **Idempotent** — a gate cannot double-queue an open approval (`requestApproval` returns the existing one).
- **Cannot be decided twice** — `decideApproval` rejects a second decision.
- `approved` → gate `pass` (subject to evidence rule) → mission resumes; `rejected` → gate `fail` → mission `blocked`.
- Every decision records the **approver identity + rationale + timestamp** and is audited.

### 2.4 API surface

| Method | Route | Purpose |
|---|---|---|
| GET | `/api/missions/audit?missionId=…` | replayable per-mission audit trail (or recent cross-mission ledger) |
| GET | `/api/approvals` | open approvals (the human-in-the-loop inbox) |
| POST | `/api/approvals` | decide an approval `{approvalId, decision, actor, rationale}` |
| POST | `/api/missions/evidence` | bind a concrete evidence handle to a mission |
| POST | `/api/missions/gate` | now enforces evidence + audit on the live path |

### 2.5 UI

Mission Control (`app/mission-control/page.tsx`) gained two panels: **Approval inbox** (open decisions needing a human) and a live **Audit trail**.

---

## 3. Architecture (files)

| File | Role |
|---|---|
| `lib/schemas.ts` | Zod schemas: `MissionEvent`, `Approval`, action/status enums |
| `lib/db.ts` | DDL for `mission_events`/`approvals`, repos (`events`, `approvals`), `controlPlaneSetGate` bridge |
| `lib/governance.ts` | The domain rules: `logEvent`, `requireEvidenceToPass`, `attachEvidence`, `advanceGateGoverned`, `requestApproval`, `decideApproval`, `pendingApprovals`, `missionAudit` |
| `app/api/missions/audit/route.ts` | read audit trail |
| `app/api/approvals/route.ts` | inbox + decisions |
| `app/api/missions/evidence/route.ts` | bind evidence |
| `app/api/missions/gate/route.ts` | governed gate advance |
| `app/mission-control/page.tsx` | UI panels |
| `tests/governance.test.ts` | 12 tests covering audit, evidence, approvals, idempotency |

**Layering rule:** `lib/control-plane.ts` owns *policy* (ladder, lifecycle). `lib/governance.ts` owns *evidence* (audit + approvals). The route calls governance, which calls the db repos. Pages/routes never query SQLite directly.

---

## 4. How to run and verify

```bash
npm install
npm run typecheck   # must be green
npm test            # 981 tests; 12 are tests/governance.test.ts
npm run build && npm start   # http://localhost:4100
```

To exercise governance by hand: create a mission from Mission Control, POST evidence (`/api/missions/evidence`), advance gates (`/api/missions/gate`). A `pass` with no evidence returns **409** with `denial`, and the denial lands in the audit trail.

---

## 5. Reference architectures consulted

These shaped the design; each is worth reading before you comment:

- **Microsoft Agent Governance Toolkit** — policy engine, audit log, identity, sandboxing. The "which agent did this / can you prove it" framing.
- **[Aegis](https://github.com/agentlifylabs/Aegis)** — *hash-chained* event log + deterministic replay. **This is our next improvement** (tamper-evident chain over a plain append-only log).
- **Preloop control plane** — the 5 primitives: tool governance, model gateway, human approvals, runtime observability, audit.
- **GitHub Enterprise AI Controls / Agent Control Plane** — `actor_is_agent` + `agent_session.task` auditing, centralized MCP registry.
- **DeepSeek Harness** — "model-visible means logged" (append-only session log as source of truth).

---

## 6. Open questions / intended next steps (please weigh in)

These are deliberately left as **discussion**, not claimed as done — comment on the PR or open an issue:

1. **Tamper-evidence.** Should `mission_events` become a hash chain (each event carries `prev_hash`)? Field consensus (Aegis) says yes for compliance-grade evidence. Cost: schema + re-verify on read.
2. **RBAC / identity.** Currently one shared `FOUNDER_OS_ACCESS_TOKEN` (no per-agent/role scoping). For a control plane routing to devops/clinical/security agents, do we want per-agent permissions, and which role may approve `merge`/`security`/`clinical`?
3. **Evidence-before-pass strictness.** Right now it's **hard-enforced** even on the live route. Do we want a trusted-approver override (e.g. a named reviewer can pass with an explicit `rationale` but no artifact), or keep it strict?
4. **Error taxonomy + cost telemetry.** Should we add the orchestration-dashboard's fifth view (error-code classification + per-run token/cost)? It feeds the same audit table.
5. **Rollback.** Is there a sanctioned un-block path you want in the domain (vs. only in the UI)?

---

## 7. Contributing

- Branch from `main`, feature branch, small commits, push to `eddieg73/NURA`, open a PR.
- TDD: failing test first, then implement; `npm test` + `npm run typecheck` green before claiming done.
- **Evidence-first:** every behavior change should ship with a test that proves it, and (for control-plane writes) an audit event. No silent state mutations.
- Never commit secrets; `.env.local` is gitignored. Review the repo's `AGENTS.md`.
- To comment on this work: open an Issue or comment on the PR — the questions in §6 are where input most changes the direction.
