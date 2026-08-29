# NURATECH.ai TECHNOLOGY MASTER PLAN — Hermes Agent: Agentic RCM Platform (2026-08-02)
CTO-authored plan (Osama Ben Akka — platform · Amrit Raj — AI/ML · Andrw — IT infra · Voice/PBX Mgr). Encoded canon + deltas.

## 1. Business context
Full-risk Medicare Advantage practice (primary payer: Solis HMO). Clinics: North Miami · Little Haiti · Fort Lauderdale (~2 mo). 285 MA patients · RAF 1.27 · PMPM $360 · nutrition giveback $60 · revenue/patient $300. Service lines: Primary Care · Psychiatry (NeuroStar TMS) · Radiology (X-ray). 5-yr potential: $12M+/yr scaled.

## 2. Platform essence
Hermes = digital RCM organization in software: chart review → diagnosis extraction → ICD-10 recs → CMS-HCC risk scores → RAF optimization → denial prevention → billing automation → patient comms → imaging integration. **ALL automated decisions require Billing Manager approval — AI-assisted, not autonomous.**

## 3. Architecture layers
- Clinical: EMM EMR · hospital HIE · MyChart · Operational: GoHighLevel CRM · Perfex ERP · Imaging: Orthanc PACS · OHIF Viewer · Comms: SMS/Email/FB/IG/LinkedIn · Voice: PBX + SIP · AI: Mac Studio M3 Ultra (Ollama, ClinicalBERT, GatorTron, embeddings, OCR) + external (OpenAI, Claude, Perplexity) · Data: Supabase Postgres + pgvector.
- Orchestration: Claude MCP Server (agent orchestration, tool/model routing, workflows).

## 4. Agents (9)
Connector · Chart Retrieval · Diagnosis Discovery · Coding · HCC/RAF · Denial Intelligence · Communication · Voice · Memory.

## 5. Deterministic rules engine (NON-NEGOTIABLE)
CMS risk adjustment is computed independently of LLM outputs: ICD-10→HCC mapping · CMS hierarchy · exclusion/interaction rules · RAF calc · full trace output. (Matches compliant-coding doctrine.)

## 6. Workflow
Chart retrieval → diagnosis extraction → ICD-10 → HCC → RAF → denial risk → **Billing Manager review → claim release** (audit-logged).

## 7. Data (Supabase Postgres + pgvector)
patients · encounters · documents · diagnosis_candidates · icd10_codes · hcc_mappings · raf_scores · denial_predictions · billing_tasks · approvals · agent_runs · audit_logs. RAG memory: clinical history, coding decisions, payer policies, denial outcomes, documentation patterns, comms records.

## 8. Infra/DevOps/Security
Docker (+optional K8s) · GitHub Actions · Terraform · Prometheus/Grafana/OpenTelemetry/Sentry · Keycloak/Auth0 · RBAC · encrypted storage · API authN · audit + PHI access tracking. Microservices (16): gateway, identity, connectors, normalization, retrieval, embeddings, memory, diagnosis-discovery, coding-recommendation, rules-engine, denial-intelligence, communications, voice, workflow, audit, evaluation. Repo layout /openclaw with apps/services/packages/infra/docs.

## 9. Phases
P1 core infra+DB · P2 EMR+PACS integration · P3 AI coding agents · P4 comms+voice · P5 denial intelligence + RAF optimization. Environments: dev → integration → simulation (de-identified) → staging → prod (supervised) + local-fallback (local inference only).

## 10. HIE targets
Jackson Memorial · University of Miami · UM Health System · North Shore Medical · Broward Health · Memorial Healthcare — discharge summaries, encounters, consults, external imaging.

## 11. Diagram pack
docs/diagrams/rcm-architecture-pack.html (12 diagrams: overview, RCM workflow, agents, local AI, data, microservices, comms, voice, imaging, HIE, environments, security).

## 12. DELTAS vs current canon (resolve with founder)
1. **Supabase/pgvector vs Qdrant-local doctrine** — plan mandates Supabase Postgres+pgvector; standing = Qdrant local forever (zero-credit, PHI-safe). Recommend: Qdrant remains live memory; Supabase adopted for the RCM product DB (new domain, not the Hermes memory lane).
2. **Mac Studio M3 Ultra local AI** — NEW compute asset (vs Lab KVM8). Aligns with offline-first; decide placement of ClinicalBERT/GatorTron (fine-tune targets: our Bio_ClinicalBERT pipeline).
3. **Claude MCP orchestration vs Hermes Agent** — platform named "Hermes agent"; orchestration layer = Claude MCP server. We ARE Hermes (Agent by Nous Research); MCP lanes already wired. Adopt the concept; keep our gateway.
4. **OpenAI/Anthropic/Perplexity providers vs cost doctrine** — free lanes first, DeepSeek cheapest paid; OpenAI credits exhausted. External providers = optional premium lanes behind quality gate.
5. **GHL as comms hub vs Chatwoot** — plan centers GHL (creds pending); Chatwoot lane already live. Dual-track until GHL creds land.
6. Repo /openclaw name vs our /opt/data layout — internal naming only; keep ours.

## Owners
Board: Atlas (CEO) oversees · Orion (CTO) owns plan + NUR-56 · Midas (RCM) owns Billing-Manager gate · Tally (Perfex) · Florence (OpenEMR) · Meridian/Meridian2 (Mirth/HIE) · Echo (voice/PBX) · Frame (PACS) · Iris (brand) — per NUR-57/55/41/42/43 directives.
