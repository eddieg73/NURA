# PRINCIPAL BACKEND PLATFORM ARCHITECT & AI INTEGRATION ENGINEER — the role spec (2026-08-04, founder canonical)

**Position:** Principal Backend Platform Architect & AI Integration Engineer · Alt: Chief Platform Architect / Lead Backend Systems Engineer / Principal Distributed Systems Engineer / Principal AI Infrastructure Engineer
**Reports to:** CTO (Hermes lane) · **Funnel:** the AI hiring manager · **Signer:** the founder

## 1. MISSION
Design, build, and maintain the **Hermes Platform Kernel** — the core operating system for NURA. Hermes owns: AI orchestration · multi-agent runtime · API Gateway · MCP Gateway · authN/authZ · clinical workflow orchestration · event-driven processing · healthcare-system integration · secure inter-service communication · audit logging · knowledge retrieval · workflow automation · tenant isolation. **Every subsystem — OpenEMR, Perfex CRM, Chatwoot, Twilio, Tavus, Orthanc PACS, OHIF Viewer, ThaiRIS, NextGen Connect (Mirth), mobile apps, AI agents — communicates through Hermes.**

## 2. PRIMARY RESPONSIBILITIES
**Platform kernel:** Hermes Core · event bus · workflow engine · service registry · API Gateway · MCP Gateway · agent runtime · scheduling engine · queue processing · background workers · plugin framework · integration framework · identity services · audit services.
**AI orchestration:** multi-agent architecture · tool calling · MCP tools · function calling · model routing · prompt templates · long/short-term memory · vector search · RAG · knowledge graphs · AI evaluation · confidence scoring · clinical safety rules · guardrails · human approval workflows. Models: OpenAI GPT · Anthropic Claude · Gemini · Llama · Qwen · DeepSeek · Ollama · vLLM · RunPod-hosted.
**API Gateway:** REST · GraphQL · gRPC · WebSockets · SSE · OAuth 2.0 · OIDC · JWT · API keys · mTLS · rate limiting · request validation · versioning · tracing · tenant routing.
**MCP Gateway:** secure MCP for OpenEMR · Perfex · Chatwoot · Gmail · Twilio · Google Calendar · Orthanc · ThaiRIS · NextGen Connect · OpenEvidence · PubMed · FDA APIs · AWS · GitHub · PostgreSQL · Redis · Qdrant · Supabase · Stripe · Shopify · QuickBooks.

## 3. EVENT-DRIVEN ARCHITECTURE
Hermes operates as an event-driven platform. Example: Appointment Scheduled → Patient Reminder Created → Twilio SMS → Chatwoot Conversation → Provider Notification → OpenEMR Task → Audit Event. Example 2: Lab Result Received → Mirth → FHIR Normalization → Hermes → AI Analysis → Critical Value Detection → Provider Alert → OpenEMR Draft Note → Patient Follow-up Task.

## 4. HEALTHCARE INTEGRATION
Deep experience: HL7 v2 · FHIR R4 · SMART on FHIR · DICOM · DICOMweb · CDA · CCD · X12 · NCPDP SCRIPT · USCDI. Integrations: OpenEMR · Epic · Cerner · athenahealth · eClinicalWorks · Tebra · Meditech · NextGen · LabCorp · Quest · Surescripts · DoseSpot · Orthanc · OHIF Viewer · ThaiRIS · Mirth.

## 5. DATABASES
PostgreSQL · Redis · Qdrant · Supabase · Amazon S3. Skills: replication · partitioning · index optimization · full-text + vector search · backup/recovery · encryption · data lifecycle.

## 6. MESSAGING & QUEUES
NATS JetStream · RabbitMQ · Kafka · Redis Streams · BullMQ. Capabilities: retries · DLQs · idempotency · exactly-once where practical · workflow compensation · scheduled jobs · distributed locks.

