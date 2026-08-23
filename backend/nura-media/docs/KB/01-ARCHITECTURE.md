# 01 — ARCHITECTURE

How the NURA platform is put together and why.

## Core principle
**Hermes is the spine, not a peripheral.** Every module publishes/subscribes to Hermes events;
no module writes another module's database. All state changes are events. Hermes owns workflow,
tool-control, safety, provenance, and audit — and is **model-agnostic** (the reasoning engine is
interchangeable).

## Layers
1. **Event/Workflow engine** — Hermes + durable broker (**NATS JetStream** for durable clinical
   events; **Redis** for transient: locks, rate-limit, cache, idempotency window). Postgres outbox/inbox.
2. **Model Gateway** — `model_gateway.reason(task,payload)`. Routes by TASK (routing table), enforces
   policy (provider-review, consensus-if-high-risk), runs consensus for high-risk (disagree, never
   average), validates schema, retries/falls back, PHI-strips, audits every call. Providers are
   interchangeable: DeepSeek (cloud), Qwen3/BioMistral (local), OpenAI (fallback).
3. **Knowledge & Dataset Gateway** — FDA/PubMed/radiology/lab data behind a controlled gateway
   (`dataset_registry` + license/DUA enforcement). No PHI leaves. Never called directly by the model.
4. **Domain subsystems** — Clinical (OpenEMR/Mirth/MedPlum), Radiology (Orthanc/ThaiRIS/AI),
   Media (nura-media), each emitting/consuming events.

## Event envelope (canonical)
```json
{"spec_version":"1.0","event_id":"uuid","event_type":"nura.imaging.inference.completed.v1",
 "source_service":"radiology-orchestrator","tenant_id":"...","patient_ref":"opaque-uuid",
 "correlation_id":"workflow-uuid","causation_id":"prior-event-uuid","idempotency_key":"sha256(...)",
 "occurred_at":"...","data_classification":"PHI","payload_ref":"s3://.../object.json",
 "payload_sha256":"hex","provenance":{...}}
```
**Events carry references, never PHI payloads.** Large objects (DICOM, media, docs) go to B2.

## The model abstraction (the key design ratio)
```
HERMES = nervous system      | one, owns the workflow & safety
MODEL GATEWAY = reasoning    | DeepSeek/Qwen3/BioMistral, replaceable
IMAGING MODELS = visual      | structured findings first, never raw pixels to a text model
ORTHANC = imaging memory     | B2 = durable objects
POSTGRES = structured memory | REDIS = working memory | QDRANT = semantic memory
PUBMED/FDA = external knowledge | MIRTH/FHIR = interoperability | OHIF = provider UI
```
If DeepSeek disappears, is too costly, or is PHI-blocked — you change the route, not the design.

Related: `docs/NURA-ECOSYSTEM.md` (governing decisions A1-A5, D1-D4, MD1).
