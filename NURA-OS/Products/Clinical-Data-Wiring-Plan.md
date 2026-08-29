# Clinical Data Wiring Plan — wire everything, cross-reference everything

**Date:** 2026-08-19 · **Author:** Atlas (Paperclip CEO) · **Directive:** wire radiology (PACS/DICOM + imaging corpus), labs (lab-intake + trends), every specialty's datasets; cross-reference labs ↔ imaging ↔ diagnoses ↔ HCC; define the schema/linking design.
**Governance inherited from:** Medical-Data-API-MCP-Dataset-Catalog (governance rules §1, status labels §2) and hermes-emh-clinical-skill-architecture (clinical event taxonomy, draft-only doctrine). Research datasets ≠ point-of-care authorities. No PHI outside governed lanes.

---

## 1. Current state (live lanes, verified)

| Lane | Live today | Gated/pending |
|---|---|---|
| PACS | Orthanc :8042 (DICOMweb QIDO/WADO/STOW, HttpWebhooks → n8n, OnStoredInstance → wet-read gateway) · OHIF viewer · ThaiRIS bilingual worklist | — |
| Wet-read | scripts/wet-read-gateway.py (pydicom → windowing → vision cascade → structured impression, draft-only + STAT flags) | production reads |
| Labs | lab-intake-interpreter cron (Med42 interpretation) · hermes-laboratory-intelligence (lab-review) · LOINC via fhir.loinc.org | Quest/LabCorp/BayCare HL7 via Mirth (creds pending) |
| EMR | OpenEMR MCP (20 tools) — the clinical spine · Mirth/OIE HL7 bridge | — |
| Coding | MSO Coder (RAF/HCC v28) + coding agent (nura-coding-agent) | — |
| Corpus | 6 Kaggle imaging sets (RSNA Abdominal Trauma, CQ500, etc. per Orthanc-ThaiRIS-WetRead-Plan) · Vision/Lab catalog (UMIE, CheXmask, MIMIC-CXR, Symile-MIMIC, MIMIC-IV, NHANES, eICU) · 6 B2 buckets | MIMIC CITI credential · kaggle.json · CheXpert license |
| Models | Local Ollama 16 models (med42/meditron/qwen3) · Kaggle fine-tune lane · Bio_ClinicalBERT ONNX (aesthetics precedent) | — |
| Knowledge | Qdrant nura-docs RAG · PubMed/openFDA/CDC/BioPortal MCP lanes | — |

## 2. Target architecture — one spine, four wires, one xref layer

```
DICOM sources (modalities, devices)          HL7 ORU (Quest/LabCorp/BayCare, Mirth)
        │                                            │
        ▼                                            ▼
  Orthanc PACS (DICOMweb)                    OpenEMR (observations, LOINC)
   ├─ OHIF / ThaiRIS (humans)                └─ lab-intake-interpreter cron (Med42)
   ├─ wet-read gateway (draft impressions)        └─ lab-trend analytics
   ├─ SR/SEG AI sidecars (never overwrite original)
   └─ imaging corpus → fine-tune lane (Kaggle/Lab)
        │                                            │
        └──────────────┬─────────────────────────────┘
                       ▼
        CLINICAL XREF LAYER (duckdb xref + Qdrant vectors)
        links: patient → encounter → orders → observations (LOINC)
               → studies (DICOM UIDs) → conditions (ICD-10/SNOMED)
               → HCC (MSO Coder RAF v28) → provenance
                       │
        ┌──────────────┼──────────────────┐
        ▼              ▼                  ▼
   Specialty lanes   CDS / EMH lanes    MSO Coder + coding agent
   (derm/optho/      (differential,     (HCC candidates, RAF
    cardio/path)      escalation)        evidence capture)
```

## 3. The four wires

### 3.1 Radiology wire (PACS/DICOM + imaging corpus)
- **Production path:** modality → Orthanc C-STORE/DICOMweb → (a) OHIF/ThaiRIS for humans, (b) webhook → wet-read gateway → vision cascade → **draft** impression {normal/abnormal/confidence/STAT} → provider review → chart-ready.
- **AI-output discipline (catalog §8):** AI results stored as DICOM **SR/SEG/secondary capture sidecars**, original DICOM + metadata preserved, model/weights/preprocessing/threshold/series/timestamp recorded. Radiologist final.
- **Corpus path:** the 6 Kaggle sets + UMIE/CheXmask/MIMIC-CXR (gated) → Lab node (32GB) → Swin/ViT fine-tune → ONNX → TorchServe (aesthetics pipeline precedent) → PACS annotation sidecar module.
- **Linking keys:** StudyInstanceUID, SeriesInstanceUID, accession number, patient_id, modality, body-part (RadLex).

