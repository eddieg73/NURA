# Mission Control — Governance Layer (2026-08-24)

Source-of-truth note. The full developer doc lives in the repo: `eddieg73/NURA` → `nura-command-center` (branch `nura-command-center-2026-08-23`) → `docs/GOVERNANCE.md`. Notion mirror: "NURA Mission Control — Governance Layer" (CTO Suite).

## What
Control-plane governance for Mission Control. Adds the missing **evidence** layer to the existing gate-ladder **policy**.
- **Immutable audit trail** — `mission_events` table. Every consequential write emits an event (mission, actor, action, gate, detail, at). Actor is mandatory; anonymous writes throw. Actions include `approval_requested`, `approval_decided`, `gate_pass_denied_no_evidence`, `mission_complete`.
- **Evidence-before-pass** — a gate can't `pass` without ≥1 concrete evidence handle (build id / test run / review / SHA). Denial is itself audited.
- **Governed approvals** — `approvals` table. A `waiting` gate arms an Approval (approver identity + rationale + timestamp). approve → pass, reject → fail. Idempotent, not double-decidable.

## Why (the gaps)
1. No audit trail — couldn't replay who/when/why a gate changed.
2. Approvals were a status flag, not a governed decision — no approver/rationale/record.
3. Gates passed with zero evidence — no proof requirement.

## API
- `GET /api/missions/audit?missionId=…`
- `GET /api/approvals` · `POST /api/approvals` (decide)
- `POST /api/missions/evidence`
- `POST /api/missions/gate` (now enforces evidence + audit)

## Files
`lib/governance.ts` · `lib/db.ts` (DDL + repos) · `lib/schemas.ts` (Zod) · `app/api/**` routes · `app/mission-control/page.tsx` (UI) · `tests/governance.test.ts` (12 tests).

## Reference architectures
Microsoft Agent Governance Toolkit · Aegis (hash-chain + replay) · Preloop control plane · GitHub Enterprise AI Controls (`actor_is_agent`) · DeepSeek Harness ("model-visible means logged").

## Open questions (for review)
1. Hash-chain the audit trail for tamper-evidence? (Aegis precedent)
2. RBAC/identity — per-agent scopes replacing the single shared token?
3. Keep evidence-before-pass strict, or add a named-reviewer override?
4. Error taxonomy + per-run cost telemetry (orchestration-dashboard 5th view)?
5. Sanctioned rollback in the domain layer?

## Repo-update doctrine (2026-08-24)
Every completed increment is documented → committed → pushed → verified (local==remote SHA). GitHub + Notion mirror each build so devs can review/comment.
