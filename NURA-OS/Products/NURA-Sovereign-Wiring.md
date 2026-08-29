# NURA SOVEREIGN WIRING (2026-08-19 — the watsonx review → the open-stack sovereign equivalent)

**The founder's directive: the review the IBM watsonx's the whole system — the wire the NURA's the BETTER. This doc = the full gap-analysis (the IBM's six pieces vs the ours) + the wiring plan (audit consolidation · policy layer · case-context engine) + the create-ready schemas. Constraints honored: NO production writes (docs + schemas only), open-stack only (Postgres · Qdrant · Paperclip · hermes_gateway · n8n — zero IBM components).**

**Companions:** `[[NURA-Policy-Matrix]]` (the RBAC matrix v1.0 — canonical) · `sql/sovereign-audit-log.sql` (the CREATE-READY DDL — audit store + policy registry + case-context tables).

---

## 0. THE GAP-ANALYSIS — the six pieces vs the ours

| # | IBM watsonx piece | What it delivers | OUR open-stack equivalent | Status | Gap |
|---|---|---|---|---|---|
| 1 | **Orchestrate** | Agent control plane — task routing, agent lifecycle, human gates | **Paperclip board + hermes_gateway (:8642)** — the 6 agents, issues = directives, CEO approval lane | ✅ LIVE | Small — policy decisions are NOT enforced at dispatch (no role check before an agent runs) |
| 2 | **Sovereign Core** | Provable compliance — *where PHI lives, who touched it, which model produced which output, which policy was in force* | Scattered: Paperclip issue log · cron output JSON · circuit-breaker.json · per-lane logs | ⚠️ SCATTERED | **BIG — the audit consolidation is the #1 gap. The "who touched what" question is not one query today.** |
| 3 | **Docling** | Documents → AI-ready | **ocr-router + lab-intake** (faxes/referrals/prior-auths) | ✅ LIVE | None structural — but doc events must FEED the case-context engine (they don't today) |
| 4 | **Concert / Confluent** | Ops + real-time context | **n8n (53 workflows) + gateway + 24+ MCP lanes** | ✅ LIVE | Real-time event feed not unified into one stream |
| 5 | **Bob** | Legacy modernization | **Claude Code** | ✅ LIVE | None structural |
| 6 | **ViClinic AHOS** | Shared case-context engine — every agent works from the SAME evolving case state | Per-task context only — each agent gets its own prompt-scoped snapshot | ⚠️ IMPLICIT ONLY | **BIG — the case-context engine must become explicit** |

**The third gap (carried from the MCP-Architecture v1, 2026-08-06):** the Supervisory MCP defined identity · RBAC · HITL · audit — but the RBAC matrix was never formalized as a table. The v1 doc's tool-class gates (READ-free / WRITE=HITL / WRITE=auto) exist as prose. This doc codifies them.

**Why ours ends up BETTER (the sovereign argument):** the same provable-compliance shape as the watsonx Sovereign Core, but (a) every component is open-stack and self-hosted — no per-seat tax, no PHI egress; (b) the audit event carries the POLICY VERSION in every row, so "which policy was in force" is answerable per-event, not per-deployment; (c) the enforcement chokepoints are our own gateway and supervisory MCP — we can add fields without a vendor roadmap.

---

## A. THE AUDIT CONSOLIDATION — the one audit-log store

### A.1 The design
**One table, one schema, one write pattern: `sovereign.audit_event` (Postgres).** Every agent action — coding agent, MSO coder, scribe, MIA, intake, ops — logs one row carrying the founder's five:

| Field group | Columns | Answers |
|---|---|---|
| **actor** | `actor_type` · `actor_id` · `actor_role` | who did it (agent UUID from the Paperclip `agents` table / provider / lane) |
| **resource** | `resource_type` · `resource_id` | what it touched (patient · encounter · document · issue · config) |
| **model** | `model_id` · `model_version` · `prompt_ref` | which model produced which output |
| **policy** | `policy_version` · `decision` · `gate` | which policy was in force + the allow/deny/HITL decision + which checkpoint decided |
| **action+result** | `action` · `result` · `phi_scope` · `payload_sha256` · `session_id` · `tenant_id` | what happened, did it pass, PHI exposure, payload hash (circuit-breaker doctrine), tenant scope |

**Append-only mechanics (in the SQL):**
- `seq` = `GENERATED ALWAYS AS IDENTITY` — monotonic order, gap-free enough for a hash-chain (`payload_sha256` carries the circuit-breaker hash; a `prev_sha256` chain can be added app-side without schema change).
- A trigger (`block_audit_mutation`) REJECTS `UPDATE`/`DELETE` — the table physically cannot be rewritten.
- The app role gets `INSERT` + `SELECT` only (grant pattern commented in the SQL).
- Hash + append-only + trigger = tamper-evident by construction, not by convention.

**Queryable (the views in the SQL):**
- `v_who_touched_patient` — **the "who touched what" question becomes one indexed query.**
- `v_model_outputs_by_policy` — model × policy-version × action histogram (the compliance report shape).
- `v_agent_actions_by_day` pattern — the daily ops probe.

### A.2 The hookup points (exactly where the writes happen)
1. **hermes_gateway :8642 = the single chokepoint.** Every Paperclip agent executes through it (verified 2026-08-16: the reverse-tunnel makes the Lab's loopback 8642 live). Add one audit-emission middleware: a row per dispatched task + a row per tool call. The actor UUID comes from the Paperclip `agents` table (the DB-lane already resolves it).
2. **The Supervisory MCP wrapper** — per the v1 doc it is *the* identity/RBAC/audit layer; it sits in front of FHIR/OpenEMR-MCP and n8n-MCP. Every tool call logs `action` · `tool_name` → `mcp_lane` · `gate` decision. This is the point where `decision='deny'` rows get written — deny events are audit events too.
3. **The MSO coder** — chart-reads and code-candidate outputs log `resource_type='patient'`, `action='coding.candidates'`, `model_id` = the routed model, `policy_version` = the RAF/HCC v28 policy version.
4. **The OpenEMR API layer** — the MEDBASE rule (never-SQL-direct, audit-trail-everywhere) makes the API layer the natural second emission point for every clinical write.
5. **The Paperclip issue lifecycle** — issue create/assign/status-change = control-plane events (`resource_type='issue'`). The board's own table is NOT the audit store — it's the work queue; the audit store is the record.
6. **The ocr-router / lab-intake** — document-ingest events feed BOTH the audit store and the case-context engine (one write, two readers).

### A.3 What we are NOT doing (the constraint line)
No writes to production Postgres, no gateway changes, no agent reconfig — this phase delivers the schema + the hookup map only. The DDL is idempotent (`CREATE ... IF NOT EXISTS`) and lands in a NEW `sovereign` schema, so running it later touches nothing existing.

---

## B. THE POLICY LAYER — the RBAC matrix formalized

**The canonical matrix: `[[NURA-Policy-Matrix]]`** (v1.0, effective 2026-08-19, registered in `sovereign.policy_version`). Shape:

- **8 roles** — founder · clinician · coder_agent · scribe_agent · mia_agent · intake_agent · ops_agent · auditor.
- **10 capabilities** — chart.read · chart.write · chart.sign · orders.create · rx.prepare · claim.submit · comms.send_phi · data.export_phi · admin.config · audit.read.
- **4 gates** — ✅ ALLOW (auto, logged) · 🟡 HITL (human-in-the-loop — provider sign) · 🔴 DENY · ⚠️ STEP-UP (HMAC step-up + human, per the MCP v1 gates).
- **The never-autonomous list** (carried from the v1 doc, now policy rows): final diagnosis/treatment · controlled-substance Rx (EPCS) · high-risk med changes · abnormal-critical disposition · invasive orders. **The step-up list:** refunds (NMI gate) · large financial · irreversible chart deletes · destructive admin.

**The enforcement checkpoints (where each decision is made and logged):**

| # | Checkpoint | Enforces | Logs |
|---|---|---|---|
| 1 | **Gateway dispatch middleware** (:8642) | role → capability lookup BEFORE an agent task runs | one `audit_event` per dispatch (`gate='gateway'`) |
| 2 | **Supervisory MCP** | per-tool-call gate (READ-free / WRITE=HITL / auto) | one `audit_event` per tool call incl. denies (`gate='supervisory-mcp'`) |
| 3 | **OpenEMR API layer** | clinical write gate — `chart.write` requires the HITL token/provider id | `gate='openemr'` |
| 4 | **NMI payments gate** | refunds = step-up | `gate='nmi'` |
| 5 | **EPCS gate (Weno)** | controlled-substance Rx | `gate='epcs'` |

**Policy versioning:** every enforcement row stamps `policy_version` (FK to `sovereign.policy_version`), and every audit event carries the same version. Changing the matrix = INSERT a new version row (`v1.1` supersedes `v1.0`) — **"which policy was in force at 14:03 Tuesday" is answered by the audit table alone, no code archaeology.** This is the piece the watsonx Sovereign Core charges for; ours is one FK column.

**Role resolution:** Paperclip `agents.role`/`title` → RBAC role mapping at dispatch (e.g. the MSO coder agent UUID → `coder_agent`). Unknown actor = fail-closed (`decision='deny'`, logged).

---

## C. THE CASE-CONTEXT ENGINE — the shared case state

### C.1 The design: two halves, one view
- **The structured half (Postgres, `sovereign` schema):** `case_context` (one row per case: tenant, patient_ref, status) + `case_document` (every document the case holds: doc_type · source_lane · source_ref · qdrant_point · added_by) + `agent_view_claim` (which agent claimed which case when, and which bundle version they worked from).
- **The vector half (Qdrant):** per-document vectors stored with payload `{case_id, patient_ref, doc_type, source_lane, added_by, added_at}` — the same keys as `case_document`, so the two halves join on `qdrant_point`/`case_id`. Retrieval = `qdrant_find` filtered by `case_id`.
- **The rule stack (from the clinical memory-graph doctrine — non-negotiable):** tenant-scoped everything, source-linked facts only, EMR = the chart source of truth, drafts ≠ signed facts, clinician corrections logged as episodic lessons.

### C.2 The shared view — how coding / scribe / MIA share the one bundle
Every agent, at task start, calls **`assemble_case_bundle(case_id)`** (a Supervisory-MCP tool — to be built in Phase 3). It returns the SAME bundle to every agent:

1. **Structured summary** — Postgres: patient_ref, document inventory by type, latest actions, open Paperclip issues for the case.
2. **Vector context** — Qdrant: top-k relevant prior notes/labs/claims (the semantic half).
3. **Provenance links** — `source_ref` pointers back to the EMR object (never a copy that can drift).
4. **The claim** — a row in `agent_view_claim` recording WHO assembled for WHOM at WHICH bundle version (this is itself an audit event).

**The loop it closes:** the scribe drafts the encounter → `case_document` row + vector → the coder's next `assemble_case_bundle` sees that draft (and knows it's unsigned) → the coder's candidates land as new documents → the MIA's review reads both, flags conflicts against the EMR, and its corrections write back as new provenance-linked documents. **Nobody works from a stale per-task snapshot; the case state is the accumulator, not the prompt.**

**Why this matches/surpasses the ViClinic AHOS idea:** same shared-case-state shape, but ours is (a) two open components (Postgres + Qdrant) we already run, (b) tenant-isolated by construction, (c) audit-visible — every case-state mutation is a row in the one audit store, so "what did the agents know about patient X at 14:03" is a join, not a guess.

### C.3 The wiring order (the build phases)
| Phase | Work | Deliverable state |
|---|---|---|
| **1 — now (cheap wins)** | Run the SQL (audit + policy registry + case-context DDL in the NEW `sovereign` schema) · adopt the policy matrix | ✅ create-ready in this repo — `sql/sovereign-audit-log.sql` |
| **2 — audit + policy live** | Gateway middleware emits audit rows · Supervisory MCP enforces the matrix at tool-call · policy version stamped per event | design specified above; no production changes made |
| **3 — case engine** | `assemble_case_bundle` tool · Qdrant case payloads · wire coding/scribe/MIA to assemble on task start | design specified above |

### C.4 The verification (the acceptance questions)
1. `SELECT * FROM v_who_touched_patient WHERE patient_ref='…'` → returns the full actor/action/model/policy trail in one query.
2. `v_model_outputs_by_policy` → shows model × policy-version provenance for every output class.
3. A denied action (e.g. `coder_agent` → `chart.sign`) appears in the audit store as `decision='deny'` — the enforcement checkpoint writes it, not just the app.
4. Coding, scribe, and MIA each return the same `bundle_version` for the same `case_id` — provable shared context.

---

## D. THE ONE-LINE SCOREBOARD

| The founder's ask | The answer |
|---|---|
| Audit consolidation | `sovereign.audit_event` — append-only, one table, five question-fields, three views, six hookup points |
| Policy layer | `NURA-Policy-Matrix.md` v1.0 — 8 roles × 10 capabilities × 4 gates, five checkpoints, version-stamped |
| Case-context engine | Postgres `case_context`/`case_document` + Qdrant vectors + `assemble_case_bundle` — one shared evolving view |
| Better than the IBM's? | Same sovereign shape, open-stack, self-hosted, policy-version-per-event, tenant-isolated — and zero per-seat tax |
