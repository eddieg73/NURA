# MEDISUN RIS + PACS SETUP (1441409 Clinic host, 2026-08-02)
Stack: Orthanc (PACS) + OHIF (viewer) + ThaiRIS (RIS) — production on KVM4 (PHI boundary). Deploy = host-side block below. Expected outputs included — paste back anything that differs.

## 1. On the 1441409 host (root) — one block
```bash
cd /opt/data/imaging-stack   # or /opt/nura/imaging-stack if moved

# Secrets (fill STRONG values, chmod 600)
cat > .env <<'EOF'
THAIRIS_DB_ROOT_PASSWORD=CHANGE_ME_STRONG_ROOT
THAIRIS_DB_PASSWORD=CHANGE_ME_STRONG_APP
THAIRIS_DB_NAME=thairis
THAIRIS_DB_USER=thairis
ORTHANC_TAG=latest
OHIF_TAG=latest
EOF
chmod 600 .env

# Orthanc admin password (edit modules/orthanc/orthanc.json RegisteredUsers + healthcheck below):
#   "orthanc": "CHANGE_ME_ORTHANC_PASS"  ->  set a strong password in BOTH places
#   (docker-compose.pacs.yml line 16 healthcheck curl -u orthanc:CHANGE_ME_ORTHANC_PASS must match)

# Build the ThaiRIS image (local Dockerfile in imaging-stack)
docker build -t nura-thairis:1.0 .

# Create the shared network (if missing)
docker network create nura 2>/dev/null || true

# Bring up RIS (thairis + db) then PACS (orthanc + ohif)
docker compose up -d
docker compose -f docker-compose.pacs.yml up -d
```

## 2. Verify (expected outputs)
```bash
# Orthanc REST (auth enabled) — expect JSON with "Version" and "Name":"Orthanc"
curl -u orthanc:YOUR_ORTHANC_PASS -s http://127.0.0.1:8042/system | python3 -m json.tool | head -8
# DICOM C-STORE port listening (private)
ss -tlnp | grep 4242
# OHIF viewer — expect HTTP 200
curl -fs -o /dev/null -w "%{http_code}\n" http://127.0.0.1:3000/
# ThaiRIS — expect HTTP 200 (login page)
curl -fs -o /dev/null -w "%{http_code}\n" http://127.0.0.1:8085/
```

## 3. NPM host records (NPM UI on 1441409)
| Host | Forward to | WS |
|---|---|---|
| pacs.nuratech.ai | http://orthanc:8042 (or 127.0.0.1:8042) | ON (DICOMweb) |
| viewer.nuratech.ai | http://ohif-viewer:3000 | OFF |
| ris.nuratech.ai | http://thairis:8085 | OFF |

