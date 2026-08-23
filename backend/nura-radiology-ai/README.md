# NURA Radiology AI — Architecture & Build Route

**Decision (CTO, 2026-08-23): reconcile-and-wire, not rebuild.**

The greenfield blueprint assumes we need Orthanc + PostgreSQL + Mirth + orchestrator from
scratch. We already run 80% of it. The net-new work is the AI orchestration layer, wired to
the existing stack — plus fixing a few broken integration points that would otherwise make
the AI layer dead on arrival.

## What already exists (deployed, not to be rebuilt)

| Layer | Component | State |
|---|---|---|
| Storage/PACS | Orthanc (`radris-stack-orthanc-1`, Postgres 15 backend) :8042 REST/DICOMweb + :4242 C-STORE | live |
| Interface engine | OIE Mirth 4.6 (`mirth-oie46-mirth-engine-1`) :8445 admin, MLLP :6661→:6663 | live |
| RIS | ThaiRIS (`nura-ris-web` :32790 + `nura-ris-db`) | live |
| Viewer | OHIF :32791 | live, auth broken |
| AI model env | Lab `/opt/radiology-venv` — TorchXRayVision + TotalSegmentator | installed, NOT wired |
| Corpus | `/opt/data/imaging-corpus` (6 Kaggle sets, 21GB, no PHI) | local |
| Categorizer | `orthanc-categorizer.py` → 5-axis category index | live |

## Known integration gaps (fix before wiring AI)

1. **OHIF DICOMweb 401** — nginx strips/doesn't forward Basic auth to Orthanc upstreams;
   the viewer has no working data path.
2. **Mirth MLLP 6665/6666/6667 closed** — described channels (RISPACS_HERMES :6667,
   OPENEMR_HERMES :6666, solis_hermes :6665) are not listening; only 6661/6663 is.
3. **radris-stack-radris-1 crash loop** — Django `staticfiles.json` manifest error.
4. **Mirth admin creds stale** — the sealed `MIRTH_PASS` 401s; founder holds current.
5. **Modality AE registration** — gated on device static IPs (not yet known).

## Build phases

**Phase 0 — Reconcile + fix the base (days, not weeks).**
Fix OHIF auth-forwarding, restore Mirth listeners, fix the RIS crash, register AEs when IPs
land. No point wiring AI to a viewer that can't display and an engine that can't return.

**Phase 1 — AI orchestration core (the net-new build).**
Model registry (Postgres) + FastAPI orchestrator + Orthanc stable-study webhook + DICOM-SR
output + HL7 ORU return via Mirth. This directory is that layer.

**Phase 2 — First model = critical-findings triage.**
TorchXRayVision (already installed) for CXR normal/abnormal + priority flag. Deterministic,
assistive, provider-gated. Triage is the FDA-adjacent lane — NOT autonomous diagnosis.

**Phase 3 — FTO claim chart (parallel with Phase 2).**
Claim chart on Rad AI US 12,354,723 + IBM US 11,244,755 / 12,014,807 / 12,561,963, scoped to
report *generation*. Triage/detection is a different, lower-risk lane.

**Phase 4 — Assistive draft reporting (only after FTO clears).**
Report agent consuming model outputs + priors → DRAFT structured report → radiologist signs.
This is where IP + regulatory risk concentrates, so it is deliberately last.

**Phase 5 — Expand models via the dataset-to-model matrix.**
PE, ICH, pneumothorax, mammo — one at a time, gated on dataset license + eval evidence.

## Clinical gate (non-negotiable)

Every AI output is a **DRAFT — PROVIDER REVIEW REQUIRED** flag. The system does triage,
prioritization, and draft assembly. It never issues a final diagnostic report. This matches
current FDA-cleared radiology AI (assistive/triage), not autonomous interpretation.

## Why this order

- Respects sunk cost — we don't rebuild Orthanc/Mirth.
- Ships clinical value fastest — ER triage saves lives.
- Front-loads regulatory + IP safety — triage first, report-generation last.
- NO-MONEY — TorchXRayVision + TotalSegmentator are free OSS, already installed.

## Directory

```
nura-radiology-ai/
├── README.md                  (this file)
├── docker-compose.yml         AI layer only — does NOT redeclare Orthanc/Mirth
├── orchestrator/
│   ├── Dockerfile
│   ├── main.py                FastAPI: webhook → registry → runner → DICOM-SR + ORU
│   └── requirements.txt
└── model-registry/
    └── schema.sql             models / inferences / evaluations / datasets
```