### 3.2 Lab wire (intake + trends)
- **Intake:** HL7 ORU via Mirth → OpenEMR observations → lab-intake-interpreter cron: LOINC normalization, UCUM validation, local reference ranges (age/sex/pregnancy/specimen/method-aware), delta checks, critical-value rules, hemolysis flags → lab-review skill output (normal/abnormal/critical/indeterminate + trend).
- **Trends:** per-patient time series per LOINC → trend arrows, rate-of-change alerts, duplicate/impossible-value detection → feeds longitudinal patient memory.
- **Linking keys:** LOINC code + specimen + collection timestamp + accession; mapped to encounter_id and order accession in OpenEMR.

### 3.3 Specialty wires (datasets per lane)
| Specialty | Corpus (per Vision/Lab catalog) | Live lane |
|---|---|---|
| Dermatology | HAM10000 · ISIC archive | aesthetics/derm skill lane |
| Ophthalmology | EyePACS · APTOS (DR screening) | RPM-adjacent opportunity |
| Cardiology | PTB-XL (21K ECGs) · MIT-BIH · MIMIC-IV-Waveform | ECG classifiers, telemetry |
| Pathology | Camelyon16/17 · TCGA slides | future lab lane (slide AI) |
| Radiology NLP | OpenI · IU X-Ray (report↔image pairs) | report-generation fusion |
| ICU/critical care | eICU · MIMIC-IV · Symile-MIMIC | deterioration models |
| Neuro | BraTS · fastMRI · IXI | future MR lane |
| Population | NHANES · CDC MCP (keyless live) | reference ranges, public-health lane |

Every specialty dataset registers in the dataset-governance registry with license/DUA/commercial-use/PHI status **before** ingestion (catalog §19 checklist).

## 4. Cross-reference strategy — the value engine

The plan's purpose: make **labs ↔ imaging ↔ diagnoses ↔ HCC** queryable in one join, so CDS has full context and the coder has evidence.

| Link | Rule | Product output |
|---|---|---|
| **Labs → Imaging** | Abnormal/critical lab (e.g., troponin, D-dimer, A1c) + open order gap → flag missing/indicated study | CDS nudge: "A1c 9.2 — retinal exam not ordered in 12 mo" |
| **Imaging → Diagnoses** | Wet-read finding (SNOMED candidates from impression) → suggest condition candidates | Draft problem-list additions for provider |
| **Diagnoses → Labs** | Chronic condition (diabetes, CKD) → gap check on monitoring labs (A1c, eGFR, microalbumin) | HEDIS/quality gap alerts |
| **Diagnoses → HCC** | ICD-10 condition → MSO Coder RAF v28 candidate + evidence pointers (note/lab/study) | Coding candidates with provenance |
| **Labs → Diagnoses** | Trend anomalies (e.g., rising creatinine) → differential candidates with uncertainty | Ranked differential (draft) |
| **Labs + Imaging → Longitudinal** | All links accumulate per patient → Symile-MIMIC-style fusion model training | Deterioration/readmission models (research) |

**Fusion training:** Symile-MIMIC (11,622 admissions: CXR + ECG + 50 labs) is the goldmine for the lab↔imaging↔diagnosis joint model — credentialed PhysioNet access, free registration.

## 5. Schema / linking design

### 5.1 Identity spine (canonical keys)
- `patient_id` — OpenEMR pid (canonical). `encounter_id` — OpenEMR encounter.
- Labs: `loinc_code` + `accession_number` + `observation_ts`.
- Imaging: `study_instance_uid` + `series_instance_uid` + `accession_number`.
- Conditions: `icd10_code` (+ `snomed_code` where mapped). HCC: `hcc_code` (v28) via MSO Coder.
- Provenance: source_system + retrieval/model version + timestamp on **every** row (catalog §1 rule 8).

### 5.2 Xref table (duckdb — analytics + fast joins; no PHI in derived research copies)

