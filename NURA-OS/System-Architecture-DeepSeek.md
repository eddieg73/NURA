# Unified Healthcare & Aesthetic Practice OS — System Architecture (Principal Architect, 2026-08-02)

Deliverables 1-3: Architecture Overview · Local/Cloud Sync Protocol · Primary DB Schema. Built against the VERIFIED NURA stack (Hostinger fleet, OpenEMR/Perfex/GHL, Mirth, Orthanc, Hermes gateway, FlutterFlow app, offline SLM).

## 1. ARCHITECTURE OVERVIEW (zero-trust, PHI-isolated)
```
[ Client: Flutter (5-tab bottom: News/Ask/Dialer/Scribe/Fax + 3x4 Practice grid) ]
   ├── Offline Engine: whisper.cpp/CoreML + quantized SLM (MedGemma/Qwen3-8B via mlc_llm)
   │                   SQLCipher SQLite/CRDT queue · wipe on logout · masked push
   └── TLS 1.3 + App Attestation + OAuth PKCE (OpenEMR identity)
                              │
              [ Hermes API Gateway :8642 + Auth (MFA/JWT/timeouts) ]
                              │
   ┌──────────────────────────┴───────────────────────────┐
   ▼                                                      ▼
[ NON-PHI services ]                            [ HIPAA SECURE ZONE — Clinic 1441409 ]
  News/CME · Directory (NPPES)                    OpenEMR (EHR) · Orthanc (PACS) · ThaiRIS
  · Perfex/GHL CRM pipelines                       · Mirth Connect (HL7v2/v3/FHIR R4) · Wet-Read
                                                   gateway · Ephemeral AI (in-memory drafts)
                              │
              [ App Platform DB: PostgreSQL/JSONB (new — cloud schema below) ]
                              │
              [ Lab 1030183: training/inference (Bio_ClinicalBERT, Qwen2-VL) — NO PHI ]
              [ R2: WORM audit snapshots · n8n: orchestration · Qdrant: RAG (non-PHI) ]
```

## 2. LOCAL/CLOUD SYNC PROTOCOL (offline-first, op-log CRDT-style)
- **Local store**: SQLCipher SQLite; every row carries `sync_state` (queued|syncing|synced|conflict), `op_ts` (monotonic LWW timestamp), `device_id`, `op_id` (UUID idempotency key), `base_rev`
- **Write path (offline)**: write locally → mark queued → append to outbox (op-log) → return to UI immediately (optimistic)
- **Sync triggers**: on reconnect · app foreground · 30s idle timer · manual "Sync Now"
- **Reconcile (server, idempotent)**: 1) PULL: server sends ops since client's last cursor (per entity stream)  2) PUSH: client sends outbox ops  3) CONFLICT: LWW by op_ts; **clinical fields (notes/billing) never auto-resolve → flag conflict → provider review**  4) ACK: server returns applied op_ids → client marks synced; retry with backoff (5 attempts → circuit breaker)
- **CRDT choice**: LWW-register per field + op-log for append-only streams (messages, fax logs, audit) — simple, verifiable, no merge complexity for clinical data (provider-reviewed anyway)
- **Audit**: every op hashes into the WORM chain (prev_hash + op_hash) — snapshots to R2

## 3. PRIMARY DATABASE SCHEMA
### Cloud: PostgreSQL/JSONB (app platform DB — PHI stays in OpenEMR; app DB holds sync + comm + billing + fax metadata)
```sql
CREATE TABLE providers (id UUID PK, npi TEXT UNIQUE, openemr_user_id INT, name JSONB,
  credentials TEXT, state TEXT, verified_at TIMESTAMPTZ, created_at TIMESTAMPTZ DEFAULT now());
CREATE TABLE patients (id UUID PK, openemr_pid INT UNIQUE, demographics JSONB, travel JSONB,
  created_at TIMESTAMPTZ DEFAULT now());
CREATE TABLE encounters (id UUID PK, patient_id UUID REFERENCES patients, openemr_eid INT,
  provider_id UUID REFERENCES providers, type TEXT, status TEXT, started_at TIMESTAMPTZ);
CREATE TABLE notes (id UUID PK, encounter_id UUID REFERENCES encounters, note_type TEXT,
  content JSONB,  -- SOAP + confidence + source_citations
  sync_state TEXT DEFAULT 'queued', op_id UUID UNIQUE, op_ts BIGINT, base_rev BIGINT,
  requires_provider_review BOOLEAN DEFAULT true, provider_reviewed_at TIMESTAMPTZ,
  mirth_ack TEXT,  -- HL7 ACK id once pushed to OpenEMR
  created_at TIMESTAMPTZ DEFAULT now());
CREATE TABLE outbox (op_id UUID PK, entity TEXT, entity_id UUID, op TEXT, payload JSONB,
  device_id TEXT, op_ts BIGINT, attempts INT DEFAULT 0, state TEXT DEFAULT 'queued');
CREATE TABLE communication_threads (id UUID PK, patient_id UUID, channel TEXT,
  direction TEXT, metadata JSONB);
CREATE TABLE messages (id UUID PK, thread_id UUID REFERENCES communication_threads,
  body TEXT, masked_push BOOLEAN DEFAULT true, sent_at TIMESTAMPTZ);
CREATE TABLE fax_logs (id UUID PK, patient_id UUID, direction TEXT, documo_id TEXT,
  pages INT, summary JSONB, status TEXT, created_at TIMESTAMPTZ DEFAULT now());
CREATE TABLE billing_claims (id UUID PK, encounter_id UUID, icd10 JSONB, cpt JSONB,
  status TEXT, submitted_at TIMESTAMPTZ);
CREATE TABLE audit_ledger (op_hash TEXT PK, prev_hash TEXT, entity TEXT, entity_id UUID,
  actor TEXT, payload_hash TEXT, ts TIMESTAMPTZ);  -- WORM: INSERT-only, verified chain
CREATE INDEX ON notes (encounter_id); CREATE INDEX ON outbox (state, op_ts);
```
### Local: SQLite/CRDT mirror (same core entities + sync meta)
```sql
CREATE TABLE local_notes (id TEXT PK, encounter_id TEXT, note_type TEXT, content TEXT,
  sync_state TEXT, op_id TEXT, op_ts INTEGER, base_rev INTEGER, device_id TEXT);
CREATE TABLE sync_meta (stream TEXT PK, last_cursor BIGINT, last_sync_at TEXT);
CREATE TABLE audio_segments (id TEXT PK, path TEXT, transcribed INTEGER DEFAULT 0, wiped INTEGER DEFAULT 0);
-- wipe on logout/expiry per policy; audio never leaves device (ephemeral)
```
### Data rules
- PHI content lives in OpenEMR (Clinic); app DB = sync/comm/billing/fax metadata + JSONB clinical DRAFTS (provider-reviewed, then pushed; drafts purged per ephemeral policy)
- No boolean in SQLite (0/1 ints) · every sync op idempotent · masked push payloads only

## Remaining deliverables (next pass, per request)
4. Mobile frontend state plan (Riverpod/Bloc + grid/tab/badge structure) · 5. AI agent pipelines (receptionist STS→intent→scheduling→TTS; hybrid scribe; fax summarizer) → NUR-103 CTO sequencing.
