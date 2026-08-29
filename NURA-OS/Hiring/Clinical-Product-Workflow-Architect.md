# DIRECTOR OF CLINICAL PRODUCT ARCHITECTURE & INFORMATICS — the role spec (2026-08-04, founder canonical)

**Position:** Director of Clinical Product Architecture & Informatics
**Alt:** Chief Clinical Informatics Product Architect / Clinical Workflow and Safety Architect / Lead Physician Informatics Engineer / Director of Clinical Systems Design / Principal Clinical Product Manager
**Reports to:** CMO + CTO · **Funnel:** the AI hiring manager · **Signer:** the founder
**Why:** prevents engineers from building technically impressive workflows that are clinically unsafe, inefficient, or unusable.

## 1. MISSION
Convert real-world clinical practice into precise product requirements, workflow rules, safety controls, interface behavior, and acceptance criteria. The architect sits between clinical leadership, providers, product, Flutter/web/backend/AI/NextGen/OpenEMR engineers, security, compliance, and QA — ensuring NURA reflects how medicine is actually practiced while preserving patient safety, provider authority, documentation integrity, compliance, and efficient operations.

## 2. CORE RESPONSIBILITY
Define how clinicians: locate/verify patients · open encounters · review histories · reconcile meds · review allergies · document · examine · assess · rank differentials · plan · order · prescribe · review labs/imaging · respond to critical findings · communicate · refer · follow up · sign · amend · close encounters · sync to external EMRs. Specify the difference between: clinical fact · patient-reported · imported · AI draft · clinician interpretation · recommendation · preliminary vs final diagnosis · signed record · administrative · billing.

## 3. CLINICAL PRODUCT GOVERNANCE
**Clinical Product Council:** Medical Director · PA · NP · RN · Pharmacist · Clinical Informaticist · Product Architect · Patient Safety Officer · Compliance · Engineering. Approves: workflows · new AI functions · safety risks · terminology · escalation rules · prescription workflows · incident reviews · release criteria · provider feedback · automation boundaries · policy versions.

## 4. PROVIDER WORKFLOW ARCHITECTURE
**Patient banner:** full legal name · preferred name · DOB · age · administrative sex · pronouns · MRN · photo (authorized) · allergies · critical alerts · facility · current encounter · assigned provider. **The provider must confirm patient context before: signing, prescribing, ordering, clinical messaging, document upload, result release.**
**Encounter types:** office/telehealth/home/MIH/emergency-follow-up/hospital-discharge-follow-up/transitional-care/telephone/asynchronous/med-refill/results-review/administrative/procedure/CCM/RPM — each with required/optional data, templates, documentation, billing, signature, EMR mapping, closing criteria.

## 5. DOCUMENTATION FRAMEWORK
Modular sections: CC · HPI · ROS · PMH · SurgHx · FamHx · SocHx · MedHx · AllHx · Vitals · PE · Diagnostic Data · Assessment · Differential · Plan · Orders · Rx · Education · Follow-up · Return Precautions · Provider Attestation. Specialty variations WITHOUT fragmenting the canonical data model.

## 6. AI-ASSISTED DOCUMENTATION RULES
Hermes MAY: transcribe · summarize · extract · draft notes · suggest differentials · identify care gaps · coding suggestions · follow-up reminders · patient-instruction drafts · message drafting · result summarization. **Hermes MUST NOT autonomously:** sign · final diagnoses · prescribe · refills · orders · release critical results · contact emergency services (without the approved escalation) · send clinical messages without authorization · amend signed records · submit claims · override clinician judgment · conceal uncertainty. **Every AI section displays: "AI-generated draft · Clinician review required · Not part of the signed record until approved."** Preserve the distinction: imported facts vs AI interpretation vs clinician-edited vs clinician-authored vs final signed.

## 7. ASSESSMENT & DIFFERENTIAL DESIGN
Structure: Established → Preliminary → Ranked Differential → Must-Not-Miss → Unresolved Questions → Supporting/Conflicting Evidence. Each suggestion: relative likelihood · supporting/against findings · missing info · next steps · evidence source · confidence. **Danger and probability stay separate — a low-probability high-danger diagnosis belongs in must-not-miss, not artificially at the top.**

## 8. MEDICATION RECONCILIATION
Sources: OpenEMR · external EMR · Rx history · pharmacy · patient report · discharge list · facility admin record · claims data. Statuses: active/inactive/discontinued/completed/on-hold/unknown/not-taking/taking-differently/duplicate/historical/unverified. Workflow: import → duplicate matching → conflict ID → patient verification → clinician review → continue/discontinue/modify → final list → signed provenance. **Never silently replace a provider-reviewed list with a new import.**

