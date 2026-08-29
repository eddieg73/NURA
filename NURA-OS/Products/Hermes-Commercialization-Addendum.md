# HERMES COMMERCIALIZATION & DEPLOYMENT ADDENDUM (2026-08-04, founder canonical v1.0)

**Final pre-implementation requirements before the clinician pilot. Status: Final. The next phase is IMPLEMENTATION, not brainstorming.**

## 1. TENANT OWNERSHIP & DATA-CONTROL POLICY
Define ownership for: patient records · clinical documentation · agent conversations · clinician preferences · workflow/prompt configs · AI drafts · audit records · derived analytics · de-identified data · model feedback · custom skills/integrations · org knowledge. **Rule:** data_ownership = patient_record/signed_clinical_documentation → healthcare_organization · clinician_private_preferences → clinician-or-org by contract · platform_software/shared_clinical_skills → nuratech · org_customizations/de-identified_analytics → by contract+consent. **Nuratech shall not assume the right to process = ownership.**

## 2. SHARED-NOTHING TENANT BOUNDARY
**Never share:** patient records · conversation history · credentials · local files · API tokens · private prompts · unreviewed feedback · org procedures · internal comms · legal docs · proprietary info. **May share after governance:** validated skills · public knowledge · approved templates · de-identified stats · security updates · safety policies · integration packages · SOPs.

## 3. WORKSPACE PORTABILITY
**Exportable:** clinical records · signed docs · patient comms · audit history · workflow definitions · settings · approved private knowledge · device inventory · integration config · templates. **Non-exportable unless licensed:** source code · proprietary prompts · commercial skills · security rules · routing logic · architecture · other tenants' configs.

## 4. DIGITAL-TWIN BOUNDARIES
**May store:** specialty · licenses · privileges · documentation style · terminology · workflows · hours · notification prefs · order sets · templates · comm prefs. **Shall NOT:** impersonate without disclosure · sign records · fake review · send high-risk comms without authorization · final decisions · extend privileges · cross-apply one clinician's private behavior to another.

## 5. MODEL DRIFT MONITORING
Monitor: accuracy · citation quality · hallucination frequency · provider acceptance/override · per-specialty/population performance · latency · tool errors · schema failures · safety violations · post-update changes. **Response:** restrict the workflow → notify governance → roll back to the prior validated model → investigate → revalidate.

## 6. GOLDEN TEST SET (permanent, mandatory for every release)
Outpatient · critical emergencies · med interactions · allergy conflicts · abnormal labs · critical imaging · pediatric/geriatric/pregnancy · behavioral emergencies · telehealth jurisdiction conflicts · duplicate records · missing consent · identity uncertainty · offline · tool/model failure · prompt injection · malicious documents · cross-tenant attempts.

## 7. ADVERSARIAL CLINICAL RED-TEAM PROGRAM
Test: reasoning failures · unsafe meds · false reassurance · missed emergencies · hallucinated citations · prompt injection · cross-tenant · privilege escalation · patient/clinician impersonation · malicious device data · manipulated imaging metadata · poisoned knowledge docs · social engineering · credential theft · unsafe autonomous tools — every finding = a tracked remediation item.

## 8. CLINICAL GOVERNANCE BOARD (before broad deployment)
Medical director · APP · nursing · pharmacist · privacy/security officers · compliance · healthcare attorney · AI eng lead · quality/patient-safety · HIM · patient rep. Approves: skills · models · incidents · safety metrics · high-risk workflows · complaints · deployment expansion · suspension.

## 9. CLINICAL RISK CLASSIFICATION (per-tier validation/approval/monitoring/human review)
**Tier 0 Administrative** (scheduling · reminders · routing · doc org) · **Tier 1 Clinical Support** (note drafting · summarization · education drafts · evidence retrieval) · **Tier 2 CDS** (differentials · care gaps · med review · lab interpretation support) · **Tier 3 High-Risk** (critical results · emergency triage · med-ordering support · autonomous device response · treatment recs) · **Tier 4 Prohibited without separate authorization** (independent diagnosis/prescribing/treatment/procedure control · unsupervised high-risk patient comms · autonomous irreversible actions).

## 10. REGULATORY CLASSIFICATION ASSESSMENT
Assess: intended use · claims · automation level · clinician independent review · diagnosis/treatment influence · patient-facing vs clinician-facing · device integration · imaging interpretation · autonomous alerts · med recommendations · robot/drone control. **Rule: no regulatory claims until qualified regulatory counsel reviews the classification.**

## 11. LIABILITY & INSURANCE FRAMEWORK
Coverage review: tech E&O · cyber · professional · product · privacy/breach · business interruption · vendor failure · device · robotics/autonomous · international. Contractual: clinician/org/Nuratech/vendor responsibility · indemnification · liability limits · required limits · incident-notification duties · data-loss responsibility.

## 12. SERVICE-LEVEL AGREEMENTS
Define: uptime · support hours · incident response · backup frequency · recovery objectives · notification/escalation targets · maintenance windows · provider-outage handling · escalation path. **SEV-1** patient-safety/major outage → immediate · **SEV-2** major degradation → urgent · **SEV-3** limited → standard · **SEV-4** enhancement → planned.

