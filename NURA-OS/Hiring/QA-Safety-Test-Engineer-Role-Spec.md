# PRINCIPAL QA AUTOMATION, CLINICAL VALIDATION & SAFETY TEST ENGINEER — the role spec (2026-08-04, founder canonical)

**Position:** Principal QA Automation, Clinical Validation & Safety Test Engineer
**Alt:** Lead Healthcare Software Quality Engineer / Principal Clinical Systems Validation Engineer / Senior Test Automation Architect / Director of Quality Engineering / Clinical Safety and Release Validation Lead
**Reports to:** Director of Quality Engineering (Hermes lane) · **Funnel:** the AI hiring manager · **Signer:** the founder
**Why:** proves NURA works correctly BEFORE providers, patients, and customer health systems depend on it — the final technical quality barrier between development and real-world clinical use.

## 1. MISSION
Design, implement, and maintain the complete QA + release-validation program: verifying apps, integrations, AI agents, clinical workflows, and infrastructure operate safely, accurately, securely, reliably before production. Tests: Flutter · React/Next · Hermes kernel · OpenEMR · Perfex · Chatwoot · NextGen · Twilio · Tavus · e-Rx · Orthanc · OHIF · ThaiRIS · external EMR sync · Clinical RAG · multi-agent · authN/Z · tenant isolation · offline sync · audit/reconciliation. **Objective: prevent defects from becoming clinical, privacy, financial, or operational incidents.**

## 2. CORE OWNERSHIP
Enterprise test strategy · automated test architecture · clinical workflow validation · integration/interface/API testing · mobile/web testing · performance · security regression · AI evaluation testing · data validation · release certification · defect management · test-data governance · production monitoring validation · incident regression.

## 3. OPERATING MODEL (quality throughout, never a final check)
Requirement → Clinical Safety Review → testable acceptance criteria → unit → component → API/contract → integration → clinical workflow → security/performance → UAT → release certification → production monitoring.

## 4. TEST ARCHITECTURE (layered)
Unit (functions/classes/transformers/parsers/validators/rules/calculations/mappings/permissions/clinical safety logic) · Component (widgets, forms, tables, alerts, med/lab/imaging cards, banners, auth) · Contract (mobile↔API, web↔API, Hermes↔MCP, Hermes↔models, NURA↔OpenEMR/Chatwoot/Twilio/Tavus/NextGen, NextGen↔external EMRs) · Integration (real multi-service) · E2E (user action → destination confirmation).

## 5. CLINICAL SAFETY TESTING (explicit suites per hazard)
Wrong-patient/encounter/provider · duplicate Rx · Rx after session expiry · allergy/interaction warning failure · CS authorization failure · critical not escalated · addendum not displayed · med list overwritten incorrectly · stale data · AI draft as final · unsigned note submitted · signed note modified without amendment · EMR rejection shown as success · message to wrong department · cross-tenant exposure · offline chart conflict · duplicate upload · failed sync · provider mapping failure. **Every hazard: test case, expected result, severity, owner, release threshold.**

## 6. WRONG-PATIENT PREVENTION
Banner persistence · similar-name warnings · DOB/MRN/photo display · context confirmation · switching with unsaved work · deep links · tab confusion · mobile background/resume · external mapping · MPI exceptions. **Targets: wrong-patient chart/Rx/external upload = 0 tolerated.**

## 7. AUTH TESTING
Password/MFA/passkeys/biometric · OAuth2/OIDC/PKCE · sessions/tokens · device register/revoke · deactivation · role/tenant changes · break-glass · elevation. Roles matrix: physician/PA/NP/nurse/paramedic/MA/scheduler/coordinator/billing/manager/admin/interface engineer/auditor/patient. **Client-side restrictions tested against server-side enforcement.**

## 8. TENANT ISOLATION
Prove one customer can't touch another's: patients/providers/docs/messages/Rx/tasks/audit/files/integrations/AI memory/vector collections/DB records/objects/notifications. Tests: modified URLs/tenant/patient IDs · stolen tokens · replayed requests · cross-tenant search · background/cache/WebSocket/vector leakage · file-path + audit-query manipulation.

## 9. OPENEMR TESTING
Search/create/update · appointments · encounters · meds/allergies/problems · notes · document upload · signature/amendment · FHIR responses · API/permission failures · duplicates · audit correlation. **No test touches production DB tables.**

## 10. NEXTGEN / EMR INTERFACE TESTING
HL7 parsing · FHIR transform · C-CDA · MDM · PDF · patient/provider/encounter mapping · routing · ACK · retries · DLQ · reprocessing · duplicates · reconciliation. Scenarios: success, destination down, auth failure, patient not found/multiple, provider unmapped, encounter missing, invalid type, malformed HL7, invalid FHIR, rejected C-CDA, duplicate, late ACK, timeout, cert expiry.

