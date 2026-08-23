# 06 — DATA FABRIC & STORAGE (boundaries + contracts)

The architect's core insight: **every data type has exactly one home, and compute is disposable.**
This is what makes the platform recoverable and portable.

## One truth per store (the separation that governs everything)
| Store | Owns | Never holds | Why |
|---|---|---|---|
| **Postgres** | durable structured state: patients, study/report metadata, workflow, audit, object metadata, model registry, generation ledger | large binaries | Source of truth; queryable; transactional |
| **Backblaze B2** | large binaries: DICOM, docs, audio, media renders, models, datasets | patient identity in keys; nothing queryable | Durable object layer; exit-friendly; BAA-able |
| **Redis** | transient: locks, rate-limit, cache, queue coordination, idempotency window | durable clinical record — **never** | Ephemeral by design |
| **Qdrant / pgvector** | embeddings / semantic index | source binaries (store refs: object_id, chunk) | Vector similarity |
| **Compute VPS** | nothing durable — replaceable | any authoritative data | If the box dies, recover without its disk |

## Object-key contract (no PHI in keys)
`objects/<hash-prefix>/<opaque-uuid>.dcm` — never `John-Doe/`, `MRN-…`, `DOB-…`. Patient identity
lives only in the clinical DB. B2 holds opaque references + metadata in storage_object.

## Buckets (prod vs dev never share credentials)
`nura-prod-clinical-imaging|documents|audio` · `nura-prod-ai-derived` · `nura-prod-audit` (Object Lock,
no-delete key) · `nura-prod-backups` (encrypted, Object Lock) · `nura-research-deidentified` ·
`nura-datasets-public` · `nura-model-artifacts` · `nura-development`.

## Compute vs data boundaries
- **Hostinger = dev/non-PHI/synthetic** (terms disclaim HIPAA). Control-plane only — no large models.
- **Production PHI compute = a BAA-executing provider** (decision/purchase pending).
- **B2 = PHI-capable only after the B2 BAA** is executed. Never before.
- Access via **short-lived signed URLs** (never expose B2 master creds to OHIF/browser/agent/portal).
- Orthanc: index in Postgres, objects in B2 (S3 plugin). Validate plugin against B2 with synthetic
  DICOM first (C-STORE, multi-frame US, CT, MRI, mammo, concurrent, restart, checksum, index).

## Reference
`backend/nura-radiology-ai/storage/B2-STORAGE-BLUEPRINT.md` · `infrastructure/media_schema.sql`.
