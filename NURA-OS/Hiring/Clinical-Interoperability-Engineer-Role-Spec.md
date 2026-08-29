# PRINCIPAL NEXTGEN CONNECT ARCHITECT & CLINICAL INTEROPERABILITY ENGINEER — the role spec (2026-08-04, founder canonical)

**Position:** Principal NextGen Connect Architect & Clinical Interoperability Engineer
**Alt:** Lead Mirth Connect Integration Architect / Principal HL7-FHIR Interface Engineer / Director of Clinical Interoperability Engineering / Senior EMR Integration and HIE Architect / **NURA Clinical Sidecar Integration Lead**
**Reports to:** Director of Clinical Interoperability · **Funnel:** the AI hiring manager · **Signer:** the founder

## 1. POSITION MISSION
Design, build, secure, test, deploy, and maintain the interoperability layer connecting NURA, OpenEMR, Perfex CRM, and external EMRs — the **NURA Clinical Sidecar**: a background clinical documentation + interoperability application. Providers: work inside the NURA app · retrieve patient/encounter context from the org's EMR · chart in NURA · OpenEMR = the internal clinical record + staging · Perfex = operational workflows · review + sign · convert the approved doc to the destination format · upload into the destination EMR · confirm acceptance · full audit + reconciliation. **OpenEMR exposes REST + FHIR APIs — FHIR-based integration, never direct DB writes.**

## 2. PRODUCT: THE NURA CLINICAL SIDECAR
EMR-agnostic workspace alongside (not a replacement for) the org's EMR. Flow: Destination EMR → patient/schedule/encounter context → NextGen Connect → Hermes kernel → NURA apps → provider charts/reviews/signs → OpenEMR (authoritative NURA record) → NextGen transforms → destination EMR → ACK + reconciliation. **Core principle: the provider never sees HL7/FHIR/vendor APIs/retry queues — only: Patient matched → Encounter opened → In progress → Ready for review → Signed → Submitted → Accepted → Reconciliation complete.**

## 3. SYSTEM-OF-RECORD MODEL
| Data | Authoritative |
|---|---|
| Draft NURA note | NURA/OpenEMR |
| Final signed NURA note | OpenEMR (immutable signed version) |
| External org chart | destination EMR after confirmed acceptance |
| Patient identity | NURA Master Patient Index |
| Provider identity | NURA Provider Directory |
| Operational tasks | Perfex / Hermes Task Service |
| Patient communication | Chatwoot (approved chart extraction) |
| Interface messages | NextGen Connect message store |
| Audit history | Hermes append-only audit |
| Uploaded PDF/CDA | encrypted storage + destination reference |
| Integration status | NURA reconciliation service |

## 4. REQUIRED ARCHITECTURAL OUTCOMES — connect to: OpenEMR · Epic · Oracle Health/Cerner · athenahealth · eClinicalWorks · NextGen Enterprise · Tebra · AdvancedMD · MEDITECH · Veradigm/Allscripts · Greenway · Practice Fusion · DrChrono · CareCloud · CPSI/TruBridge · Netsmart · PointClickCare · MatrixCare · VA interfaces (where contracted) · state/regional HIEs · labs · radiology · pharmacy/e-prescribing · claims clearinghouses · document systems. Each may need: FHIR R4 · SMART · vendor REST · SOAP · HL7 v2 · C-CDA · XDS/XDS-I · Direct Secure Messaging · SFTP · secure file drop · vendor document-import API · MDM · ORU · interface-engine connection · **RPA only as a temporary last resort** · manual upload fallback under controlled policy. **Never assume every EMR speaks the same protocol.**

## 5. NEXTGEN CONNECT OWNERSHIP
**Platform:** install · config · DB selection · channel architecture · env separation · HA · clustering · load balancing · backup · DR · version control · deployment automation · monitoring · logging · hardening · cert management · channel promotion · message retention/purging/archiving/reprocessing.
**Channels:** source/destination connectors · filters · transformers · response transformers · code templates · pre/postprocessors · deploy/undeploy scripts · global scripts · shared libraries · error handlers · alerts · queues · retry policies. Transformers modify/convert/extract (HL7↔JSON etc.).

## 6. CANONICAL CLINICAL DATA MODEL
Prevent NURA dependency on any EMR's proprietary model. Canonical entities: Tenant, Organization, Facility, Location, Patient, PatientIdentifier, Practitioner, PractitionerRole, Appointment, Encounter, EpisodeOfCare, Coverage, Allergy, Problem, Diagnosis, Medication, MedicationRequest, MedicationAdministration, Immunization, Observation, LaboratoryResult, DiagnosticReport, ImagingStudy, Procedure, ServiceRequest, CarePlan, CareTeam, ClinicalNote, Document, Task, Communication, Consent, Provenance, AuditEvent.
**Canonical event envelope:** {event_id, event_type, event_version, tenant_id, source_system, destination_system, patient_correlation_id, encounter_correlation_id, practitioner_correlation_id, document_correlation_id, occurred_at, received_at, idempotency_key, trace_id, payload, provenance, security_labels, status}. The canonical model isolates the Flutter app, OpenEMR, and Hermes from vendor formats.