## 11. E-PRESCRIBING TESTING
New/refill/renewal/change/cancel/discontinue · pharmacy · allergy/duplicate/interaction/formulary · prior auth · CS workflow · identity proofing + 2FA · transmission status · pharmacy rejection · duplicate clicks · network interruption · stale context. **No live Rx in automated testing except approved vendor test environments.**

## 12. TWILIO TESTING
In/out/missed calls · voicemail · SMS/MMS · transfer/conference · hold/mute · Bluetooth · WebRTC failure · token expiry · push failure · recording/consent indicators · dispositions · transcription → OpenEMR doc workflow. Test credentials + controlled numbers.

## 13. TAVUS / VIDEO TESTING
Conversation creation · short-lived tokens · camera/mic permissions + switching · audio routing · degradation/disconnect/reconnect · termination · transcripts · AI disclosure · human escalation · consent · no unauthorized recording · no auto chart insertion · no autonomous clinical decisions.

## 14. CHATWOOT TESTING
Conversations · delivery · attachments · internal notes · assignment/transfer · labels · status · push · contact matching · ambiguous matching · escalation · chart-summary creation + provider review · failure handling. **Not all messages auto-convert to clinical documentation.**

## 15. FLUTTER MOBILE TESTING
iOS/Android · phones/tablets · screen sizes · OS versions · biometrics · push · camera/mic/Bluetooth · offline/background/resume · local encryption · secure wipe · device revocation · deep/universal/app links · memory/battery · network switching. Tools: Flutter integration · Appium · Maestro · XCTest/XCUITest · Espresso · Firebase Test Lab · BrowserStack · Sauce Labs.

## 16. WEB TESTING
Chrome/Edge/Safari/Firefox · responsive · a11y · large tables · clinical forms · real-time · calling/video · sessions/tabs · caching/service workers · draft recovery · refresh/back · deep links · clipboard · uploads/downloads. Tools: Playwright · Cypress · Vitest · Testing Library · Storybook · Axe · Lighthouse.

## 17. API TESTING
REST · FHIR · GraphQL · gRPC · WebSockets · SSE · webhooks · MCP tools. Valid/invalid/missing/extra fields · unauthorized/forbidden · expired tokens · rate limits · idempotency · pagination/filter/sort · timeouts · retries · schema changes · version compat. Tools: Postman/Newman · Bruno · REST Assured · Pact · Schemathesis · Karate · k6 · Locust.

## 18. AI / CLINICAL RAG TESTING (with the AI/ML engineer + clinicians)
Summarization · drafts · differentials · must-not-miss · retrieval/citations · med rec · lab interpretation · imaging summaries · coding · triage · injection resistance · unauthorized tools · cross-patient memory · cross-tenant retrieval · hallucination · unsupported claims · refusal · structured validity. Categories: accuracy/grounding/safety/completeness/bias/consistency/citation integrity/tool selection/permission compliance/latency/cost. **Evaluated against expert-reviewed cases — never merely against another model.**

## 19. DETERMINISTIC RULE TESTING (independent coverage)
Critical K/glucose/Hgb · severe HTN/HDN · allergy conflicts · duplicate meds · max/renal doses · CS rules · cosignature · authentication · emergency escalation. **Each rule: positive + negative + boundary + unit + integration tests, version reference, effective date.**

## 20. TEST DATA (governed synthetic program)
Adult/pediatric/geriatric/pregnancy · multiple allergies · polypharmacy · renal/hepatic impairment · psych emergency · critical labs · similar patients · duplicates/merges · unmatched provider · missing encounter · multilingual · offline mobile. **Production PHI never casually copied down.**

## 21. TEST ENVIRONMENTS
Developer · automated integration · QA · clinical validation · staging · customer acceptance · production · DR — each with separate DBs, credentials, OAuth clients, Twilio/Tavus, OpenEMR/Chatwoot/Perfex/NextGen instances, e-Rx accounts, object storage, model policies.

## 22. PERFORMANCE / LOAD
Concurrent users · searches · chart open · note saves · lab ingestion · uploads · EMR submissions · chat/calls/video · AI requests · queues · DB · WebSockets. Measure: response time · throughput · error rate · CPU/mem/disk · DB connections · queue depth · latency · tokens · model latency · recovery time.

## 23. RESILIENCE / CHAOS
Postgres/Redis/Qdrant down · OpenEMR/NextGen/Twilio/Tavus/model down · DNS failure · cert expiry · disk full · queue backup · latency spikes · node/region failure. **Fail safely and visibly.**

## 24. SECURITY REGRESSION (with cybersecurity)
Auth bypass · session fixation · token replay · XSS/CSRF · SQL/command injection · path traversal · upload abuse · SSRF · IDOR · tenant violations · secret exposure · prompt injection · dependency vulns. Automated scanning + manual validation.

## 25. ACCESSIBILITY (WCAG)
Keyboard · screen readers · focus order/visibility · labels · errors · contrast · scaling · tables/charts · captions · non-color indicators · reduced motion · mobile. **Automated scans never replace manual testing.**

