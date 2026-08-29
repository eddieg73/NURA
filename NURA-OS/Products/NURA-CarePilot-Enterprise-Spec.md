# NURA CarePilot Enterprise — the canonical spec (the founder's reference, 2026-08-19)
The population health & specialty command center. The reference-grade expansion blueprint for the CarePilot (the carepilot.nuratech.ai).

## The 10 modules
1. **Enterprise Command Center** — the financial (the revenue, the leakage, the capitation, the shared savings) + the population health (the RAF gaps, the quality gaps, the utilization) + the clinical (the follow-ups, the discharges, the med-recon).
2. **Medicare Advantage** — the HCC engine (the V28, the suspect/recapture/gap-closure, the MRA/RAF scoring) + the dashboards (the current/target RAF, the open opportunities, the patient/provider/practice ranking) + the conditions (the diabetes/CHF/CKD/COPD/CAD/depression/behavioral/dementia/cancer/obesity/HIV/substance/renal/transplants/frailty/ESRD).
3. **Managed Care Command Center** — the payers (the UHC/Humana/Aetna/Cigna/Florida Blue/Wellcare/Devoted/Alignment/Optimum) + the MLR/cost/utilization/leakage/quality/shared-savings.
4. **Primary Care** — the panels, the AWVs, the chronic tracking, the gap closure, the CCM/RPM/TCM.
5. **Behavioral Health** — the PHQ-9/GAD-7/MDQ/PCL-5, the suicide risk, the med compliance, the telepsych, the CoCM, the BH HCCs.
6. **Radiology** — the RIS/PACS dashboards, the OHIF/Orthanc/ThaiRIS, the critical findings, the incidental tracking (the lung nodules, the breast), the AI-assisted review + the revenue (the by-modality, the TATs).
7. **Surgery** — the pipeline (the lead→consult→approval→pre-op→scheduled→post-op→closed) + the metrics.
8. **Dermatology** — the medical/cosmetic/Mohs, the biopsy tracking, the pathology, the registries (the skin cancer, the chronic).
9. **Aesthetics** — the cash-pay BI (the injectables, the devices, the memberships, the LTV, the channel ROI).
10. **Plastic Surgery** — the pipeline + the analytics.

## The NURA Agents (the multi-agent layer)
The Care Manager (the outreach/gaps) · the RAF Agent (the risk analysis) · the Clinical Agent (the chart review/care plans) · the Radiology Agent (the findings/follow-ups) · the Revenue Agent (the leakage/forecasting) · the Aesthetics Agent (the leads/retention).

## The CTO's stack correction (the spec's the Azure/Mongo → the NURA's the open)
| Spec | NURA |
|---|---|
| Next.js/TypeScript | the FastAPI + the React (the ours) |
| MongoDB Atlas | the PostgreSQL + the Qdrant (the deployed) |
| Azure/AKS | the Hostinger Docker fleet |
| OpenRouter (the GPT-4/Claude/Gemini) | the local Ollama (the 16 models) + the NVIDIA NIM free |
| Azure Key Vault | the sealed vault (the 0600) |

## The match (the spec vs the the built)
✓ the RAF engine (the MSO Coder + the solis pipeline's the 1,570 rows) · ✓ the Radiology (the PACS/RIS/OHIF) · ✓ the Behavioral (the Medisun's the psych lane + the PHQ-9 trends in the OpenEMR MCP) · ✓ the Flutter mobile · ⏳ the dashboards (the CarePilot's the expansion) · ⏳ the Revenue engine (the Perfex's the data)

The reference only.