## 13. SUPPORT & FLEET OPERATIONS (hundreds/thousands of devices)
Remote device health · version inventory · cert-expiration monitoring · remote revocation · update status · disk capacity · local-model status · agent heartbeat · security posture · failed-sync alerts · remote diagnostics · approved remote support · replacement workflow.

## 14-15. HARDWARE BASELINE + NETWORK STANDARDS
**Minimum:** supported Windows · hardware-backed security · full-disk encryption · Secure Boot · endpoint protection · supported browser · storage · reliable network · mic · device certs. **Advanced:** GPU · RAM · local encrypted vectors · local inference · scanner · clinical mic · BLE. Graceful degradation. **Network:** Ethernet · secure Wi-Fi · hotspot · cellular · satellite · high-latency · intermittent · fully offline — resumable sync · bandwidth-aware · chunking · compression · retry/backoff · conflict detection · integrity validation · no repeated full-history sync.

## 16. OFFLINE CLINICAL CONTENT PACKAGE
Emergency protocols · med references · calculators · procedure guides · local formulary · org policies · escalation directory · doc templates · downtime forms · patient education · cached terminology · local safety rules — versioned · signed · timestamped · expiration-aware · auto-updated · clearly identified when outdated.

## 17. FIRST-CLINICIAN PILOT SUCCESS CRITERIA (Eddie's pilot)
Windows→cloud connection · NO cross-tenant leakage · reliable device registration · task delegation · accurate audit · offline completion · resync · tool-permission enforcement · human-approval enforcement · safe failure during outages · backup/restoration · satisfaction · reduced documentation time · acceptable cost/latency · **ZERO unauthorized clinical actions.**

## 18. SECOND-CLINICIAN ISOLATION TEST (the most important architectural test)
B cannot access A's memory/files/API keys/patient records · B cannot impersonate A's agent or register a device in A's tenant · A cannot view B's data · shared skills contain no private pilot data · logs preserve both tenant boundaries · admin access explicitly audited. **No broad deployment until these pass.**

## 19-20. TEMPLATE VERSIONING + REFERENCE DEPLOYMENT PACKAGE
`clinician_template: nura-clinician-standard v1.0.0` (hermes/policy/skills/knowledge/device/model versions) — NEVER provision from an unversioned copy of Eddie's env. Package: compose/K8s manifests · env template · secrets refs · tenant bootstrap · migrations · agent registration · device enrollment · policy/skill/workflow bundles · monitoring · backup · health checks · rollback · test suite · DR instructions.

## 21-22. COMMERCIAL PACKAGING + PRICING GUARDRAILS
**Core** (cloud, workspace, documentation, evidence, standard integrations, audit) · **Edge** (Windows desktop, offline, local files/voice/device/inference) · **Enterprise** (multi-location, SSO, custom workflows, private deploy, analytics, dedicated support) · **Specialty** (radiology · EM · psych · population health · MIH · remote · space/austere). **Safety policies mandatory across ALL tiers.** Track: tokens · GPU · voice/video minutes · storage · vectors · DB · backups · bandwidth · support · integration maintenance · device mgmt · licensing — per-tenant budgets · per-workflow limits · routing thresholds · cost alerts · dashboards · rate limits · emergency override · **no silent degradation.**

## 23-24. FEEDBACK LOOP + NO SILENT LEARNING
Feedback types: helpful/incorrect/unsafe/incomplete/unsupported/wrong-context/citation/workflow/tool/suggestion — linked to model+prompt version · privacy preserved · quality feedback separated from the medical record · safety reports immediate · remediation tracked. **Prohibited:** silent prompt/policy mutation · automatic cross-tenant learning · PHI training without authorization · cross-clinician preference bleed · unreviewed global corrections. **Approved process:** feedback → de-identification → quality review → clinical review → engineering → validation → governance approval → versioned release.

## 25. FINAL BUILD FREEZE + THE DIRECTIVE
**The conceptual architecture is COMPLETE. Do not continue adding services before building the pilot.** Next deliverables: 1) founder-pilot architecture · 2) Hostinger cloud deployment spec · 3) Windows Hermes install package · 4) secure gateway spec · 5) agent identity + device-enrollment workflow · 6) tenant data model · 7) capability registry · 8) structured task envelope · 9) synchronization protocol · 10) pilot test plan · 11) second-clinician isolation test · 12) production-readiness checklist.

**THE BUILD: One Clinician + One Cloud Hermes + One Windows Hermes + Secure A2A + Strict Tenant Isolation + Shared Approved Skills + Private Memory + Complete Auditability = the NURA Hermes REFERENCE DEPLOYMENT. Prove it → convert into the reproducible clinician template → test with the second isolated clinician. Do not scale before isolation, recovery, authorization, and audit testing are complete.**

## THE NURA MAP (the freeze in practice)
- The founder pilot = Eddie's environment = the FIRST tenant (the desktop connect happening TONIGHT = the Windows Hermes + the cloud = the gateway!)
- The 12 deliverables = the immediate build queue — the reference deployment = what we're wiring right now
- The second-clinician isolation test = the next gate after the pilot works
- The freeze means: no more architecture addenda — the next documents are BUILD artifacts, boss.
