# NURA COGNITIVE CONTRACTS v1 (2026-08-07 — the founder's review, codified!)

**The review's verdict accepted: the infrastructure ~90%, the cognitive-architecture ~40%. The missing pieces = the cognitive contracts + the control boundaries + the evaluation. This doc = the definitive division + the contracts + the tiers — the buildables!**

## 1. THE DEFINITIVE DIVISION (the overlap-killer — the review's table, adopted!)
```
Hermes = the conversational executive + the delegation (NOT the broker/DB/policy!)
Agent-Registry = identities · permissions · versions · lifecycle
LangGraph = the bounded cognitive state-machines
Temporal = the durable workflows (minutes→months!)
NATS-JetStream = the event transport ONLY
PostgreSQL = the authoritative state + the event-ledger
n8n = the ADMIN automation only
MCP-Gateway = the policy-enforced tool-invocation
LiteLLM = the routing · budgets · failover
OpenEMR/FHIR = the clinical system-of-record
Qdrant = the rebuildable index (NOT the authoritative memory!)
```

## 2. THE WORLDSTATE CONTRACT (the machine-readable world!)
- The entities: patients · providers · organizations · encounters · relationships!
- The state: problems · meds · allergies · orders · results · appointments · tasks · commitments!
- The metadata: versioning · provenance · uncertainty · temporal-validity · conflicts · consent!
- The JSON-schema: the memory-record (below!) as the unit!

## 3. THE MEMORY-CONTRACT (every durable memory!)
```json
{"memory_id": "uuid", "tenant_id": "org", "subject_ref": "opaque-ref",
 "memory_type": "episodic|semantic|procedural", "statement": "normalized",
 "source_ref": "authoritative", "source_type": "human|ehr|device|model|external",
 "confidence": 0.0, "valid_from": "ts", "valid_until": "ts|null",
 "review_at": "ts", "supersedes": [], "contradicts": [],
 "verification_status": "unverified|corroborated|verified|disputed",
 "data_classification": "PHI", "consent_basis": "auth-ref"}
```
- The functions: consolidation · contradiction-detection · confidence-decay · temporal-expiry · supersession · patient-context-separation · right-to-forget · source-scoring · retrieval-authz · correction-propagation · the NO-AI-becomes-fact rule!

## 4. THE GOAL-LEDGER (the persistent commitments!)
- objective · principal · authority-scope · priority · dependencies · deadline · completion-criteria · action-budget · risk-class · approvals · plan-version · abandonment · outcome · follow-up-obligations!
- The canonical example: "I ordered a test → the result is pending → someone must review it" — the ledger keeps the commitment alive!

## 5. THE POLICY-DECISION-POINT (the unified authority!)
- OPA/Cedar-class engine: "May agent-X use tool-Y on patient-Z for purpose-P under tenant-T using data-class-D without approval-A?"
- EVERY tool-call gets the signed, short-lived authorization — the MCP-server ENFORCES it (never trusts the agent!)

## 6. THE TIERED-APPROVAL (the auto-approve-FIX — the dashboard-flag!)
```
Read-only retrieval → AUTO · Draft generation → AUTO
Administrative-reversible → policy-dependent
Patient-communication → reviewed/narrowly-pre-authorized
Chart-write → PROVIDER approval
Orders/Rx/diagnosis/referrals/billing → QUALIFIED human authorization
Destructive/security → EXPLICIT admin approval
```
- The founder's screenshot showed the global auto-approve ENABLED — the tiered-model replaces it, NOW!

## 7. THE EVALUATION-FRAMEWORK (the named metrics!)
| Domain | Metric |
|---|---|
| Scribe | concept-recall · omission-rate · unsupported-statement-rate |
| Identity | wrong-patient-event-rate |
| Retrieval | recall@k · source-precision · authz-leakage |
| Clinical-QA | factuality · citation-entailment · contraindication-recognition |
| Coding | ICD-10/CPT precision + recall |
| Tool-use | valid-call-rate · correct-tool-rate · side-effect-error |
| Abstention | appropriate-refusal sensitivity + specificity |
| Agent | completion-without-rescue · dup-action-rate |
| Security | prompt-injection-rate · cross-tenant-leakage |
- The golden-set: synthetic-patients · adversarial · incomplete · conflicting · critical-results · med-interactions · wrong-patient-traps!

## 8. THE SELF-IMPROVEMENT-GOVERNANCE (the controlled pipeline!)
```
Observed-failure → Improvement-proposal → Sandbox-eval →
Safety+regression-tests → HUMAN-approval → Versioned-deploy → Outcome-monitor
```
- The agent proposes; it NEVER silently alters clinical-rules/prompts/permissions/workflows!

## 9. THE BUILD-ORDER (the team-queue!)
1. The WorldState + the memory-contract (the schema + the store!)
2. The Goal-ledger (the commitments-service!)
3. The Policy-decision-point (the OPA/Cedar-engine + the MCP-enforcement!)
4. The tiered-approval (the auto-approve-replacement!)
5. The eval-framework + the golden-set (the release-gates!)
