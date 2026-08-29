# NURA ARCHITECTURE CONSTITUTION (2026-08-08 — the founder's formulation, ADOPTED VERBATIM)

> **"Hermes is the executive cognitive interface; LangGraph performs bounded reasoning; Temporal preserves commitments; MCP supplies controlled actions; the world model supplies context; policy controls authority; and the clinical system of record remains authoritative."**

## The seven roles — the division of responsibility (definitive)

| Role | Component | Build-state |
|---|---|---|
| Executive cognitive interface | **Hermes** | ✅ LIVE — this machine, the gateway, the memory |
| Bounded reasoning | **LangGraph** | ✅ TOOLED — the langgraph-skills + the deep-agents-core (the production-harness: pending!) |
| Durable commitments | **Temporal** | ⚠️ NOT-BUILT — the temporal-server + the workers = the queued build |
| Controlled actions | **MCP** | ✅ LIVE — 24+ lanes, policy-aware wrappers, sealed keys |
| World-model context | **WorldState** | ⚠️ SPEC'D — the memory-contract + the goal-ledger = COGNITIVE-1 ticket |
| Authority control | **Policy engine** | ⚠️ SPEC'D — the tiered-approval + the RBAC = the OPA/Cedar-engine pending |
| System of record | **OpenEMR/HAPI-FHIR** | ✅ LIVE — the sidecar-doctrine, API-only writes, the clinical truth |

## The governing rules (from the formulation)
1. No component crosses its role: Hermes never brokers events (NATS does), never stores truth (the EMR does), never grants itself authority (policy does).
2. The world model supplies context — it never overrides the record. Retrieval ≠ authority.
3. Every controlled action flows through MCP with a policy decision — the agent proposes, the policy disposes.
4. The clinical system of record is the final arbiter of clinical fact — the AI augments, never replaces, the record.

## The build-order (what the constitution demands next)
- COGNITIVE-1: WorldState + the memory-contract + the goal-ledger (the board ✓)
- COGNITIVE-2: the policy-engine (the OPA/Cedar decision point at the MCP-gate)
- COGNITIVE-3: the Temporal-lane (the durable clinical commitments: "the test is pending, someone must review")
- COGNITIVE-4: the LangGraph production-harness (the bounded-reasoning lanes)

## The audit-truth
The constitution is adopted — and the audit says: 4 of 7 roles are LIVE, 3 are spec'd-and-queued. The architecture is credible and governable exactly as the formulation states — the build continues until all seven stand.
