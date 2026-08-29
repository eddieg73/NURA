# Evidence & Datasets Registry (2026-08-02 — all lanes probed live)

Machine-readable: data/evidence-datasets.json. Doctrine: verified before use, gated items flagged, no fabricated sources.

## 1. Data sets
- LIVE: nura-docs RAG (470 chunks) · Mem0 (Qdrant) · IDC open-data GCS (proven, sample DICOM on disk) · Moltbook corpus · aesthetics nura-corpus (Bio_ClinicalBERT ONNX)
- GATED: MIMIC (CITI) · CheXpert (license) · RSNA (kaggle) · CQ500/fastMRI (forms) · BRATS/ADNI/DDSM/INbreast/TCGA (access)

## 2. Imaging
- Lane: Orthanc :8042 (running, healthy) · vision cascade · medical-imaging-vision.py
- LIVE: IDC (real DICOM, magic-verified) · Open-i NIH API · Orthanc PACS
- GATED: MIMIC-CXR · CheXpert · RSNA · TCGA

## 3. Labs
- Lane: hermes-laboratory-intelligence · OpenEMR (mock) · Mirth (creds pending)
- LIVE: LOINC via FHIR server (direct site 403s — use fhir.loinc.org) · openFDA device/label lanes
- GATED: Quest/LabCorp/BayCare HL7 via Mirth

## 4. Drugs
- Lane: openFDA MCP (18 tools) LIVE · RxNorm · DailyMed
- LIVE: labels/FAERS/NDC/recalls · RxNorm (lisinopril→29046 verified) · DailyMed 200
- GATED: WENO eRx/EPCS (registration + DEA)

## 5. Vitamins & supplements
- Lane: NIH ODS · PubMed (live)
- LIVE: ODS fact sheets (200) · DSLD label database · PubMed
- NOT ADOPTED: Natural Medicines (subscription — NIH/PubMed cover the lane)

## 6. Repurposed drugs
- Lane: ClinicalTrials.gov APIv2 · ReDO · NCATS
- LIVE: CT.gov v2 (repurposing studies probe OK) · ReDO open oncology list · NCATS new-uses
- GATED: none

## Rules
All findings feed CDS ONLY under provider review · supplement/drug claims tagged [V]/[U] · repurposing = off-label → always evidence-cited + provider decision · no fabricated sources — every lane probed (dates above)
