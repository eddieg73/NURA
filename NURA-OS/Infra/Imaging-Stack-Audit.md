# Imaging Stack Audit — live probe (2026-08-19)

Probed by: NURA Imaging & Interop Engineer · Method: read-first, no PHI, no prod
changes (one synthetic study pushed + deleted to prove the lane — PACS restored to 0).
Sources: SSH Clinic (72.61.71.211), REST/DICOMweb, MLLP passive probes, MCP lanes.

## Scoreboard

| # | Component | Status | Evidence |
|---|---|---|---|
| 1 | Orthanc PACS (`orthanc-pacs`) | **PASS** | Up 7h · API v30 · AET NURAPACS · auth 401-anon/200-auth · DICOMweb 200 · 0 studies · ingest C-STORE 0x0000 verified |
| 2 | OHIF viewer (`ohif-viewer`) | **PARTIAL — UI PASS, data path FAIL** | HTTP 200 on :32791 · nginx DICOMweb routes `/dicom-web-pacs/` + `/dicom-web-legacy/` = **401 even with Basic auth** |
| 3 | ThaiRIS 1.8 (`nura-ris-web` + `nura-ris-db`) | **PASS** | Both healthy · HTTP 200 on :32790 |
| 4 | OIE Mirth 4.6 (`mirth-oie46`) | **PARTIAL — engine PASS, channels UNVERIFIED** | Engine Up 7h · version 4.6.0 · postgres healthy · **admin login FAIL (stale creds)** · MLLP 6661/6663 OPEN, **6665/6666/6667 CLOSED** |
| 5 | OpenEMR (`openemr-zklo-openemr-1` + mariadb) | **PASS** | Healthy · 302→login · MCP patient-search lane answers (synthetic query → `[]`, zero PHI pulled) |
| 6 | Adjacent: radris stack (`radris-stack-radris-1`) | **FAIL (adjacent)** | Django app Exited(1) — `Couldn't load manifest 'staticfiles.json'` · its nginx (80/443) still fronts the OHIF DICOMweb routes |

## 1. Orthanc PACS — PASS

- `docker ps`: Up 7 hours · ports 4242 (C-STORE) + 8042 (REST/DICOMweb) on 0.0.0.0
- `/system`: ApiVersion 30 · DicomAet `NURAPACS` · IsHttpServerSecure true ·
  DICOMweb root `/dicom-web/` · Orthanc Explorer 2 enabled
- Auth: anonymous `/statistics` = 401 · `nuraadmin` = 200 ✓
- `/statistics`: **0 studies / 0 series / 0 instances / 0 patients** (pristine)
- `/modalities`: **`[]` — empty** ← the top gap (see Gaps)
- `/peers`: `[]`
- **Ingest lane verified end-to-end (QA run, then cleaned):** synthetic CR via
  pynetdicom AE `NURAMAMMO` → `NURAPACS` through the SSH tunnel → C-STORE 0x0000 →
  statistics 1/1/1/1 → QIDO-RS 200 (study `QA^SYNTHETIC`, PatientID
  `NURATEST-0001`) → WADO-RS series metadata 200 → `DELETE /studies/{id}` →
  statistics back to **0/0/0/0**. The C-STORE gate on 4242 works from a modality AE.

## 2. OHIF viewer — UI PASS, data path FAIL

- :32791 = **200** (the viewer UI serves) ✓
- `app-config.js`: two DICOMweb datasources — `pacs` (default) →
  `/dicom-web-pacs/`, `legacy` → `/dicom-web-legacy/`, `requestFromBrowser: true`
- nginx (radris-stack-nginx-1) routes:
  - `/dicom-web-pacs/` → `http://orthanc:8042/dicom-web/` → resolves to
    **radris-stack-orthanc-1** (a second Orthanc, not `orthanc-pacs`)
  - `/dicom-web-legacy/` → `http://host.docker.internal:8042/dicom-web/` →
    the main `orthanc-pacs`
- **Live probe: BOTH routes return 401 through nginx — anonymous AND with Basic
  auth forwarded.** The direct Orthanc DICOMweb path returns 200 with the same
  credentials, so the nginx layer is dropping/not forwarding the Authorization
  header (or adding its own). Net effect: **the viewer currently has no working
  study data path from the browser.**
