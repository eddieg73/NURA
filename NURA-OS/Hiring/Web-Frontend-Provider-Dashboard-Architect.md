# SENIOR WEB FRONTEND ARCHITECT & CLINICAL DASHBOARD ENGINEER — the role spec (2026-08-04, founder canonical)

**Position:** Senior Web Frontend Architect & Clinical Dashboard Engineer
**Alt:** Lead React/Next.js Healthcare Engineer / Principal Clinical UI Architect / Senior Provider Dashboard Developer / Lead Web Applications Engineer / NURA Clinician Experience Architect
**Reports to:** VP Web · **Funnel:** the AI hiring manager · **Signer:** the founder

## 1. MISSION
Design, build, secure, test, and maintain NURA's browser-based applications for: physicians · PAs · NPs · nurses · paramedics · MAs · coordinators · schedulers · practice managers · billing · clinical administrators · interface engineers · security · support · executives. The unified web interface connecting: Hermes kernel · OpenEMR · Perfex · Chatwoot · NextGen · Twilio · Tavus · Orthanc · OHIF · ThaiRIS · e-prescribing · labs · external EMRs · Paperclip ops · population-health analytics.

## 2. PRIMARY WEB APPLICATIONS
1. **Provider Clinical Workspace:** patient search · chart · encounter documentation · note drafting · med rec · allergy review · orders · e-Rx · lab/imaging review · signature · external sync · clinical messaging · tasks.
2. **Administrative Portal:** users · roles · tenants · facilities · onboarding · integration config · workflow config · devices · audit review · billing admin · support.
3. **Paperclip Executive Operations Dashboard:** department performance · projects · agent supervision · assignments · operational tasks · integration status · financials · onboarding · SLA · escalations · executive reporting.
4. **Interoperability Operations Console:** NextGen channel status · interface health · message failures · patient-match exceptions · provider mapping · encounter matching · delivery reconciliation · DLQs · retries · customer integrations.
5. **Population Health Dashboard:** high-risk lists · discharge follow-up · ED utilization · care gaps · adherence · chronic cohorts · preventive opportunities · RPM · MIH · outreach.

## 3. REQUIRED STACK
React · Next.js · TypeScript · Tailwind · TanStack Query + Table · React Hook Form · Zod · WebSockets + SSE · OpenAPI clients · FHIR components · Storybook · Playwright · Vitest · Testing Library. Supporting: OAuth2/OIDC · SMART on FHIR · WebAuthn/passkeys · WebRTC · service workers/PWA · IndexedDB · secure browser storage · CSP · Trusted Types · OTel · Sentry · Docker · GitHub Actions. Must understand browser internals: HTTP/TLS/cookies/sessions/CORS/CSRF/XSS/clickjacking/caching/secure delivery.

## 4. FRONTEND ARCHITECTURE
Application shell (auth · tenant selection · nav · notifications · audit context · feature permissions) + clinical domains (patient, encounter, meds, allergies, labs, imaging, prescribing, documents, messaging, tasks) + operational domains (Perfex, Paperclip, interface ops, support, analytics, admin) + shared services (API client, FHIR client, WebSocket client, error handling, feature flags, telemetry, accessibility, design system).

## 5. PROVIDER CLINICAL WORKSPACE
**Patient banner** (always visible): legal + preferred name · DOB/age · MRN · photo (authorized) · allergies · critical alerts · encounter · facility · assigned provider · external EMR status. **Prevent accidental patient switching with unsaved/unsigned work.** Chart sections: summary/timeline/encounters/problems/meds/allergies/immunizations/vitals/labs/imaging/procedures/documents/messages/care plans/referrals/tasks/billing/audit (authorized). Encounter docs: type · import history · dictate/type/templates · structured findings · review Hermes drafts · edit · diagnoses · orders · prescribe · follow-up tasks · sign · sync OpenEMR · submit destination · delivery status.

## 6. AI-ASSISTED CHARTING UI
Clear visual distinction: source facts · imported · patient-reported · AI draft · clinician-edited · clinician-authored · signed · external EMR. Required: "AI-generated draft" label · evidence panel · uncertainty panel · supporting/conflicting info · suggestions · accept/reject controls · edit tracking · citation inspection · safety warnings · feedback. **Never imply AI content is already part of the record.**

## 7. CLINICAL WORK QUEUES
Queues: unsigned notes · drafts · refill requests · med rec · abnormal/critical labs · imaging reports · critical imaging · patient messages · referral follow-up · prior auths · discharge follow-up · interface failures · EMR rejections · provider-mapping exceptions · identity exceptions · care gaps. Support: filter/sort/assign/priority/due/escalation/bulk navigation/audit. **Bulk clinical approval PROHIBITED for high-risk actions.**

