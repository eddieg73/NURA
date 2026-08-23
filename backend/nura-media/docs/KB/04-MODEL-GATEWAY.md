# 04 — MODEL GATEWAY

The reasoning cortex. **Hermes never calls a vendor API directly — it calls `model_gateway.reason()`.**

## Layout (`backend/nura-radiology-ai/services/model_gateway/`)
`router.py` (GatewayRouter.reason) · `routing.py`/`routing.yaml` (task-driven routing table) ·
`schemas.py` (radiology reasoning I/O contract) · `tool_registry.py` (14 allow / 12 deny) ·
`phi_policy.py` (Redacts MRN/DOB/phone; whitelists internal emails) · `policy.py` (provider_review +
escalate) · `consensus.py` (flag disagreement, never average) · `retry.py` · `telemetry.py` ·
`audit.py` · `providers.py` (DeepSeek / OpenAI / Local / Stub). **Verified `GATEWAY-VERIFY-PASS`.**

## Routing (task → provider)
- `radiology_interpretation` → preferred **deepseek**, fallback local-medical-llm, structured, review
- `differential_diagnosis` → deepseek, fallback openai, **consensus if high-risk**
- `document_extraction` → local → deepseek · `patient_message_draft` → deepseek, approval required
- `coding_suggestions` → deepseek → openai · `evidence_synthesis` → deepseek → local
- `fast_extraction` → local · `clinical_embedding` → **local-encoder** (Clinical ModernBERT/nomic)

## Tool discipline (the founder's "narrow tools")
ALLOWED (context/draft only): get_patient_context, get_prior_imaging_report,
get_structured_imaging_findings, search_pubmed, get_fda_drug_label, get_lab_trends,
get_guideline_evidence, get_model_validation, create_draft_report, create_ranked_differential,
request_provider_review, storage_* read/presign.
DENIED: delete_study, write_final_diagnosis, send_patient_result, prescribe_medication,
execute_shell, raw_database_query, unrestricted_email_send, finalize_radiology_report, delete_*.

## PHI & safety
- `phi_policy` strips identifiers before ANY external call. Never send PHI to a third-party model.
- Structured JSON output required by task; validate schema, retry (3 local / 1 commercial), fall back
  provider, then degrade, then human exception queue. **Never silently discard failure.**
- High-risk/critical → provider review + consensus harness (second model identifies disagreement,
  unsupported assumptions, missing info, failure modes — **never average diagnoses**).

## Model lane (encoder vs generator — decided)
Reasoning (generator): DeepSeek cloud (PHI-stripped) · Qwen3-8B (tool-calling+JSON, primary local)
· BioMistral-7B (medical) · deepseek-r1:8b (CoT). **GatorTron/ClinicalBERT = ENCODERS** → use
Clinical ModernBERT / nomic-embed-text for the embedding/NER lane. Never reason with an encoder.
