# LAB RESULTS → OPENEMR → CRM CONDITION TAGS — the Workflow (2026-08-04)

**Owner:** Hermes (RHEU) · **Clinical gate:** the licensed provider · **Source of truth:** OpenEMR
**Purpose:** Every final lab result lands in the patient's OpenEMR lab section, and the CRM gets tagged with provider-validated medical conditions (heart failure, diabetes, CKD, etc.).

---

## 1. THE PIPELINE (end-to-end)

```
LAB RESULTS ARRIVE
   (HL7 ORU via Mirth · fax via Documo · PDF/CSV upload → provider_labs queue)
        │
        ▼
1. INGEST + VALIDATE (hermes-clinical-lab-review — Step 1-2)
   · patient match (MRN/name/DOB) · source validation · extraction
        │
        ▼
2. PRELIMINARY REVIEW (hermes-clinical-lab-review — Step 3-14)
   · classification · patterns · differentials · coding suggestions (ICD-10)
   · urgency/escalation (critical → immediate provider alert)
        │
        ▼
3. PROVIDER REVIEW GATE  ← the human signs (approve / modify / reject)
   · REJECT → the task returns with the provider's notes
   · APPROVE → the results = FINAL
        │
        ▼
4. MAP INTO OPENEMR (the LAB SECTION)
   · procedure_order + procedure_result rows (the patient's encounter)
   · result_code (LOINC) · result_text · result_date · reference ranges
   · via: OpenEMR FHIR API (DiagnosticReport/Observation) OR HL7 ORU → Mirth → OpenEMR lab module
        │
        ▼
5. CONDITION DERIVATION
   · the provider-validated diagnoses/patterns → ICD-10-CM codes:
     heart failure (I50.x) · diabetes (E11.x) · CKD (N18.x) · etc.
   · ONLY codes the provider approved in Step 3 — never auto-derived diagnoses
        │
        ▼
6. TAG THE CRM (Perfex)
   · client = the patient's associated client (Medisun member → the client record)
   · tag: "Medical Conditions" custom field += the ICD-10 condition
   · via the Perfex MCP lane (perfex-mcp skill)
        │
        ▼
7. AUDIT (append-only)
   · audit_event: patient · encounter · source doc · provider · action · timestamp · hashes
```

## 2. THE SYSTEM MAP
| Step | System | Lane | Interface |
|---|---|---|---|
| 1-2 | Hermes | hermes-clinical-lab-review · provider_labs MCP | the queue |
| 3 | Provider | the review task (OpenEMR/queue UI) | human approval |
| 4 | OpenEMR | OpenEMR FHIR API / Mirth ORU | procedure_result |
| 5 | Hermes | ICD-10 mapping (provider-approved) | coding_suggestions |
| 6 | Perfex CRM | Perfex MCP (mcp-installs/perfex/server.py) | client custom field |
| 7 | Hermes | the audit log (append-only) | audit_event |

## 3. THE OPENEMR MAPPING (the lab section)
- **Patient match**: the MRN/name/DOB — NO match = stop + human review (never guess)
- **procedure_order**: the order the results belong to (the encounter/date)
- **procedure_result** fields:
  - procedure_order_id · procedure_order_seq · result_code (LOINC) · result_text
  - result_date · result_status (final — never preliminary) · normal_range
  - units · interpretations (abnormal/critical — the provider-validated flags)
- **Result status**: ONLY "final" results enter the chart (the provider approved)
- **No direct writes** to the signed record without the provider authorization step (Section 4)

## 4. THE CRM TAGGING (Perfex)
- The client record: the patient's associated client (the tenant/member mapping — Medisun members → the client)
- The tag: the client custom field `medical_conditions` — the ICD-10-CM code + the label (e.g. "E11.9 — Type 2 diabetes without complications")
- The tagging happens ONLY after the OpenEMR write succeeds (the EMR-first order)
- The CRM = the operational view (care gaps, RAF, follow-ups) — the EMR = the clinical truth (never the reverse)

## 5. THE GATES (non-negotiable)
1. **Provider review BEFORE any EMR write** — the review task must be accepted
2. **Patient identity validated** — mismatch = stop
3. **Only "final" results enter the chart** — pending/preliminary never write
4. **ICD-10 conditions = provider-approved only** — no auto-diagnosis tagging
5. **EMR first, CRM second** — the CRM tag follows a successful EMR write
6. **PHI stays on the Lattice** — no patient data leaves the fleet
7. **Audit every step** — the append-only trail: who/what/when/hashes

## 6. THE AUTOMATION (n8n candidate)
```
Trigger: provider_labs queue → result finalized
→ OpenEMR MCP (write procedure_result) → verify (read-back)
→ Perfex MCP (update client medical_conditions) → verify
→ audit event → notify the provider (task complete)
· Failure at any step: stop + the ticket (trouble-ticket-log) — never partial writes
```

## 7. THE CONDITION LIBRARY (the common tags, ICD-10)
| Condition | ICD-10 | Source pattern |
|---|---|---|
| Heart failure | I50.9 | BNP ↑ · echo findings · fluid overload |
| Type 2 diabetes | E11.9 | HbA1c ≥ 6.5% · glucose pattern |
| Chronic kidney disease | N18.x | eGFR < 60 ×3mo · creatinine ↑ |
| Hypertension | I10 | BP pattern · follow-up |
| Anemia (iron deficiency) | D50.9 | Hgb ↓ · ferritin ↓ · MCV ↓ |
| Hyperlipidemia | E78.5 | LDL ↑ · triglycerides ↑ |
*(The library = suggestions only — the provider approves the tag)*

## 8. THE AUDIT SCHEMA
```json
{"event": "lab_result_finalized", "patient_id": "", "encounter_id": "",
 "source_document_id": "", "actor_id": "", "actor_role": "provider",
 "action": "openemr_write|crm_tag", "timestamp": "",
 "icd10": "", "result_status": "final", "source_hash": "", "output_hash": ""}
```

## Related
hermes-clinical-lab-review · openemr-mcp-n8n-orchestration · practice-revenue-operations · perfex-mcp · provider_labs MCP · hermes-clinical-interoperability · trouble-ticket-log · hermes-coding-quality-compliance