## 7. CORE INTEGRATION FLOWS
**Intake:** destination EMR → ADT/SIU/FHIR/vendor API → NextGen → normalize identity → MPI → OpenEMR patient/encounter → NURA workspace.
**Documentation:** provider opens patient → context verified → charts (Hermes may draft) → provider reviews/edits → signs → signed version immutable → outbound event.
**Document sync:** signed NURA doc → canonical doc → destination capability profile → NextGen transform → FHIR/C-CDA/PDF/MDM/API → destination → ACK/response → reconciliation → provider sees accepted/failed.

## 8. DOCUMENT UPLOAD STRATEGY (priority order)
1. **Structured FHIR** (Composition, Bundle, DocumentReference, Binary, Encounter, Condition, Observation, MedicationRequest, Procedure, Provenance) — preferred where supported.
2. **C-CDA** (validated, patient/encounter/provider/organization/section/signature metadata, template-validated, exact version retained).
3. **HL7 MDM** (T02/T04/T06/T08/T10 — encapsulated PDF/text/CDA + metadata + signature status).
4. **PDF upload** (standardized: identifiers, encounter, doc type, timestamp, provider + credentials, signature metadata, source system, page numbers, amendment status, cryptographic hash).
5. **Direct Secure Messaging** (approved doc → Direct address → tracked → reconciled → duplicate prevention).
6. **RPA fallback** ONLY where: no standards interface contractually available, no vendor API, no document interface, customer authorizes, vendor terms complied, human review available, audits preserved — a temporary adapter, never the foundation.

## 9. DESTINATION CAPABILITY REGISTRY
Every EMR gets a formal profile: {vendor, product, version, tenant_id, supported_interfaces[], supports_read/write/document_reference/binary/composition/mdm, requires_encounter_id/department_id/provider_mapping, acknowledgment_type, retry_policy, document_types, identifier_namespaces}. The sidecar auto-selects the strongest method: FHIR write → vendor REST → C-CDA → HL7 MDM → secure doc API → Direct → SFTP → controlled manual → authorized RPA.

## 10. PATIENT IDENTITY & MASTER PATIENT INDEX
Enterprise identifier · MRNs · assigning-authority namespaces · historical identifiers · aliases · DOB · legal sex · admin gender · address · phone · email · facility · insurance member ID · probabilistic + deterministic matching · duplicate/merge/unmerge detection · manual reconciliation. **RULE: never silently choose among patients — ambiguous matches = "Patient match requires review" — no note submitted until the destination identity is confirmed.**

## 11. PROVIDER IDENTITY CROSSWALK
NURA ID · OpenEMR practitioner ID · destination user ID · NPI · state license · DEA · facility credential · department · specialty · supervising physician · ordering/rendering provider codes · signing authority. **Never transmit under a generic integration user when the destination requires the treating/signing provider.**

## 12. ENCOUNTER MATCHING
Resolve: patient · facility · department · appointment · encounter · visit/account number · admission · service date · provider · document type. Support: scheduled, walk-ins, emergency, inpatient, telehealth, home visits, MIH, outreach, chart-only, telephone, async. **Never invent an encounter without an approved workflow.**

## 13. OPENEMR RULES
Functions: patient create/update · practitioner mapping · appointment sync · encounter creation · allergy/problem/medication sync · observation + lab ingestion · document + note storage · signature status · export · provenance · audit correlation · amendments. **RULE: use OpenEMR's supported API interfaces — never direct production DB writes, never bypass permissions, never manipulate signed documents, never shared super-admin creds, never assume internal schemas are stable.**

## 14. PERFEX RULES
Operational only: onboarding · facility implementation · interface builds · credentialing · vendor contacts · projects · tickets · milestones · billing · deployment checklists · customer success. **Perfex never stores full medical records.** Allowed: correlation IDs, minimal status, account/facility, task owner, integration status, support case, nonclinical milestone, redacted error category. Never: notes, reports, medications, labs, imaging, unstructured PHI, sensitive psychiatric records.

## 15. HL7 v2 EXPERTISE
ADT (A01-A40) · SIU (S12-S26) · ORM/OML/ORU/OUL/RDE/RAS · MDM (T02-T10) · DFT/BAR · X12 270/271, 276/277, 278, 837, 835.