## 8. OPENEMR INTEGRATION (through Hermes + the API gateway)
Frontend must NOT: connect directly to the OpenEMR DB · store admin creds · embed permanent secrets · bypass permissions · assume success without server confirmation. Functions: patient retrieval · encounter creation · note retrieval/draft · meds/allergies/labs · document upload · signature + amendment workflows · audit correlation.

## 9. PERFEX (operational only)
Onboarding · projects · credentialing · contracts · tickets · tasks · invoices · estimates · staffing · vendor coordination · milestones. **No full clinical records in Perfex — sanitized references + correlation IDs only.**

## 10. CHATWOOT (native omnichannel inbox)
Conversations · identity status · history · attachments · internal notes · agent/team assignment · labels · status · escalation · search · typing/read indicators · audio · clinical classification. Provider selects clinically relevant messages → draft chart entry for review. **Not every conversation auto-enters the chart.**

## 11. TWILIO (dashboard)
Browser calling · in/out calls · SMS/MMS · voicemail · queues · transfer · conference · telehealth video · dispositions · recording indicators · consent · missed-call flows. Controls: mute/hold/speaker/mic/camera/transfer/end · network indicator · identity confirmation. **Master creds stay server-side — the browser gets short-lived scoped tokens.**

## 12. TAVUS VIDEO
Patient education · intake · navigation · appointment prep · discharge instructions · care-plan reinforcement · admin assistance. MUST: disclose AI · consent · camera/mic permission · connection status · termination · human escalation · no unsupervised clinical decisions · approved transcripts · review before chart insertion.

## 13. E-PRESCRIBING INTERFACE
Search · strength/form/route/frequency/qty/refills/days' supply/SIG · pharmacy · formulary · allergy/interaction/duplicate warnings · history · renewals/changes/cancel/discontinue · prior auth · EPCS. Final review screen: patient/DOB/prescriber/med/strength/instructions/qty/refills/pharmacy/warnings/CS status. **Vendor-required authentication before transmission.**

## 14. LABORATORY INTERFACE
Statuses clear: normal/abnormal/critical/preliminary/final/corrected/cancelled/indeterminate. Ranges · units · trends · graphs · source lab · collection/result dates · acknowledgment · follow-up · notification · task creation. **Criticals remain prominently visible until addressed.**

## 15. IMAGING / PACS
Orthanc · OHIF · ThaiRIS · external PACS · reports · orders · study status · criticals. View metadata · read report · open in OHIF · compare · addenda · acknowledgment · follow-up tasks · communication documentation.

## 16. EXTERNAL EMR SYNC STATUS (exact delivery state)
Draft → Signed → Queued → Transforming → Transmitted → Transport ACKed → Accepted → Indexed in chart → Reconciliation complete · Failed/Rejected/Held. **Never show "complete" when only transmitted.** Failures display: error category · patient · encounter · destination · retry status · responsible team · recommended action · audit reference.

## 17. PAPERCLIP EXECUTIVE OPS INTERFACE
Departments: clinical ops · engineering · onboarding · credentialing · billing · marketing · sales · compliance · legal · HR · security · support. Functions: agent status · objectives · tasks · approvals · exceptions · escalations · projects · workload · performance/budget indicators · audit · human takeover. **Agents must not conceal completed actions or exceed permissions.**

## 18. ADMIN PORTAL
Tenant/facility creation · department config · invitations · roles · permissions · onboarding · identity mapping · integration config · feature flags · branding · templates · clinical policies · notification settings · audit review · session/device revocation · emergency access review. **Admin separated from normal clinical access.**

## 19. DESIGN SYSTEM
Typography · spacing · forms · buttons · tables · modals · drawers · cards · tabs · clinical alerts · patient banners · med/lab/imaging/task cards · message components · signature controls · status badges · empty/loading/error states. Alert hierarchy: informational → routine → abnormal → urgent → critical → emergency. **Color is never the only status indicator.**

## 20. ACCESSIBILITY (WCAG 2.2 AA)
Keyboard · screen readers · contrast · focus states · semantic HTML · accessible forms/tables/charts · captions · scalable text · reduced motion · error descriptions · non-color indicators.

## 21. RESPONSIVE
Desktop · laptops · tablets · large monitors · mobile browsers where appropriate. Complex charting = desktop/tablet priority; urgent review + tasks = mobile-usable.

## 22. REAL-TIME
Messages · calls · criticals · assignments · document sync · interface failures · signature requests · agent/patient status. WebSockets/SSE/push/event streams. **Every event tenant-scoped + authorization-checked.**

