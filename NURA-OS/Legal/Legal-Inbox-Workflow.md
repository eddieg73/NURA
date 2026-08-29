# LEGAL INBOX WORKFLOW — legal@nuratech.ai (2026-08-02)

**Goal:** Alex Stavrou emails case info → legal@nuratech.ai → Hermes ingests, disseminates,
# Legal + Medical Inbox Workflow (verified 2026-08-02)

## Mailboxes (sealed in .env 0600)
- `legal@nuratech.ai` — LEGAL case mail (Stavrou + case patterns only)
- `medfax@nuratech.ai` — MEDICAL ingestion (fax-to-chart, provider docs)
- Both created 08-02; IMAP creds sealed (LEGAL_IMAP_* / MEDFAX_IMAP_*)
- **BLOCKER (user action)**: Google 2-Step Verification on both accounts blocks plain-password IMAP
  (AUTHENTICATIONFAILED verified). Fix = turn off 2SV on both (ingestion-only mailboxes) OR create
  App Passwords (T18) — then the 30-min legal-inbox-poll goes live automatically.

## The flow
```
ALEX → legal@nuratech.ai (case emails + attachments)
  → LEGAL INBOX POLL (cron, every 30 min — silent when empty)
  → INGEST (legal-inbox-ingest.py):
      · parse sender/subject/date
      · download attachments (autopsy PDFs, records, discovery)
      · auto-create case folder under /opt/data/legal-cases/CASE-XXX (0700, sealed)
      · move docs into source/ · update manifest.json (no PHI in manifest names)
  → DISSEMINATION ALERT (Telegram to Eddie — case id + doc list + sender)
  → RESEARCH PREP (on engagement — skill forensic-medical-review):
      · OCR → chronology → autopsy/tox/med analysis
      · legal lanes: CourtListener/FL dockets/eCFR/FL Admin
      · clinical lanes: DailyMed/openFDA/PubMed
      · evidence-cited draft → Eddie + forensic pathologist sign
```

## The legal bolt (separate lane)
- **LEXA** = the legal-work agent lane (compliance + case workflow)
- Sealed workspace `/opt/data/legal-cases/` — OUTSIDE RAG/vault (privilege)
- Board: MLR project lane for case tracking (non-PHI)
- Quiet: no public mention, ever

## Activation checklist (founder)
1. Create **legal@nuratech.ai** mailbox (Google Workspace admin)
2. IMAP on + app password (or OAuth) → seal creds in .env as LEGAL_IMAP_* (0600)
3. Alex uses legal@nuratech.ai for all case mail (or CC/forward rule)
4. Cron activates automatically when creds present; silent until then