## 16. FHIR EXPERTISE
R4 · US Core · SMART on FHIR · OAuth2/OIDC · Bulk Data · Subscriptions · search params · conditional create/update · transactions/batches · CapabilityStatement · OperationOutcome · Provenance · AuditEvent · Consent · security labels · terminology binding. NextGen = FHIR listener/sender + ADT→FHIR Patient templates.

## 17. ADAPTER FRAMEWORK (reusable, never from-scratch per vendor)
EmrAdapter: testConnection() · getCapabilities() · searchPatient() · getEncounter() · submitDocument() · getSubmissionStatus() · reconcile() — with per-EMR adapters for auth, patient search/read, encounter, appointment, document submission, structured write, ack, error translation, capability, reconciliation.

## 18. DOCUMENT RENDERING ENGINE
Outputs: FHIR Bundle/Composition/DocumentReference · C-CDA · PDF/A · text · RTF · HL7 ED · canonical JSON/XML. Metadata: patient name/id/DOB · encounter · service date · type · status · author · signing provider · facility/department · creation/signature time · amendment status · confidentiality · source system · version · hash · correlation ID.

## 19. RECONCILIATION & DELIVERY CONFIRMATION
**Sending ≠ success.** States: Draft → Signed → Queued → Transforming → Ready → Transmitted → Transport ACKed → Application accepted → Indexed in destination → Reconciliation complete · Failed/Retrying/Held/Rejected/Cancelled. Proof: HL7 ACK · FHIR 200/201 + resource ID · vendor tx ID · repository ID · Direct notification · file confirmation · destination query presence · human verification. **The UI shows the exact state — never merely "sent".**

## 20. ERROR HANDLING & DEAD-LETTER
Error classes: auth, authorization, patient not found/multiple, encounter not found, provider unmapped, invalid type, validation, destination unavailable, timeout, duplicate, rejected, unsupported, certificate, network, parsing, transformation, vendor business-rule. Flow: failure → classify → retryable? → safe retry → DLQ → human work queue → correct → reprocess → reconcile. **No failed clinical document disappears silently.**

## 21. IDEMPOTENCY
Key = SHA-256(tenant + destination + patient + encounter + document + version). Before resubmit: was the same version accepted? newer version? destination document ID created? amendment instead? manual intervention?

## 22. SECURITY
TLS ≥1.2 · mTLS · VPN · private routes · IP allowlisting · OAuth2/OIDC/SMART · SFTP keys · cert rotation · secrets management · RBAC/least privilege · DB + message encryption · log redaction · audit · tenant isolation · segmentation · secure backups · DR. **Prohibited:** passwords in channel scripts · PHI in unsecured logs · test patients to production · prod creds in dev · disabled cert validation · public NPM admin · one integration account for all customers · indefinite retention · unrestricted reprocessing · un-reviewed production channel edits.

## 23. DEPLOYMENT MODEL
Environments: Dev → Integration → QA → Staging → Customer Validation → Production → DR. Production: LB/private gateway → Node 1 + Node 2 → external PostgreSQL → encrypted shared storage → centralized logs/monitoring → backup/DR. **A single Mirth container on one VPS is NOT production HA.**

## 24. CHANNEL VERSION CONTROL & PROMOTION
Every channel: source-controlled XML · semantic version · peer review · tested · approved · promoted · release-tagged · change ticket · reversible · documented. Pipeline: dev branch → static review → unit tests → synthetic message tests → security validation → integration → customer acceptance → approved production. **No direct production channel edits except documented emergencies.**

## 25. TESTING FRAMEWORK
Synthetic patients/encounters/providers · vendor-approved test envs · deidentified payloads · known positive/negative. Tests: identity/encounter/provider mapping · HL7 parsing · FHIR/C-CDA validation · PDF rendering · submission · ACK · retry · duplicate prevention · timeout · invalid identifiers · missing encounter · destination outage · cert expiration · reprocessing · amendment · tenant isolation · audit generation.

## 26. MONITORING
Channel status · messages received/sent/filtered/queued/failed · retries · DLQ · latency (processing/destination/ACK) · DB health · disk/heap/CPU/memory · cert expiration · interface availability · reconciliation backlog · patient-match exceptions · provider-map failures · documents awaiting acceptance. Dashboards: executive status · per-customer health · per-EMR health · delivery · error queue · SLA · volume · reconciliation · security events.

## 27. SKILLS
NextGen: connectors/filters/transformers · JavaScript/Java · templates · DB/HTTP/TCP-MLLP/File/SFTP/SOAP/REST/FHIR/DICOM/JMS/SMTP · web services · extensions · message browser · stats · alerts · clustering · admin API. Programming: Java · JavaScript · SQL · Python · Bash required; TS/Go/C#/PHP/XSLT/XML/JSONPath/XPath preferred. DBs: PostgreSQL · MSSQL · Oracle · MySQL/MariaDB · Redis · MongoDB.