## 23. OFFLINE / CONNECTIVITY
Network interruption · expired sessions · failed writes · partial loads · retries · unsaved drafts · refresh · duplicates. Display: online/offline/reconnecting/saving/saved-locally/synchronized/failed. **Clinical writes use idempotency keys.**

## 24. SECURITY
OAuth2/OIDC/PKCE · WebAuthn/passkeys · MFA · secure cookies · CSRF/XSS/CSP/Trusted Types/clickjacking/CORS · sessions · RBAC/ABAC · tenant isolation · secure logging · dependency/secret scanning · SBOM. **Prohibited:** production secrets in the frontend · stored passwords · trusting browser role state · disabled TLS · PHI in analytics · sensitive tokens in ordinary local storage · clinical console logging · client-side-only admin hiding · assuming obscured elements = security.

## 25. AUDIT & PROVENANCE UI
Authorized view of: chart access · draft/edits · what Hermes generated vs provider accepted/changed · signatures · submission · destination · acceptance · amendments · model/prompt versions. Visibility without alteration.

## 26. PERFORMANCE BUDGETS
Initial dashboard < 3s · patient search < 2s · chart summary < 3s · draft-save ack < 1s · critical alert delivery < 5s — measured under realistic conditions.

## 27. TESTING + CLINICAL SAFETY SCENARIOS
Unit/component/integration/E2E/visual regression/accessibility/security/performance/cross-browser/role-permission/tenant-isolation. Scenarios: wrong-patient · stale encounter · duplicate Rx click · failed signature/sync · critical ack · session expiry mid-chart · network loss during save · cross-tenant URL manipulation · unauthorized deep links · AI draft shown as signed · EMR rejection.

## 28-29. BROWSERS + CI/CD
Chrome · Edge · Safari · Firefox (maintained versions; clinical deployments block dangerously outdated). CI/CD: PR review · static analysis · type checking · unit/component/E2E · dependency/secret scans · a11y checks · preview envs · staging · UAT · feature flags · canary · rollback. **No unreviewed frontend code to production.**

## 30-32. EXPERIENCE & CREDENTIALS
7+ yrs frontend · 4+ yrs React/TS · production Next.js · complex dashboards · real-time · secure auth · large forms/tables · automated testing · regulated/sensitive data · API-team collaboration · responsive + accessible. Preferred: healthcare · OpenEMR · FHIR/SMART · clinical documentation · e-Rx · Twilio · Chatwoot · WebRTC · OHIF · PACS/RIS · multi-tenant SaaS · HIPAA · clinical AI interfaces. Credentials: advanced React/TS · AWS · CKAD · Security+ · a11y cert · HL7/FHIR · HIPAA — **demonstrated ability > certificates.**

## 33. PRACTICAL EXAM
Build a provider-dashboard prototype: authenticate · patient banner · synthetic FHIR patient · meds + allergies · encounter draft · AI content shown separately · clinician edits · evidence citations · draft save · FAILED save handled · lab result · critical alert · external sync status · real-time event · two user roles enforced · automated tests · accessibility · documented security decisions. **Evaluation: architecture · type safety · security · clinical usability · a11y · error handling · real-time · testing · performance · docs · tradeoffs.**

## 34. FIRST 90 DAYS
**1-30:** web architecture · design system · auth · tenant selection · patient banner · navigation · CI/CD · component testing · Storybook. **31-60:** patient chart · encounter workspace · work queues · OpenEMR APIs · Chatwoot · real-time notifications · audit context · external delivery status. **61-90:** e-Rx workspace · Twilio calling/messaging · Tavus video · OHIF · Paperclip ops dashboard · a11y + security reviews · provider usability testing · limited clinical pilot.

## 35. KPIs
Adoption · documentation time · UI error rate · draft-save failure · page-load · a11y compliance · test coverage · production defects · satisfaction · critical/failed-sync visibility · task completion time · security findings · cross-tenant incidents. **Safety targets: wrong-patient = 0 · cross-tenant = 0 · hidden criticals = 0 · unsigned-as-signed = 0 · failed-as-complete = 0 · unauthorized actions = 0.**

## 36-37. PROFILE + THE JD
Required: expert React/Next/TS · complex dashboards · secure auth · real-time · frontend testing · a11y · API integration · responsive · security awareness. Preferred: healthcare/FHIR · OpenEMR · e-Rx · Chatwoot · Twilio · Tavus · OHIF/PACS · clinical AI interfaces · multi-tenant SaaS.
**The JD:** leads NURA's browser-based clinician, administrative, interoperability, population-health, and executive operations applications — one efficient workspace where the provider reviews the patient, documents, communicates, prescribes, signs, and verifies synchronization into the receiving EMR.
