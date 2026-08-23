# NURA Storage Architecture — Hostinger (dev) + Backblaze B2 (durable PHI objects)

Governing rule (founder 2026-08-23): **Hostinger is NOT a HIPAA host.** Use it for
dev/non-PHI/synthetic only. **Backblaze B2 = durable object storage** (BAA executed before any
production PHI). Postgres = durable structured state · Hermes = workflow/events (object refs,
never pixel payloads) · Redis = transient only · Compute VPS = replaceable.

## Bucket plan (separate dev and prod; never share credentials)
| Bucket | Class |
|---|---|
| `nura-prod-clinical-imaging` | PHI — DICOM, SR, SEG, presentations, multi-frame US, DXA, mammo, CT, MRI |
| `nura-prod-clinical-documents` | PHI — PDFs, reports, referrals, faxes, scans, patient uploads |
| `nura-prod-clinical-audio` | PHI — clinical audio |
| `nura-prod-ai-derived` | PHI — DICOM-SR/SEG, PNG, findings JSON, AI overlays |
| `nura-prod-audit` | audit — Object Lock, no-delete app key |
| `nura-prod-backups` | backups — encrypted, Object Lock |
| `nura-research-deidentified` | de-identified research |
| `nura-datasets-public` | datasets (public / registered / DUA-restricted) |
| `nura-model-artifacts` | model checkpoints, cards, manifests |
| `nura-development` | dev / synthetic / non-PHI |

## Object keys — NO PHI in names
`objects/<hash-prefix>/<opaque-uuid>.dcm` — never `John-Doe/`, `MRN-...`, `DOB-...`.
Patient identity lives only in the clinical DB; B2 stores opaque references.

## Orthanc S3 plugin → B2 (evaluate for production; validate plugin version against B2)
```json
{
  "AwsS3Storage": {
    "BucketName": "nura-prod-clinical-imaging",
    "Region": "${B2_REGION}",
    "AccessKey": "${B2_ACCESS_KEY_ID}",
    "SecretKey": "${B2_SECRET_ACCESS_KEY}",
    "Endpoint": "${B2_S3_ENDPOINT}",
    "StorageStructure": "flat"
  }
}
```
Secrets via env substitution / secret manager — never in source-controlled JSON.
**Validate with synthetic DICOM first**: C-STORE, retrieve, multi-frame US, CT, MRI, mammo,
concurrent uploads, Orthanc restart, B2 interruption, checksum, index consistency.

## storage_object DB (Postgres object metadata; B2 holds the bytes)
```sql
CREATE TABLE storage_object (
  id UUID PRIMARY KEY,
  tenant_id UUID NOT NULL,
  bucket_class TEXT NOT NULL,       -- clinical-imaging | documents | audio | ai-derived | audit | ...
  object_key TEXT NOT NULL,         -- objects/<hash-prefix>/<uuid>.dcm
  content_type TEXT,
  size BIGINT,
  sha256 TEXT,
  encryption_status TEXT,
  source_system TEXT,               -- orthanc | gmail | fax | portal | ai
  source_event_id UUID,
  patient_ref UUID, study_ref UUID,
  created_at TIMESTAMPTZ DEFAULT now(),
  created_by TEXT,
  current_version INT,
  retention_policy_id UUID,
  status TEXT
);
```

## Hermes storage events (refs, not payloads)
`nura.storage.object.created.v1` · `.verified.v1` · `.failed.v1` ·
`nura.storage.document.created.v1` · `nura.storage.dicom.created.v1` ·
`nura.storage.integrity.failed.v1` · `nura.storage.legal-hold.changed.v1`.

## Security
- TLS everywhere; B2 server-side encryption; consider app-level encryption for sensitive datasets.
- Per-service least-privilege app keys (orthanc-prod, ai-readonly, audit-writer-no-delete, dataset-ingest).
- Pre-signed short-lived URLs only (never expose B2 master creds to OHIF/browser/agents/portal).
- Object Lock on audit/backup; the app account should NOT hold delete/disable-retention capability.
- Multi-tenant: every object has tenant_id; authorize user→tenant→patient→object, never by knowing the ID.

## Dev environment (Hostinger)
Run Hermes, Orthanc, OHIF, Mirth, Postgres, Redis, Qdrant, NURA API, MONAI with **Synthea +
public/de-identified DICOM + synthetic patients only**. No real PHI on Hostinger.

## Implementation order
Confirm BAA host → execute B2 BAA (before prod PHI) → dev B2 account/buckets → separate prod
account/buckets → MFA → restricted app keys → encryption → Object Lock → storage service →
storage_object schema → SHA-256 verification → Hermes events → Orthanc+Postgres → Orthanc
object-storage plugin → validate with synthetic DICOM → C-STORE → DICOMweb → OHIF → outage/
restart/restore tests → document object path → Gmail/fax ingest → DB backup → audit storage →
DR test → security review → only then production PHI.