## 28. TERMINOLOGY
ICD-10-CM · CPT · HCPCS · LOINC · SNOMED CT · RxNorm · NDC · UCUM · CVX · NUCC taxonomy · NPI · OIDs · URI namespaces · value sets · concept maps · terminology services. Need not be a clinician — MUST understand the clinical consequences of incorrect mapping.

## 29. VENDOR ONBOARDING
Per customer: discovery questionnaire · capability assessment · network + data-flow diagrams · interface spec · security assessment · BAA/contract list · identity strategy · provider mapping · encounter matching · doc-type mapping · transport spec · test/go-live/rollback plans · support escalation · reconciliation · retention.

## 30. EXPERIENCE
7+ yrs healthcare integration · 5+ yrs production Mirth/NextGen · advanced HL7 v2 + FHIR R4 · C-CDA · 3+ major EMR integrations · OpenEMR or equivalent · document interfaces · identity mapping · HIPAA · high-volume interfaces · failure response · go-lives · vendor coordination.

## 31. CERTIFICATIONS
HL7 v2 · FHIR proficiency · NextGen training · Epic Bridges (where obtainable) · Oracle Health/Cerner training · AWS SA-A + Security · RHCSA/Linux · Security+ · CISSP/CCSP · ISO 27001 · HITRUST. **Supplemental — the exam proves the ability.**

## 32. PRACTICAL HIRING EXAM
Build a NextGen solution that: receives HL7 ADT · parses identifiers · converts to canonical JSON · creates/updates a patient in a mock OpenEMR FHIR server · receives a signed NURA doc · generates FHIR DocumentReference + Binary + PDF · produces HL7 MDM · sends to TWO mock destinations · handles one success + one rejection · retries appropriately · moves the final failure to a DLQ · prevents duplicates · records audit · shows reconciliation · documents the architecture. **Evaluation: correctness · patient safety · code quality · reusability · error handling · security · idempotency · observability · documentation · standards compliance · tradeoff explanations · vendor-lock-in avoidance.**

## 33. FIRST 90 DAYS
**1-30:** assess the existing Mirth/OpenEMR lanes · establish dev/test/prod environments · canonical model + event envelope · patient + provider crosswalks · connect OpenEMR (FHIR API) · source control + channel promotion · synthetic test library.
**31-60 (Sidecar core):** inbound patient/schedule interfaces · encounter-context service · signed-document event · PDF rendering · FHIR DocumentReference · C-CDA export · HL7 MDM export · reconciliation service · error work queue · Perfex operational tasks.
**61-90 (first external EMR):** first customer discovery · first destination adapter · patient/provider/document mapping · end-to-end + customer acceptance testing · controlled go-live · monitor acceptance · rollback/recovery docs · reusable onboarding template.

## 34. KPIs
Acceptance rate · interface availability (≥99.9%) · median delivery time · reconciliation completion · unresolved errors · duplicate rate (<0.1%) · patient-match exceptions · provider-map failures · EMR onboarding time · reusable-adapter % · MTTR/MTTD · channels under version control · automated-test coverage · complete audit provenance (≥99.5% confirmed acceptance; <0.5% unreconciled after 24h; critical alerting <5 min; **wrong-chart delivery = 0**).

## 35. CREDENTIAL PROFILE
Required: expert Mirth/NextGen · expert HL7 v2 · advanced FHIR R4 · C-CDA · Java/JS/SQL · OpenEMR API · identity mapping · document upload + reconciliation · HIPAA ops · production troubleshooting. Preferred: Epic/Cerner/athena · SMART · XDS/XDS-I · Direct · DICOM · clustering · AWS/K8s · MPI · HIE · security architecture.

## 36. THE JD
The Principal NextGen Connect Architect & Clinical Interoperability Engineer leads the NURA Clinical Sidecar — connecting NURA, Hermes, OpenEMR, Perfex, and external EMRs so providers chart once in NURA and the approved record is delivered safely and accurately to the destination system without re-charting. Owns HL7, FHIR, C-CDA, document generation, patient matching, provider mapping, encounter resolution, routing, upload, acknowledgments, reconciliation, security, monitoring, production support — making NURA a genuinely EMR-agnostic clinical workspace.

**Founder note (08-04):** the next critical role after this = the **Clinical Product and Workflow Architect** — a clinician-informaticist who defines exactly how providers chart, sign, prescribe, reconcile meds, handle abnormal results, and resolve interface exceptions BEFORE developers encode those workflows.
