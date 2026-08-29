# Imaging QA Test Plan — DICOM ingest · HL7 channels · OHIF retrieval

Owner: NURA Imaging & Interop Engineer · Status: DICOM ingest **EXECUTED + PASS
(2026-08-19)**; HL7 + OHIF retrieval **documented, gated on the blockers below**.
Doctrine: non-PHI synthetic fixtures only · passive probes before active sends ·
leave-no-residue (QA studies deleted, statistics re-verified at 0) · every step
records its evidence (HTTP code + JSON output).

## 0. Prerequisites (one-time)

```bash
export SSHCMD="ssh -F /opt/data/profiles/nura/home/.ssh/config \
  -i /opt/data/profiles/nura/home/.ssh/id_nura_clean"
# QA venv (already built): /opt/data/venvs/imaging-qa  (pydicom 3.0.2, pynetdicom 3.0.4, numpy)
# Ingest script (already built): /opt/data/scripts/qa_dicom_ingest.py
```

## 1. DICOM ingest test — EXECUTED, PASS (2026-08-19)

Non-PHI: the fixture is a synthetic 64×64 CR with PatientName `QA^SYNTHETIC`,
PatientID `NURATEST-0001`, StudyDescription `NURA-QA-SYNTHETIC` — no real
person, no real acquisition.

Procedure (repeatable):
1. **Tunnel** (C-STORE stays off the public interface):
   `$SSHCMD -L 10424:127.0.0.1:4242 -N clinic &` — record the pid, kill after.
2. **Send** (simulates the NURAMAMMO modality AE):
   `/opt/data/venvs/imaging-qa/bin/python /opt/data/scripts/qa_dicom_ingest.py 127.0.0.1 10424`
   → PASS = `C-STORE status: 0x0000` + `QA-STORE-OK`.
3. **Verify in the PACS** (on the Clinic):
   ```bash
   curl -s -u nuraadmin:<pass> http://127.0.0.1:8042/statistics        # 1/1/1/1
   curl -s -u nuraadmin:<pass> http://127.0.0.1:8042/studies           # 1 study id
   curl -s -u nuraadmin:<pass> 'http://127.0.0.1:8042/dicom-web/studies?limit=5'
   #   → the QIDO-RS JSON carries QA^SYNTHETIC / NURATEST-0001 (DICOMweb lane)
   ```
4. **WADO-RS metadata** (the retrieval the viewer uses):
   `curl -s -u nuraadmin:<pass> -o /dev/null -w '%{http_code}\n' \
   'http://127.0.0.1:8042/dicom-web/studies/<study-uid>/series'` → **200**.
5. **Cleanup — leave no residue:**
   `curl -s -X DELETE -u nuraadmin:<pass> http://127.0.0.1:8042/studies/<id>`
   then re-probe statistics → **0/0/0/0**.
6. Kill the tunnel.

2026-08-19 run: PASS at every step; PACS restored to 0 studies.

## 2. HL7 channel test — DOCUMENTED, gated (do NOT run blind)

Gate: sending an HL7 frame into a listener whose channel transformers are
unknown can insert junk rows into prod OpenEMR/ThaiRIS. **Active sends are
blocked until the Mirth admin password is recovered from the founder** (the
sealed `MIRTH_PASS` in the profile .env currently 401s) and the channel map is
confirmed via `GET /api/channels`.

Step 1 — passive listener probe (safe, run anytime):
```bash
$SSHCMD clinic 'docker exec mirth-oie46-mirth-engine-1 bash -c \
"timeout 3 bash -c \"exec 3<>/dev/tcp/127.0.0.1/6666\" 2>/dev/null && echo 6666-OPEN || echo 6666-CLOSED"'
# known today: 6661 OPEN (host :6663) · 6665/6666/6667 CLOSED
```
Step 2 — recover admin auth, then inventory:
```bash
curl -sk -u <admin> -H 'X-Requested-With: OpenAPI' https://127.0.0.1:8445/api/channels
#   → confirm which channel owns which MLLP port + deployed state
```
Step 3 — the end-to-end send (only against a confirmed NON-PROD sink; the
`hermes-hl7-simulator` pattern):
```bash
# fixture: synthetic ADT^A01, patient NURATEST-0001 (same synthetic identity)
$SSHCMD clinic 'docker exec mirth-oie46-mirth-engine-1 bash -c ...'   # or
python send_mllp.py <port> fixtures/adt_a01_synthetic.hl7             # expect MSA|AA
```
Pass = ACK `MSA|AA` + the sink log shows the payload + the channel VALID +
listener state confirmed in `/api/channels/statuses`. No ACK / closed port =
FAIL with the evidence attached.

## 3. OHIF retrieval test — DOCUMENTED, currently FAILS at the nginx layer

Blocked by: nginx returns **401** on `/dicom-web-pacs/` and `/dicom-web-legacy/`
even with the Basic header forwarded (direct Orthanc DICOMweb = 200 with the
same creds). The viewer UI serves (200) but has no data path.

Procedure once the nginx auth-forwarding is fixed:
1. Re-probe the routes:
   ```bash
   curl -sk -u nuraadmin:<pass> -o /dev/null -w '%{http_code}\n' \
     https://127.0.0.1/dicom-web-legacy/studies        # expect 200 (→ orthanc-pacs)
   curl -sk -o /dev/null -w '%{http_code}\n' https://127.0.0.1/dicom-web-pacs/studies
   ```
2. Browser pass (the real UI/UX check): load the viewer (pacs/viewer.nuratech.ai,
   or :32791), confirm the study list renders, open the QA study (if kept) —
   otherwise repeat §1 ingest and keep the study while testing, delete after.
3. Decide the default datasource target (today `pacs` → radris-stack Orthanc,
   `legacy` → orthanc-pacs) and pin it in `app-config.js` + the viewer.conf
   proxy so ONE production PACS backs the viewer.
Pass = QIDO/WADO 200 through the public path + a study renders in the browser.

## Acceptance matrix

| Test | Fixture | Pass criterion | State |
|---|---|---|---|
| DICOM ingest | synthetic CR `QA^SYNTHETIC` | C-STORE 0x0000 · stats 1/1/1/1 · QIDO 200 · WADO 200 · cleanup→0 | **PASS (run 2026-08-19)** |
| HL7 channel | synthetic ADT^A01 | MLLP connect · MSA|AA · sink log · channel VALID | **GATED** (admin creds + channel map) |
| OHIF retrieval | the QA study | DICOMweb 200 via nginx · study renders in browser | **BLOCKED** (nginx 401) |

## Residue check (run after every test session)

```bash
curl -s -u nuraadmin:<pass> http://127.0.0.1:8042/statistics   # must read 0/0/0/0
$SSHCMD clinic 'ss -tlnp | grep 6663'                          # only the known listener
```