- Also: the default datasource (`pacs`) points at the radris Orthanc while the
  production PACS is `orthanc-pacs` — a routing decision to reconcile.

## 3. ThaiRIS 1.8 — PASS

- `nura-ris-web` (Up ~1h, healthy) · `nura-ris-db` (healthy) · :32790 = **200**
- Path `/docker/nura-ris` per the deploy record.

## 4. OIE Mirth 4.6 — engine PASS, channel layer UNVERIFIED (credential-blocked)

- Engine container Up 7h · admin https on :8445 (self-signed → `curl -sk`) ·
  `/api/server/version` = **4.6.0** (not auth-gated — not an auth test)
- postgres `mirth-oie46-postgres-db-1` healthy · engine log shows 3 clean starts,
  no channel-deploy errors in the tail
- **Admin auth: FAIL** — the sealed `MIRTH_USER`/`MIRTH_PASS` from the profile
  .env returns `LoginStatus: Incorrect username or password` → `/api/channels`
  and statuses are UNVERIFIABLE until the founder provides the current password
  (known trap: sealed values go stale after a rotation).
- MLLP passive probes (in-container):
  - `6661` **OPEN** (host-mapped as :6663)
  - `6665` **CLOSED** · `6666` **CLOSED** · `6667` **CLOSED**
  - → the channels described in the stack record (RISPACS_HERMES :6667,
    OPENEMR_HERMES :6666, MLLP solis_hermes :6665) are **NOT listening** today.
- Local Mirth MCP (`mcp__mirth__*`): Connection refused — its default endpoint
  (localhost:8081) is not tunneled to the Clinic.

## 5. OpenEMR — PASS

- `openemr-zklo-openemr-1` + mariadb both healthy · :32768 = 302 → login redirect
  (normal for OpenEMR)
- MCP lane: `openemr_patient_search("ZZTEST-NOPHI-PROBE")` → `[]` — the API
  answers correctly; no PHI was pulled for this audit.

## 6. Adjacent finding — radris stack (FAIL)

- `radris-stack-radris-1`: **crash loop → Exited(1)** — Django raises
  `ValueError: Couldn't load manifest 'staticfiles.json' (version 1.1)` (missing
  deploy artifact). Restart policy keeps retrying.
- Up in the same stack: `radris-stack-nginx-1` (owns public 80/443 and the OHIF
  DICOMweb routes), `radris-stack-orthanc-1` (internal), `radris-stack-db-1`.
- Impact: the front proxy survives, but the radris RIS app is down. The crash is
  the root-cause blocker for any radris-driven worklist flow.

## The gaps (ranked)

1. **Modality AEs not registered** — `/modalities` = `[]`. NURAMAMMO / NURADEXA /
   NURAXCUBE are defined by the Modality-Integration-Spec (vault
   NURA-OS/Engineering/Modality-Integration-Spec.md) but **cannot be registered
   yet: each device's static IP (and DICOM port, default 104) is only known at
   install time**. Exact PUT calls are staged in the QA/ops doc; do not register
   placeholder hosts (that creates broken outbound C-STORE/C-FIND routes).
2. **OHIF data path 401 through nginx** — the viewer renders but cannot load
   studies; auth forwarding on `/dicom-web-pacs|legacy` must be fixed, and the
   default datasource's target (radris Orthanc vs orthanc-pacs) decided.
3. **Mirth channel layer unverified + listeners down** — stale admin creds block
   REST verification; MLLP 6665/6666/6667 closed. Escalate the password to the
   founder, then re-verify channel states + redeploy what's stopped.
4. **radris-stack-radris-1 crash loop** — staticfiles manifest deploy fix.
5. **Privacy posture** — 4242 + 8042 are bound to 0.0.0.0 on the Clinic host;
   confirm the Hostinger cloud firewall covers them (4242 must stay private).
6. **MCP lanes unwired** — the Orthanc MCP (19 tools, built) and the Mirth MCP
   need tunneled endpoints / Hermes MCP registration; b2 CLI not installed
   (b2-mcp present).

## What was NOT touched (per constraints)

- No PHI accessed anywhere; OpenEMR queried only with a synthetic name.
- No prod channel modified: zero Mirth calls that write, zero Orthanc config
  changes, the only write was the synthetic QA study — deleted, statistics
  re-verified at 0.
- No AE registered against placeholder hosts (deliberate gate, see gap 1).
