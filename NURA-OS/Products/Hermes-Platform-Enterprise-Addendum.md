# HERMES PLATFORM ARCHITECTURE ADDENDUM — ENTERPRISE SERVICES & PLATFORM COMPONENTS (2026-08-04, founder canonical v1.0)

**The shared enterprise infrastructure used by ALL clinician agents and organizational deployments — the platform services under the Hermes kernel.**

## THE 24 ENTERPRISE SERVICES
1. **Policy Engine** — every request/workflow/tool-call/AI action evaluated against central policies BEFORE execution: authorization · least privilege · state-specific clinical rules · org policies · tool permissions · human-approval requirements · time-based access · device-trust validation · emergency break-glass. (Recommended: OPA · Cedar · Casbin.)
2. **IAM** — centralized authN/authZ for users/agents/devices/services: MFA · SSO · OAuth2 · OIDC · RBAC · ABAC · service accounts · agent identities · device identities · session management.
3. **Secrets Management** — API keys · OAuth secrets · JWT signing keys · TLS certs · DB creds · cloud creds · vendor tokens · encryption keys. (Vault · Infisical · AWS Secrets Manager.)
4. **Feature Flag Service** — controlled deployment without redeploys: AI Scribe · Radiology AI · Voice Agent · Robot Control · Mobile Offline · betas · experimental models.
5. **Skill Registry** — modular packages: name · version · description · dependencies · required tools · required permissions · SAFETY CLASSIFICATION · clinical validation status · digital signature. (EM · Cardio · Radiology · Derm · EMS · ICU · Surgery · Coding · Billing · Compliance.)
6. **Tool Registry** — the approved-integration inventory (OpenEMR · Epic · Oracle Health · athena · eCW · Tebra · NextGen · Mirth · Orthanc · OHIF · ThaiRIS · Twilio · Chatwoot · Perfex · OpenEvidence · PubMed · FDA · CDC · Bluetooth devices): every tool defines version · permissions · auth method · required policies · audit level.
7. **Knowledge Gateway** — all external medical knowledge through a controlled gateway (PubMed · DailyMed · OpenEvidence · ClinicalTrials.gov · FDA · CDC · NIH · WHO · RxNorm · LOINC · SNOMED/UMLS as licensed): caching · citation generation · source verification · rate limiting · provenance · versioning.
8. **Model Router** — the right model per task (GPT→clinical reasoning · Claude→long-form · Gemini→vision · local→offline · biomedical→classification/extraction): criteria = cost · latency · context · privacy · accuracy · availability.
9. **Memory Service** — structured memory across agents: short-term · working · long-term · semantic · episodic · org · clinician — in Postgres/Redis/Qdrant/S3 — with version history · rollback · provenance · encryption · tenant isolation.
10. **Event Bus** — standardized events for everything (PatientCreated · EncounterStarted · NoteDrafted · LabResultReceived · MedicationUpdated · ImagingAvailable · ProviderSigned · CriticalResultDetected · TaskCompleted) over Gateway · MCP · NATS · Redis Streams · RabbitMQ.
11. **Workflow Engine** — multi-step clinical workflows (intake · discharge planning · prior auth · referrals · RPM · CCM · TCM · imaging/lab review): retries · timeouts · compensation · escalation · human approval · audit.
12. **Knowledge Ingestion Pipeline** — download → OCR → cleaning → dedup → chunking → embedding → vectorization → metadata → versioning → publishing; metadata = source · date · version · license · specialty · keywords · confidence.
13. **Observability** — metrics · logs · traces · errors · AI latency · tool usage · queue length · GPU · API performance (OpenTelemetry · Prometheus · Grafana · Loki · Jaeger).
14. **Governance Dashboard** — agent health · active sessions · AI usage · pending approvals · failed workflows · critical alerts · security events · compliance · deployment health.
15. **Cost Management** — tokens · GPU · API charges · storage · bandwidth · compute — per organization/clinician/patient/workflow/department.
16. **Explainability Engine** — every AI response includes: supporting evidence · source citations · confidence · model version · prompt version · tool usage · timestamp. **No unsupported recommendations.**
17. **Clinical Simulation Environment** — synthetic patients/imaging/labs · mock EMRs · simulated devices · DR exercises — **no production patient data.**
18. **Digital Twin Service** — structured clinician profiles: specialty · licensure · certifications · preferred documentation style · enabled skills · approved tools · organization · locations — personalized workflows with tenant isolation.
19. **Device Management** — Windows/macOS/Linux/iOS/Android/tablets/robots/drones/kiosks/medical devices/wearables: enrollment · certificates · remote revocation · health · policy · updates.
20. **Enterprise Provisioning** — automated onboarding: org → tenant → workspace → encryption keys → databases → vector store → device registration → skills → EMR connectors → comms channels → security validation → production.
21. **AI Evaluation Framework** — documentation quality · retrieval accuracy · recommendation acceptance · provider override rate · hallucination detection · latency · workflow completion · satisfaction — continuous improvement WITHOUT exposing PHI.
22. **Enterprise API Layer** — FHIR · HL7 · scheduling · billing · notifications · identity · analytics · reporting · workflow automation · third-party — versioned, backward-compatible.
23. **Backup & DR** — automated backups · PITR · multi-region (where applicable) · encryption at rest/in transit · recovery testing · business continuity.
24. **Platform Principles** — cloud-native · modular · event-driven · API-first · AI-model-agnostic · vendor-neutral where practical · offline-capable · horizontally scalable · zero-trust · tenant-isolated · fully auditable · **a human clinician remains responsible for final clinical decisions and regulated actions.**

## THE REFERENCE ARCHITECTURE
```
NURA Platform
├── Control Plane · Hermes Kernel · IAM · Policy Engine · Secrets
├── AI Gateway · Model Router · Knowledge Gateway
├── Skill Registry · Tool Registry · Event Bus · Workflow Engine
├── Memory Services · Knowledge Ingestion · Observability · Governance Dashboard
├── Cost Management · Explainability · Device Management · Enterprise Provisioning
├── Backup & DR · Enterprise API Layer · AI Evaluation Framework
```

**The design objective: Hermes as a distributed, secure, multi-tenant AI platform — standardized services, governed workflows, strong tenant isolation, human-centered clinical oversight — ready for clinicians, healthcare organizations, and future autonomous systems (Ratchet, drones, the off-world stack).**

## THE NURA MAP
- The Policy Engine + IAM + Secrets = the Cybersecurity spec's spine (zero-trust · RBAC/ABAC · sealed .env → the Vault-class future).
- The Model Router = the MoE chain (already live) · the Knowledge Gateway = the evidence lanes (OpenEvidence/PubMed/FDA — live!) · the Event Bus = the MCP/Redis lanes.
- The Explainability Engine = the clinical skills' citation doctrine · the Simulation Environment = the QA spec's synthetic-data program · the Digital Twin = the SENTINEL/spec profiles.
- The Enterprise Provisioning = the Alexis setup package's automation future.
- **The whole addendum = the shared foundation under the Multi-Agent spec — one platform, many clinicians, governed services, human oversight, boss.**