## 3a. VIEWER AT EVERY CLINIC (founder 2026-08-02 — bundle component)
NURA provides a local OHIF viewer at EACH clinic for staff to review images/reports on-site (not just the central viewer.nuratech.ai).
- **North Miami (customer #1)**: clinic-local OHIF instance → Orthanc via DICOMweb (same network; low latency; works if WAN degrades — staff review never depends on the internet link).
- **Little Haiti / Ft. Lauderdale (customers 2–3)**: same pattern per site (local OHIF → central Orthanc over private tunnel, or site-local Orthanc cache when volumes justify).
- **Workflows**: staff review images + reports (radiology reports readable in the viewer side panel); access = clinic staff RBAC (no public exposure; PHI stays within clinic + central PHI boundary).
- **Deployment**: per-site docker-compose (ohif-viewer service, same image + app-config pointing at the site's DICOMweb endpoint), local NPM or LAN-only bind; part of the SaaS bundle delivered by DIV-1.
- **Offline tolerance**: viewer caching for recently viewed studies (local browser cache) — aligns with offline-first doctrine.

## 4. Medisun modality AE registry (enter in orthanc.json DicomModalities + ThaiRIS worklist)
**CURRENT STATE (founder 2026-08-02): ONE (1) GE digital X-ray machine on site at North Miami — it is the FIRST modality to connect. CT/MRI/US/Mammo/DEXA arrive later.**
| Modality | AE Title | IP (clinic VLAN) | Port | Notes |
|---|---|---|---|---|
| **Digital X-ray (GE) — LIVE NOW** | **NURA_NM_XRAY** | <modality IP> | 104 (SCU→4242) | **PRIORITY: C-STORE to NURAORTHANC + MWL via ThaiRIS** |
| CT (≥64-slice) | NURA_NM_CT | <modality IP> | 104 | C-STORE + MWL (when delivered) |
| MRI 1.5T | NURA_NM_MRI | <modality IP> | 104 | C-STORE + MWL (when delivered) |
| Ultrasound | NURA_NM_US | <modality IP> | 104 | C-STORE (when delivered) |
| Mammo (tomosynthesis) | NURA_NM_MAMMO | <modality IP> | 104 | MQSA workflow (when delivered) |
| DEXA | NURA_NM_DEXA | <modality IP> | 104 | C-STORE (when delivered) |

Orthanc AE: **NURAORTHANC** · DICOM port: **4242** (loopback only; modality reaches via private net — add firewall rule for clinic VLAN → 4242).

## 4a. X-RAY FIRST go-live (the product's first customer delivery)
1. Register NURA_NM_XRAY in orthanc.json DicomModalities + ThaiRIS worklist.
2. C-STORE test: storescu from the GE workstation (or dcmtk) → NURAORTHANC:4242 → expect Success.
3. MWL: OpenEMR X-ray order (CPT 71045) → Mirth ORM → ThaiRIS → GE queries MWL → exam performed.
4. Verify end-to-end: image in Orthanc → viewer link in OpenEMR chart (SOP-3) → report → ORU back.
5. This = reference case #1 for sales (Iris) + the anchor for CT/MRI/US/Mammo/DEXA connects.

## 5. C-STORE test (from any modality workstation / dcmtk)
```bash
# one-liner from a machine on the clinic net:
storescu -aet MEDISUN_XRAY -aec NURAORTHANC 127.0.0.1 4242 test.dcm   # (use Orthanc IP on the net)
# expect: Received Store Response, Status: Success
```

## 6. MWL (Phase 2, NUR-49/Meridian)
OpenEMR orders → Mirth HL7 ORM → ThaiRIS worklist → modality queries MWL. Not in this block — wiring via Mirth channels (hermes-mirth-connect skill) after RIS is verified.

## 7. Security notes
- Orthanc auth = REQUIRED (already enabled in orthanc.json) — change the default password before first start.
- 4242 loopback-only; never proxy DICOM via NPM.
- Backups: orthanc-db volume + thairis-db → include in nura-backup.sh (Nightly Encrypted Backup cron).

## 8. OpenEMR tie-in (after RIS/PACS verified)
1. **Orders → MWL**: OpenEMR imaging order (procedure codes: X-ray 71045/CT 74176/MRI 74181/US 76700/Mammo 77067/DEXA 77080) → Mirth channel `ORM^O01` (NURA-IMG-ORDERS) → ThaiRIS worklist → modality queries MWL.
2. **Results → OpenEMR**: ThaiRIS report complete → Mirth `ORU^R01` (NURA-IMG-RESULTS) → OpenEMR lab/imaging results + document attach (PDF report).
3. **Viewer link in chart (SOP-3)**: on study complete, generate tokenized OHIF link → store on the OpenEMR encounter (document reference) → provider clicks `viewer.nuratech.ai/study/<uid>` straight from the chart.
4. **Demographics**: OpenEMR patient → Mirth `ADT^A04/A08` → ThaiRIS (single source of truth = OpenEMR; never reverse).
5. Requires: OpenEMR API creds drop (lane mock→api) + Mirth :8081 deploy (hermes-mirth-connect skill).

## 9. Perfex tie-in (billing/RCM)
1. **Fee sheet → Perfex invoice (SOP-2)**: ThaiRIS/OpenEMR fee sheet (CPT + modifier + provider) → sanitized generic line ("Professional Diagnostic Imaging Services - CPT 74181") → Perfex invoice via bridge (NUR-41, external_ref = openemr:{pid}:{encounter}).
2. **Auth/eligibility tracking**: Perfex custom fields (payer, auth #, status) per imaging order — Tally (Perfex dev) owns; NURA Imaging SaaS division (DIV-1) uses NURA ERP = Perfex for modality-level P&L.
3. **Denials**: denial intelligence (RCM master plan) — imaging denials (missing auth, MQSA attestation) → Midas review queue.
4. PHI rule: NEVER ICD-10/notes/Rx into Perfex — generic billing descriptions only.
