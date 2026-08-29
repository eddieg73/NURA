# LEAD FLUTTER MOBILE ARCHITECT & HEALTHCARE INTEGRATION ENGINEER — the role spec (2026-08-04)

**Title:** Lead Flutter Mobile Architect and Healthcare Integration Engineer (the senior Flutter developer for NURA's clinician app)
**Reports to:** technical leadership (Hermes CTO lane) · **Owner of the funnel:** the AI hiring manager · **Signer:** the founder
**Alignment:** Amrit (current Flutter/core engineer) — the bar for the lane + the hiring funnel

## 15. REQUIRED CREDENTIALS & EXPERIENCE
**Required:** 5+ yrs mobile dev · 3+ yrs production Flutter · published iOS + Android apps · REST/OAuth 2.0/OIDC/WebSockets/webhooks · native Swift · native Kotlin · Flutter platform channels/plugins · secure local storage + offline sync · real-time voice/video/messaging/WebRTC · regulated industry (healthcare/fintech/gov) · CI/CD, automated testing, code review, release management.
**Strongly preferred:** OpenEMR · FHIR R4 · SMART on FHIR · HL7 · Mirth/NextGen · Chatwoot · Perfex · Twilio (Voice/Messaging/Conversations/Video) · DoseSpot/e-prescribing · Surescripts · Tavus/Daily video SDKs · clinical documentation · HIPAA mobile · multi-tenant SaaS · AWS healthcare · Docker/K8s · Terraform/IaC · MDM.

## 16. RECOMMENDED CERTIFICATIONS
Mobile: Google Associate Android Developer · Apple App Development with Swift · Dart/Flutter training · AWS Developer Associate · AWS Solutions Architect Associate · CKAD · GitHub Actions/CI/CD. Security: Security+ · CSSLP · GIAC Mobile Device Security · CISSP · CCSP · OWASP mobile. Healthcare: HL7 FHIR proficiency · HL7 interface training · SMART on FHIR implementation · HIPAA training · HITRUST implementation · ISO 27001.

## 17. REQUIRED TOOLS
Flutter SDK · Dart SDK · Android Studio · Xcode · VS Code · Git · GitHub/GitLab · Fastlane · Codemagic/GitHub Actions · Firebase App Distribution · TestFlight · Google Play Console · Postman/Bruno · OpenAPI/Swagger · Docker · Sentry · OpenTelemetry · Charles Proxy/Proxyman · Wireshark · SonarQube · Trivy · Snyk · Dependabot · OWASP ZAP. Must inspect: API requests, WebSocket traffic, TLS failures, push delivery, WebRTC quality, crash traces, plugin exceptions, memory/CPU/battery, background tasks, offline sync failures.

## 18. TESTING REQUIREMENTS (built in from day one)
Dart unit · Flutter widget · integration · API contract · FHIR validation · auth · authorization · offline sync · conflict resolution · prescription workflow · Twilio call/SMS/messaging · Tavus session · push · accessibility · performance · security · regression · device compatibility.
**Clinical safety scenarios:** wrong-patient prevention · wrong-provider prevention · duplicate-prescription prevention · expired session · lost network during prescription/note-signing · duplicate taps · stale chart data · conflicting offline edits · allergy-warning display · critical-result escalation · failed OpenEMR write · failed Chatwoot delivery · failed Twilio call · Tavus interruption · revoked device · tenant-isolation failure · provider-role change mid-session.

## 19. CI/CD & RELEASE MANAGEMENT
Environments: Local → Integration → QA → Staging → UAT → Production — each with SEPARATE endpoints, signing creds, databases, OAuth clients, Twilio/Tavus creds, OpenEMR instances, Chatwoot/Perfex accounts, e-prescribing test/prod, push certs, analytics, error reporting.
Pipeline: commit → static analysis → dependency scan → secret scan → unit → widget → build → integration → security review → signed test release → QA → clinical workflow validation → authorized production release. **No developer changes production code/config/audit logs without independent oversight.**

## 20. APP STORE RESPONSIBILITIES
**Apple:** developer account · identifiers · provisioning · distribution/push certs · associated domains · universal links · privacy disclosures · health-data declarations · TestFlight · review responses · encryption declarations · Sign in with Apple · background-mode justifications · camera/mic permissions.
**Android:** Play Console · application IDs · signing keys · Play App Signing · internal/closed testing · data-safety declarations · permission declarations · foreground services · background compliance · Telecom integration · app links · managed deployment · release tracks.
**The ORGANIZATION (not an individual) owns the Apple/Google accounts, signing keys, domains, repos, and production credentials.**

## 21. MOBILE DEVICE MANAGEMENT (clinician devices)
Enrollment · app deployment · config profiles · certificate deployment · VPN config · remote lock · selective/full wipe · min OS versions · screen-lock/encryption enforcement · compromised-device detection · copy-paste/screenshot policy · managed app config · revocation · compliance checks. Platforms: Microsoft Intune · Jamf · Kandji · JumpCloud · Miradore · ManageEngine · Apple Business Manager · Android Enterprise.

## 22. INTEGRATION OWNERSHIP MATRIX
| Integration | Mobile (developer) | Backend (Hermes/ops) |
|---|---|---|
| OpenEMR | FHIR UI + workflow | auth, mapping, auditing |
| Perfex CRM | operational screens, task views | credential protection, data minimization |
| Chatwoot | inbox, messages, attachments, notifications | webhooks, identity matching, API tokens |
| E-prescribing | Rx user experience | vendor integration, EPCS controls, records |
| Twilio | call/SMS/video/notification UI | token generation, routing, recording policy |
| Tavus | video room + avatar UX | conversation creation, key protection, governance |
| Hermes | AI interaction + review interface | model routing, safety, evidence, auditing |
| Push | device registration + display | PHI minimization + dispatch |
| Offline sync | encrypted local queue + conflict UI | versioning, idempotency, final authorization |

## 23. PRACTICAL HIRING EXAMINATION (the controlled assessment)
Build a small Flutter app that: OAuth 2.0 + PKCE auth · mock FHIR Patient retrieval · meds + allergies display · draft encounter note · encrypted local storage · offline queue + sync on reconnect · Chatwoot-style conversation · short-lived Twilio token + test call/video · Tavus/Daily test room · camera/mic permissions · duplicate-submission prevention (idempotency key) · audit correlation ID · unit/widget/integration tests · architecture + threat-model documentation.
**Evaluation:** code quality · architecture · security · error handling · testing · UX · accessibility · offline behavior · API design · native integration · clinical workflow awareness · documentation · ability to explain decisions.

## 24. FIRST 90-DAY DELIVERABLES
**Days 1-30:** review NURA architecture · Flutter standards · repo structure · auth · tenant/role handling · secure storage · design system · CI/CD · TestFlight + Android testing · API contracts · mock integration environment.
**Days 31-60:** patient search · chart · appointments · encounter drafts · Chatwoot inbox · Twilio messaging · push notifications · encrypted offline queue · audit IDs · initial security review.
**Days 61-90:** Twilio voice · Tavus conversational video · med reconciliation · e-prescribing shell · OpenEMR writes · provider-signature workflow · conflict-resolution screens · clinical UAT · penetration testing · limited production pilot.

## 25. FINAL CREDENTIAL PROFILE
Required: senior Flutter/Dart · production iOS+Android deployment · Swift + Kotlin · REST/OAuth/OIDC/WebSocket/webhook · secure storage + offline sync · strong automated testing · real-time communications · regulated environment. Preferred: OpenEMR/FHIR · SMART · Chatwoot · Perfex · Twilio · Tavus/Daily · DoseSpot · HIPAA/HITRUST · Docker/K8s/AWS · multi-tenant healthcare SaaS.

## 26. THE JD SUMMARY
The Senior Flutter Healthcare Integration Developer leads NURA's clinician-facing mobile app (iOS + Android), integrating OpenEMR, Perfex CRM, Chatwoot, Twilio, Tavus, e-prescribing, and Hermes through secure, auditable backends. The app is not a mobile interface — it is a clinical access point that must preserve patient identity, provider authority, data integrity, privacy, auditability, and safe operational behavior across every connected system. Works with clinical leadership, backend engineers, DevSecOps, security officers, and interoperability engineers.

## THE FUNNEL (hiring doctrine)
The AI hiring manager runs the funnel (the spec + the practical exam) · the founder signs · the exam = the gate (section 23 — no certifications-only hires) · the 90-day plan = the onboarding contract (section 24).
