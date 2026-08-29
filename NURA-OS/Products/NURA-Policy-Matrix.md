# NURA POLICY MATRIX v1.0 — the RBAC (the role → what's allowed)

**Status:** EFFECTIVE 2026-08-19 (the founder's sovereign-wiring directive) · **Companion:** [[NURA-Sovereign-Wiring]] · **Registry row:** `sovereign.policy_version` v1.0 · **SQL mirror:** `sovereign.role_capability`.

**The gates:** ✅ ALLOW (auto — logged) · 🟡 HITL (human-in-the-loop — the provider sign/authorize) · 🔴 DENY (fail-closed, logged as deny) · ⚠️ STEP-UP (HMAC step-up + human — the refunds/destructive tier).

---

## 1. THE MATRIX — 8 roles × 10 capabilities

| Role | chart.read | chart.write | chart.sign | orders.create | rx.prepare | claim.submit | comms.send_phi | data.export_phi | admin.config | audit.read |
|---|---|---|---|---|---|---|---|---|---|---|
| **founder** (CEO) | ✅ | 🟡 direction-level, never finalize | 🔴 | 🔴 | 🔴 | ✅ business lane | ✅ templated only | 🟡 | ✅ | ✅ |
| **clinician** (licensed provider) | ✅ | ✅ | ✅ their own signature | ✅ the authorizer | 🟡 submit = ⚠️ EPCS | ✅ | ✅ | 🟡 | 🔴 | ✅ |
| **coder_agent** (MSO RAF/HCC) | ✅ | 🟡 candidates only | 🔴 | 🔴 | 🔴 | 🟡 candidate codes → biller | 🔴 | 🔴 | 🔴 | 🔴 |
| **scribe_agent** (ambient) | ✅ | 🟡 drafts only | 🔴 | 🟡 prepare only | 🟡 prepare only | 🔴 | ✅ templated follow-up | 🔴 | 🔴 | 🔴 |
| **mia_agent** (clinical review) | ✅ | 🟡 draft impressions → provider | 🔴 | 🔴 recommend only | 🔴 interaction-check read-only | 🔴 | 🟡 care-gap outreach | 🔴 | 🔴 | 🔴 |
| **intake_agent** (ocr-router / lab-intake) | ✅ routing metadata | ✅ filing into chart (auto) | 🔴 | 🔴 | 🔴 | 🔴 | 🟡 missing-forms requests | 🔴 | 🔴 | 🔴 |
| **ops_agent** (n8n lanes) | 🟡 PHI-minimized | 🔴 | 🔴 | 🔴 | 🔴 | 🟡 claim-gen → HITL submit | ✅ templated campaigns | ⚠️ | 🟡 workflow config | 🔴 |
| **auditor** (compliance) | ✅ read-only | 🔴 | 🔴 | 🔴 | 🔴 | 🔴 | 🔴 | 🟡 export for audit | 🔴 | ✅ |

**The role-resolution rule:** the gateway resolves the Paperclip agent UUID (`agents` table) → RBAC role at dispatch. Unknown actor = fail-closed (`decision='deny'`, logged). The default for any capability not in this table = 🔴 DENY.

---

## 2. THE NEVER-AUTONOMOUS LIST (the founder's non-autonomous list — codified, from the MCP-Architecture v1)

| The action | The gate |
|---|---|
| Final diagnosis / treatment decision | 🔴 DENY to every agent — clinician only, human |
| Controlled-substance Rx | ⚠️ STEP-UP — the EPCS gate (Weno) |
| High-risk medication changes | 🟡 HITL — clinician authorization |
| Abnormal / critical-result disposition | 🟡 HITL — clinician disposition |
| Invasive orders | 🟡 HITL — the clinician-authorization policy |

## 3. THE STEP-UP LIST (HMAC step-up + human)

| The action | The gate |
|---|---|
| Refunds | ⚠️ STEP-UP — the NMI gate |
| Large financial moves | ⚠️ STEP-UP |
| Irreversible chart deletes | ⚠️ STEP-UP |
| Destructive admin / config | ⚠️ STEP-UP |

## 4. THE ENFORCEMENT CHECKPOINTS (where each decision is made and logged)

| # | Checkpoint | Enforces | Audit row |
|---|---|---|---|
| 1 | Gateway dispatch middleware (:8642) | role → capability BEFORE an agent runs | `gate='gateway'`, per dispatch |
| 2 | Supervisory MCP | per-tool-call gate (READ-free / WRITE=HITL / auto) | `gate='supervisory-mcp'`, per call — INCLUDING denies |
| 3 | OpenEMR API layer | clinical write gate (HITL token / provider id) | `gate='openemr'` |
| 4 | NMI payments gate | refunds = step-up | `gate='nmi'` |
| 5 | EPCS gate (Weno) | controlled-substance Rx | `gate='epcs'` |

## 5. THE VERSION RULE

Changing this matrix = INSERT a new `sovereign.policy_version` row (`v1.1` supersedes `v1.0`) and mirror the deltas into `sovereign.role_capability`. Every audit event stamps the version it ran under — **"which policy was in force at 14:03" is a column lookup, not a meeting.**