## 9. ELECTRONIC PRESCRIBING
Flows: new · renewal · refill request · change · discontinuation · cancellation · pharmacy change · formulary alternatives · prior auth · controlled substances · shortages. Checks: correct patient/prescriber · allergies · interactions · duplicate therapy · pregnancy · renal/hepatic dosing · age/weight · max dose · quantity · refills · days' supply · pharmacy · indication · CS status. **AI may draft a prescription proposal but must not transmit it.**

## 10. LABORATORY WORKFLOW
Categories: normal/abnormal/critical/indeterminate/corrected/preliminary/final/cancelled/unable-to-process. Flow: received → patient+encounter matched → reference range → **deterministic critical-value rules** → categorized → provider queue → review → action documented → patient communication documented → closed. **Critical-value detection = deterministic rules or verified source flags — not solely an LLM.**

## 11. IMAGING WORKFLOW
Orthanc · OHIF · ThaiRIS · external PACS · reports · links · critical findings · addenda · comparisons. Display: study description/modality/date/facility/prelim-final/report/addenda/critical status/link/comparisons/follow-up/acknowledgment. **AI may summarize a report but never present the summary as an independent image interpretation unless the imaging-AI is separately validated.**

## 12. CRITICAL & URGENT FINDINGS — escalation levels
Level 1 Routine → 2 Abnormal timely → 3 Urgent → 4 Critical → 5 Immediate emergency. Each: recipients · method · response time · escalation sequence · documentation · closure criteria · failure-to-respond action. Hazards list: critical labs · critical imaging · SI/HI statements · stroke/ACS/sepsis · severe dysglycemia · dangerous vitals · med reactions · high-risk pregnancy · abuse concerns · failed emergency follow-up.

## 13. CLINICAL MESSAGING
Types: admin/scheduling/med-question/refill/symptom/results/post-discharge/advice/urgent/emergency/provider-to-provider/care-team. Safety: identify patient + sender · classify urgency · emergency disclaimers · route by type · escalate dangerous symptoms · preserve originals · document responses · selectable chart inclusion. **Chatwoot = the communication workspace; clinically significant content enters OpenEMR only after review.**

## 14. CLINICAL TASKS
Categories: result review · Rx request · callback · referral follow-up · prior auth · care-gap · discharge follow-up · imaging/lab follow-up · document completion · signature · interface exception · identity review · provider mapping · billing clarification. Each: owner/patient/encounter/priority/due/status/escalation/source/completion criteria/audit.

## 15. SIGNATURE & ATTESTATION
Define who may sign each type · cosignature · supervision · teaching/telehealth attestations · time-based statements · procedure attestations · amendments · late entries. Workflow: draft → review → field validation → warnings → authenticate → sign → LOCKED → outbound sync starts. **A signed note is never silently rewritten by AI, an interface, or another user.**

## 16. AMENDMENTS
Addendum/correction/late entry/retraction/replacement/admin correction/clarification — every change preserves: original content/author/signature + amendment author/time/reason/new content/destination sync status.

## 17. BILLING & CODING BOUNDARY
MAY: ICD-10/CPT/HCPCS suggestions · HCC opportunities · documentation gaps · medical-necessity prompts · E&M support · risk-adjustment review. MUST NOT: unsupported diagnoses · upcoding · silent doc changes · claims without authorized review · infer diagnoses for payment optimization · unnecessary PHI in Perfex.

## 18. POPULATION HEALTH
Discharge · ED follow-up · adherence · chronic disease · screening · vaccination gaps · wellness visits · high-risk outreach · frequent-ED utilization · MIH · home care · RPM. Example: discharge → risk stratify → med-rec task → follow-up appointment → Twilio outreach → Chatwoot conversation → provider reviews → OpenEMR transitional-care encounter → external EMR updated.

## 19. SPECIALTY TEMPLATES
Primary · IM · EM · urgent care · psych · cardiology · pulm · endocrine · derm · weight management · HRT · aesthetics · MIH · home health · post-acute · population health · RPM. **Configurable per tenant WITHOUT allowing customers to bypass core safety controls.**

## 20. TERMINOLOGY & STANDARDS
SNOMED · ICD-10-CM · LOINC · RxNorm · NDC · CPT · HCPCS · UCUM · CVX · US Core · FHIR R4 · C-CDA · USCDI. Own: selection · display names · preferred codes · local mappings · ambiguous-mapping review · version control · no loss of clinical meaning.

## 21. SAFETY CASE (per major feature)
Intended use/users/environment · known hazards · foreseeable misuse · severity · probability · risk controls · verification · residual risk · monitoring · escalation. Hazards: wrong patient/encounter · missed critical · duplicate Rx · wrong dose · stale meds · failed upload · unreviewed AI · wrong attribution · delayed escalation · duplicate chart entry · cross-tenant disclosure.