```sql
CREATE TABLE xref_clinical (
  xref_id         UUID PRIMARY KEY,
  patient_id      TEXT,               -- OpenEMR pid
  encounter_id    TEXT,
  accession       TEXT,               -- order accession (labs + imaging share)
  loinc_code      TEXT,               -- labs
  obs_value       TEXT, obs_ts TIMESTAMP,
  study_uid       TEXT, series_uid TEXT, modality TEXT,  -- imaging
  icd10_code      TEXT, snomed_code TEXT,                -- diagnoses
  hcc_code        TEXT, raf_version  TEXT,               -- MSO Coder v28
  source_system   TEXT, provenance   JSON, created_ts TIMESTAMP
);
CREATE INDEX idx_patient ON xref_clinical(patient_id, obs_ts);
CREATE INDEX idx_loinc   ON xref_clinical(loinc_code);
CREATE INDEX idx_study   ON xref_clinical(study_uid);
CREATE INDEX idx_hcc     ON xref_clinical(hcc_code);
```

### 5.3 Envelope contract
Every clinical output reuses the EMH skill architecture envelope: normal / abnormal / critical / indeterminate findings, ranked differential, must-not-miss, missing info, confidence, evidence + provenance, required clinician action, **human approval status**. Draft ≠ decided (catalog §1 rule 7).

### 5.4 Storage map (6 B2 buckets — proposed canonical mapping)
| # | Bucket | Contents |
|---|---|---|
| 1 | `imaging-raw` | DICOM originals (immutable, lifecycle to deep archive) |
| 2 | `imaging-derived` | SR/SEG sidecars, annotations, rendered previews |
| 3 | `labs-hl7` | HL7 messages (encrypted at rest), parsed JSON |
| 4 | `models-artifacts` | ONNX/GGUF weights, fine-tune checkpoints, configs |
| 5 | `research-datasets` | De-identified corpora (DUA-compliant), never PHI |
| 6 | `backups` | OpenEMR DB, Orthanc metadata, duckdb xref snapshots |

PHI policy: PHI lives only in OpenEMR/Orthanc/Mirth production lanes (encrypted, local). Research copies are de-identified; xref analytics can run PHI-scoped in production duckdb, but anything shipped to the corpus lane is stripped.

## 6. Build order (phases)

- **P1 — Identity + xref skeleton:** OpenEMR pid mapping, accession alignment, duckdb xref live, provenance columns. *Output: first joins (single patient's labs+studies+dx).*
- **P2 — Lab wire production:** Mirth HL7 creds → ORU live → lab-intake-interpreter on real results → trends dashboard + critical-value escalation. *Output: lab-review skill on live data.*
- **P3 — Imaging sidecars + finding mapping:** wet-read impressions → SNOMED candidates → SR sidecars to Orthanc. *Output: imaging→dx link populated.*
- **P4 — HCC cross-ref live:** MSO Coder over xref (dx + evidence pointers) → coding agent candidates with provenance. *Output: labs/imaging evidence attached to every HCC candidate.*
- **P5 — Specialty lanes:** corpus gates (CITI/kaggle.json/CheXpert) cleared → fine-tune pipeline → annotation module. *Output: first NURA fine-tune on the 6-modality corpus.*
- **P6 — Fusion:** Symile-MIMIC joint model (research lane only) → deterioration models → evaluation harness. *Output: cross-modal CDS v1.*

## 7. Governance (non-negotiables)

1. Research ≠ point-of-care (catalog §1.1) — no corpus-derived model decides anything at bedside.
2. Provider final authority — every wire terminates at a provider review gate (EMH-Autonomy-Ladder).
3. Provenance on every row — source, model, prompt, timestamp (catalog §1.8).
4. No PHI in research notes, logs, or buckets 5 — enforced at write time.
5. Local reference ranges before any public interval (catalog §1.5).
6. Kill switches on every lane; webhook failures fail closed.

---
*Inventory references: Products/Medical-Data-API-MCP-Dataset-Catalog.md · Orthanc-ThaiRIS-WetRead-Plan.md · Engineering/Vision-Lab-Dataset-Catalog.md · Evidence-Datasets.md · Clinical/OpenEMR-Structure-Mapping.md · Products/EMH-Autonomy-Ladder.md (companion).*