## 26. AUDIT / PROVENANCE
User/role/tenant/patient/encounter/action/timestamp · device/app · correlation ID · before/after values · model/prompt versions · tool calls · signature · destination · ACK · amendment. Complete, tamper-resistant, restricted.

## 27. DEFECT CLASSIFICATION
Severity: S1 patient safety/privacy/outage · S2 major clinical/operational · S3 limited impairment · S4 minor · S5 cosmetic. Priority: immediate/next release/planned/deferred. **Clinical severity and engineering priority tracked separately.**

## 28. RELEASE GATES (a release must not proceed when)
S1 open · critical vuln unresolved · wrong-patient defect · cross-tenant defect · critical-result workflow fails · e-Rx validation fails · audit incomplete · reconciliation fails · rollback unavailable · required clinical approval missing · coverage incomplete.

## 29. RELEASE CERTIFICATION PACKAGE
Version · scope · changed components · test results · open defects · clinical validation · security/performance/compatibility results · known limitations · rollback + monitoring plans · approval signatures.

## 30. UAT
Structured testing with all clinical/ops roles — realistic workflows, not scripted button checks.

## 31. PRODUCTION VALIDATION (post-deploy)
Login/search/chart/draft/sign · Rx test workflow where permitted · Chatwoot/Twilio · external EMR submission · audit · monitoring · alerts · rollback readiness — controlled accounts + approved test patients.

## 32-35. SKILLS, EXPERIENCE, CREDENTIALS
Languages: TS/JS · Python · Java · SQL · Bash · Dart/Kotlin/Swift familiarity. Tools: Playwright · Cypress · Flutter Test · Appium · Maestro · Postman/Newman · Pact · REST Assured · JUnit · Pytest · k6 · Locust · OWASP ZAP · SonarQube. Platforms: Docker · K8s · GitHub Actions · GitLab CI · Jenkins · AWS · Postgres · Redis · Qdrant · OpenEMR · NextGen.
Experience: 7+ yrs testing/QE · 4+ yrs automation · distributed systems · APIs · mobile + web · healthcare/regulated · CI/CD · performance · security · test strategies + release criteria. Preferred: OpenEMR · FHIR/HL7 · NextGen · e-Rx · Twilio · Chatwoot · AI/LLM eval · clinical safety · HIPAA · multi-tenant SaaS · PACS/RIS · offline sync. Credentials: ISTQB Advanced Test Automation · CSQE · CPHQ · CPPS · HL7/FHIR · Security+ · AWS · K8s · HIPAA · ISO 27001 audit.

## 36. PRACTICAL EXAM
For the scenario (provider logs in → selects patient → reviews meds → Hermes drafts note → signs → submits to OpenEMR → NextGen → external EMR → REJECTION → corrects mapping → reprocesses → confirms reconciliation), deliver: test strategy · risk analysis · automated API tests · web/mobile E2E · wrong-patient test · duplicate-submission test · external rejection test · audit-validation test · performance test · security test · defect report · release recommendation.

## 37. FIRST 90 DAYS
**1-30:** inventory coverage · enterprise test strategy · defect taxonomy · clinical safety test register · synthetic data framework · CI test reporting · release gates · initial API automation.
**31-60:** Flutter critical workflows · dashboard workflows · OpenEMR contract tests · NextGen interface tests · Twilio/Chatwoot · external EMR reconciliation · tenant isolation · AI safety evals.
**61-90:** performance + resilience · prescribing suite · critical-result suite · clinical UAT · release-certification process · production validation checklist · certify the initial clinical pilot.

## 38. KPIs
Automated + critical-workflow coverage · defect escape · production incident · wrong-patient/cross-tenant defect rates · MTTD/MTTR · rollback rate · execution time · flaky rate · UAT completion · interface acceptance · regression + security regression coverage. **Safety targets: wrong-patient incidents = 0 · cross-tenant = 0 · unreviewed Rx = 0 · silent criticals = 0 · failed-as-complete = 0 · unlogged actions = 0 · S1 released knowingly = 0.**

## 39-40. PROFILE + THE JD
Required: advanced automation · web/mobile/API · distributed systems · CI/CD · performance/resilience · security regression · defect analysis · regulated software · release-gate discipline. Preferred: healthcare validation · FHIR/HL7 · OpenEMR · NextGen · e-Rx · AI/LLM eval · Twilio/Chatwoot · multi-tenant clinical SaaS.
**The JD:** leads quality engineering for NURA — testing more than whether software functions: whether it behaves safely under failure, prevents wrong-patient/wrong-provider actions, preserves tenant isolation, handles clinical exceptions, records complete audits, and accurately reports external acceptance/rejection. **The final technical quality barrier between development and real-world clinical use.**

**Founder note (08-04):** six core roles remain — Cybersecurity/Privacy/Compliance Architect · SRE/DB/Cloud Operations Engineer · Clinical Data Engineer & Healthcare Analytics Architect · Healthcare UI/UX & Human-Factors Designer · Technical Product Manager & Agile Delivery Lead · Technical Writer/Training/Implementation Specialist.