## 7. DEVSECOPS KNOWLEDGE
Docker · Kubernetes · Helm · Terraform · GitHub Actions · ArgoCD · Prometheus · Grafana · Loki · OpenTelemetry · Vault · Traefik · NGINX · WireGuard.

## 8. SECURITY
Zero Trust · RBAC · ABAC · MFA · passkeys · secrets management · mTLS · JWT validation · encryption at rest/in transit · key rotation · immutable audit logs · HIPAA controls · HITRUST alignment · SOC 2 support · ISO 27001 controls.

## 9. LANGUAGES
Required: Go (preferred) · Rust (preferred) · TypeScript · Node.js (NestJS) · Python. Beneficial: PHP (Laravel/OpenEMR) · Java (Mirth customization) · Bash.

## 10. AI FRAMEWORKS
LangGraph · LangChain · DSPy · LlamaIndex · OpenAI Agents SDK · Model Context Protocol · OpenTelemetry for AI · LangSmith · MLflow.

## 11. CLINICAL SAFETY ENGINE
Human approval BEFORE: diagnosis · prescribing · signing · orders. Critical-value escalation · allergy checks · duplicate-medication detection · audit logging · provenance tracking · confidence reporting · evidence citation. **AI recommendations remain advisory unless an authorized clinician confirms them.**

## 12. APIS TO INTEGRATE
Clinical: OpenEvidence · PubMed · DailyMed · RxNorm · SNOMED CT · LOINC · ICD-10-CM · CPT · HCPCS · FDA Drug/Device APIs · ClinicalTrials.gov. Comms: Twilio · Chatwoot · Gmail · Microsoft 365 (opt) · Zoom · Tavus · Daily. Business: Stripe · Shopify · QuickBooks · Xero · HubSpot. Infra: AWS · Cloudflare (opt) · GitHub · Docker Registry · RunPod.

## 13. MONITORING
Distributed tracing · structured logging · metrics · health checks · alerting · workflow dashboards · AI token usage · model/API latency · queue depth · DB performance · error budgets.

## 14. FIRST 90 DAYS
**1-30:** Hermes Core · auth · API Gateway · event bus · Postgres/Redis/Qdrant connected. **31-60:** OpenEMR · Chatwoot · Twilio · Perfex · AI routing · audit engine. **61-90:** Mirth · Orthanc · OHIF · ThaiRIS · Tavus · OpenEvidence · provider dashboard APIs · Flutter support · production deployment prep.

## 15. REQUIRED EXPERIENCE
8+ yrs backend · 5+ yrs distributed systems · 5+ yrs API development · 3+ yrs healthcare interoperability (preferred) · production AI platform · event-driven architecture · multi-tenant SaaS · HIPAA-regulated systems.

## 16. RECOMMENDED CERTIFICATIONS
AWS SA-Professional · AWS Security Specialty · CKA · CKS · Terraform Associate · RHCE · CCNP Enterprise/Security · CISSP/CCSP · HL7 FHIR certification · ISO 27001 Lead Implementer. Certs ≠ ability — the exam decides.

## 17. HIRING ASSESSMENT (the gate)
Build a working prototype that: authenticates OAuth 2.0/OIDC · exposes a versioned API Gateway · routes events through an event bus · integrates a mock OpenEMR FHIR endpoint · connects Redis + PostgreSQL · stores embeddings in Qdrant · executes a LangGraph AI workflow · calls an MCP tool · produces a complete audit trail · demonstrates retry logic, idempotency, and observability. **Evaluation: architecture, security, resilience, code quality, and explaining design tradeoffs — not just whether the demo works.**

**Founder note (08-04):** with this role, the DevSecOps engineer, and the Flutter architect, three foundational pillars are covered. The next spec = the Senior Clinical Interoperability Engineer (HL7/FHIR, Mirth, OpenEMR, Orthanc, OHIF, ThaiRIS, HIE, e-prescribing) — the bridge that brings the healthcare ecosystem into Hermes — critical for production deployment.