## 22. HUMAN FACTORS
Reduce: alert fatigue · excess clicks · duplicate documentation · cognitive overload · hidden criticals · ambiguous status · poor mobile readability · unsafe defaults · excessive scrolling · interruptions. Principles: criticals visible · primary actions clear · destructive confirmed · warnings specific · similar patients distinguishable · draft ≠ signed visually · failed sync obvious · offline obvious · uncertainty visible · **no implied success before confirmation.**

## 23. PRODUCT REQUIREMENTS DOCS
PRDs · workflow diagrams · user stories · acceptance criteria · decision tables · data dictionaries · role-permission matrices · escalation matrices · safety requirements · interface requirements · validation plans · release notes · training · SOPs. Example story: "As a prescribing provider, I need to review verified allergies + active medications before transmitting a prescription, so I can identify preventable medication risks." Acceptance: "Given an active allergy, when the provider selects a potentially cross-reactive medication, then the app displays a specific warning, requires acknowledgment, and records it in the audit trail."

## 24. CLINICAL RELEASE APPROVAL
No clinical feature ships until: workflow documented · hazards reviewed · roles enforced · terminology correct · audit met · failure states visible · escalation works · provider testing done · training available · rollback possible · post-release monitoring defined.

## 25-26. EXPERIENCE & BACKGROUND
10+ yrs clinical practice or informatics · EHR workflows · clinical software design · cross-discipline collaboration · med rec · e-prescribing · lab/imaging workflows · documentation · QI · patient safety · translating clinical → technical. Preferred: MD/PA/NP/RN-advanced/PharmD/clinical informaticist — a licensed clinician with product + informatics experience strongly preferred.

## 27. CREDENTIALS
Board cert in clinical informatics (where applicable) · AMIA · CPHIMS/CAHIMS · CPPS · Lean Six Sigma · PMP · HL7/FHIR training · Epic informatics · OpenEMR · med-safety/pharmacy informatics · HIPAA/HITRUST.

## 28. PRACTICAL EXAM
Given a scenario, produce: end-to-end workflow map · patient-safety risk analysis · provider user story · acceptance criteria · role-permission matrix · escalation pathway · med-rec workflow · documentation template · external EMR sync requirements · failure-state design · audit requirements · training outline. **Example scenario:** a recently discharged patient reports dizziness, has an updated med list in the hospital EMR + an older list in OpenEMR + sends a Chatwoot message; the provider is mobile with intermittent connectivity. Explain how NURA identifies the patient, retrieves discharge info, reconciles the lists, triages dizziness, escalates urgent findings, preserves offline work, documents, signs, syncs, and confirms external EMR acceptance.

## 29. FIRST 90 DAYS
**1-30:** workflow inventory · user roles · governance council · documentation lifecycle · patient banner · encounter types · signature requirements · clinical risk register · terminology governance.
**31-60:** med-rec · prescribing · results-review · critical-escalation matrix · clinical messaging · task architecture · AI review requirements · provider prototypes.
**61-90:** validate OpenEMR + external sync workflows · provider usability testing · clinical release checklist · safety incident process · first specialty templates · train teams · approve limited clinical pilot.

## 30. KPIs
Documentation time · clicks/encounter · unsigned-note rate · med-rec completion · critical-result ack time · failed-sync visibility · adoption · satisfaction · wrong-patient incidents · duplicate Rx · unresolved tasks · completeness · AI draft acceptance/correction rates · features with documented safety cases. **Safety targets: wrong-patient chart submissions = 0 · autonomous AI signatures = 0 · unreviewed Rx transmissions = 0 · silent critical-result failures = 0 · cross-tenant disclosures = 0 · signed notes modified without amendment = 0.**

## 31. CREDENTIAL PROFILE
Required: licensed/formerly-licensed clinician · EHR workflow expertise · clinical product design · patient safety · med + prescribing workflows · lab + imaging workflows · precise technical requirements · engineering collaboration · governance. Preferred: informatics training · FHIR/interop · OpenEMR · population health · emergency/acute care · mobile clinical design · AI-assisted documentation · compliance.

## 32. THE JD
The Director of Clinical Product Architecture and Informatics defines the clinical operating model for NURA — converting provider workflows into safe, precise, testable requirements across the mobile app, web app, Hermes, OpenEMR, NextGen Connect, Chatwoot, Twilio, Tavus, e-prescribing, labs, and external EMRs. This role determines how clinicians document once inside NURA, safely review and sign, and sync the final record into any connected EMR without duplicative charting.

**Founder note (08-04):** the next engineering hire = the **Senior AI/ML & Clinical RAG Engineer** — Hermes reasoning, medical evidence retrieval, model routing, evaluations, hallucination controls, and clinical AI safety.
