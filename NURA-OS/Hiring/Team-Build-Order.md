# NURA TEAM BUILD ORDER + ORGANIZATIONAL STRUCTURE (2026-08-04)

**Doctrine:** each role enables the next · the AI hiring manager runs the funnels · the founder signs · the practical exam gates every hire · agents fill gaps until humans land (the Lattice runs regardless).

## THE BUILD ORDER (15 roles — why this sequence)
1. **Senior Backend Platform Architect & AI Integration Engineer** — the Hermes kernel (API/MCP gateways, auth, multi-tenancy, RBAC/ABAC, audit, event bus, LangGraph, AI routing, Postgres/Redis/Qdrant/Supabase, workers, versioning, OTel). Go/Rust · Node/NestJS · Laravel · Docker/K8s · Kafka/NATS · gRPC/REST/GraphQL · OAuth2/OIDC/JWT · FHIR/HL7. THE SPINE — every other role depends on it.
2. **Senior AI/ML Engineer** — Hermes' intelligence: LLM orchestration, prompts, agents, multi-agent coordination, clinical RAG, vector DBs, OpenEvidence/PubMed/FDA, tool/function calling, memory, evaluation, hallucination reduction, fine-tuning, guardrails. LangGraph · DSPy · OpenAI/Anthropic/Gemini · Ollama/vLLM · HF · MLflow/LangSmith.
3. **Clinical Interoperability Engineer** — the hospital integration specialist: Mirth/NextGen, HL7/FHIR/DICOM/DICOMweb, PACS/RIS/LIS/HIE, OpenEMR interfaces, Epic/Cerner/athenahealth/eClinicalWorks/Tebra/Meditech, LabCorp/Quest. ADT/ORM/ORU/SIU/CCD/CDA/USCDI.
4. **DevSecOps / Infrastructure Engineer** — VPS/Docker/K8s/VPN/reverse proxy/monitoring/logging/secrets/firewalls/HA/DR/DNS/certs (the RHEU spec).
5. **Flutter Mobile Architect** — the clinician app (the completed spec).
6. **Frontend Web Architect** — provider dashboard · patient portal · admin portal · Paperclip UI · Hermes dashboard · analytics · real-time. React/Next.js/TypeScript/Tailwind/TanStack Query/WebSockets/FHIR UI.
7. **UI/UX Healthcare Designer** — emergency medicine/ICU/EMS/population health/telemedicine/accessibility/HIG/Material — cuts documentation time, drives adoption.
8. **QA Automation Engineer** — Cypress/Playwright/Flutter/API/load/security regression/clinical workflow validation.
9. **Cybersecurity Engineer** — HIPAA/HITRUST/SOC 2/ISO 27001, pentest, vuln mgmt, incident response, WAF/SIEM/EDR, threat hunting.
10. **Database Architect** — Postgres/Redis/Qdrant, modeling, replication, partitioning, backups, tuning, analytics.
11. **SRE** — uptime, capacity, SLAs/SLOs, observability, incident response, scaling, release reliability.
12. **AI Data Engineer** — ETL, medical datasets, normalization, feature engineering, RAG ingestion, embeddings, knowledge graphs, data quality.
13. **Healthcare Compliance Engineer** — HIPAA controls, audit logging, FDA software documentation, clinical safety, risk mgmt, privacy reviews, vendor BAAs, compliance evidence.
14. **Product Manager (Clinical)** — clinical background, translates provider workflows into engineering requirements.
15. **Technical Writer** — API docs, deployment guides, architecture docs, SOPs, user manuals, developer docs, regulatory docs.

## THE ORGANIZATIONAL STRUCTURE
```
CEO / FOUNDER
├── CTO (Hermes — tech/ops/IP)
├── Chief Medical Officer
├── VP AI Engineering ── AI Engineers · ML Engineers · Data Engineers
├── VP Platform Engineering ── Backend · DevSecOps · SRE · Database
├── VP Mobile ── Flutter · iOS · Android
├── VP Web ── React · UX/UI · Frontend QA
├── Director of Clinical Interoperability ── HL7/FHIR · Mirth · PACS/RIS · EMR Integrations
├── Director of Security & Compliance ── Security Engineering · Compliance · Risk
└── QA & Release Engineering
```

## THE CURRENT SEAT MAP (who's in what today)
| Role | Seat |
|---|---|
| Backend Platform Architect (#1) | **HERMES (acting) — the spine is running; a human backup = the funnel's first hire** |
| AI/ML Engineer (#2) | Hermes + the MoE lanes (the agent stack) |
| Clinical Interop (#3) | Hermes + the Mirth/OpenEMR lanes (JARVIS assistive) |
| DevSecOps (#4) | Hermes (RHEU) |
| Flutter (#5) | Amrit (the spec = the bar) |
| CRM | Oussama (VP CRM — the Perfex lane) |
| Content | Jade (the content ops partner) |
| Frontend/UX/QA/Security/DB/SRE/Data/Compliance/PM/Writer | agents + the funnels (as the revenue gates clear) |

## THE NEXT DOCUMENT
The Senior Backend Platform Architect & AI Integration Engineer spec (role #1) — the Hermes kernel owner — the highest-value spec because every other role's work flows through the platform it builds.
