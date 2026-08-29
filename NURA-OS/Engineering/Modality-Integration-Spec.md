# Modality Integration Spec — Mammo + DEXA + US → Orthanc PACS + RIS (2026-08-16)

Three purchased units → the NURA imaging chain. **PACS target: `NURAPACS` @ Clinic :4242 (DICOM), DicomWeb `/dicom-web/` (port 8042).**

## 1. The units & their DICOM capabilities (from the vendor docs)
| Unit | Connectivity | Notes |
|---|---|---|
| Hologic Dimensions 3D Mammo (2014, SW 1.11/Win10) | "Advanced Connectivity" license INCLUDED + DICOM send (SW 1.11 supports DICOM SCU + MWL) | Old SW level — verify MWL support at install; tomo series = large files |
| Hologic Horizon A DEXA (2016) | DICOM + **Worklist + Query/Retrieve** (licensed in proposal) | Cleanest DICOM citizen of the three |
| Alpinion X-CUBE 90 Elite (US) | DICOM 3.0 Storage + Worklist (verify license at install) | Confirm MPPS if we want automatic study-status |

## 2. Device-side config (hand this to the install tech)
Every device:
- **Destination AE Title: `NURAPACS`** · Host: the Clinic's DICOM IP · **Port: 4242**
- Modality AE Titles (suggested; must match what's registered in Orthanc):
  - Mammo: `NURAMAMMO`
  - DEXA: `NURADEXA`
  - Ultrasound: `NURAXCUBE`
- Timeout/retry: default · Little-endian explicit for DEXA/US if offered (both fine).

## 3. Server-side (Orthanc)
- Incoming stores on 4242 accepted from these AEs (whitelist mode ON after install validation).
- DicomWeb root `/dicom-web/` for OHIF (`dicomweb` datasource in OHIF).
- Worklist: enable Orthanc worklist plugin; RADRIS orders feed the worklist via the bridge (below).
- Orthanc ChangeType=StableStudy webhook → RADRIS study-status API → OHIF worklist refresh.

## 4. The RIS bridge (RADRIS)
- `POST /api/modality-status` {modality, status, accession} — driven by Orthanc StableStudy events (study complete → status COMPLETE → worklist).
- MPPS (if the X-CUBE supports it) = the automatic route; otherwise the StableStudy hook.

## 5. Acceptance checklist (day of install)
- [ ] `echoscu` (or device ping) → NURAPACS:4242 answers C-ECHO for all three AEs
- [ ] Test store: one series from each device lands in Orthanc Explorer 2 (verify series count, pixel data via OHIF render)
- [ ] Tomo series (mammo) renders in OHIF (large multi-frame — check memory/timeout)
- [ ] DEXA worklist query returns RADRIS orders (MWL end-to-end)
- [ ] Study-complete → RADRIS status flips → OHIF worklist shows the study ready
- [ ] Auth on 8042 + TLS via the Clinic nginx (no plaintext PACS UI exposed)

## 6. Mesh tie-in (from the Meshtastic plan)
- Modality status nodes (`{MOD:CT1,ST:SCANNING}` etc.) → same RADRIS status API → the mesh becomes the room-level status channel (metadata only, never PHI).
