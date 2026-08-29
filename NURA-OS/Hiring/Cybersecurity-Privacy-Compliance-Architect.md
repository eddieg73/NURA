# PRINCIPAL CYBERSECURITY, PRIVACY & HEALTHCARE COMPLIANCE ARCHITECT — the role spec (2026-08-04, founder canonical)

**Position:** Principal Cybersecurity, Privacy & Healthcare Compliance Architect
**Alt:** CISO / Director of Healthcare Cybersecurity and Privacy / Principal Zero-Trust Security Architect / Chief Security, Privacy and Trust Officer / Director of DevSecOps and Clinical Information Security
**Reports to:** Director of Security & Compliance · **Funnel:** the AI hiring manager · **Signer:** the founder

## 1. MISSION
Establish, operate, and continuously improve the security, privacy, resilience, and compliance program protecting the NURA ecosystem: Hermes kernel · Flutter + web apps · OpenEMR · Perfex · Chatwoot · NextGen · Twilio · Tavus · Orthanc/OHIF/ThaiRIS · e-Rx · clinical AI/RAG · MCP services · Hostinger VPS · Docker/K8s · databases · object storage · backups · external EMRs · medical devices · workstations/mobile · customer environments. **Cybersecurity failures = potential patient-safety events** whenever they could delay care, corrupt documentation, expose PHI, disable workflows, alter prescriptions, interfere with critical-result delivery, or place information in the wrong patient's chart.

## 2. SECURITY AUTHORITY (documented + executive-supported)
Block a production release · suspend a compromised account · revoke credentials · disable an unsafe integration · isolate a compromised server · quarantine a container · suspend an AI tool · require emergency patching · trigger incident response · require trusted-backup restoration · escalate privacy incidents · require vendor remediation · reject insecure architecture · deny unsupported exceptions · require pen-tests · require corrective-action plans. **Findings must not be overruled solely to meet a release deadline.**

## 3. GOVERNANCE FRAMEWORK
HIPAA Security + Privacy Rules · HITECH · NIST CSF 2.0 · SP 800-53/800-66/800-207 (Zero Trust) · HHS HICP + CPG · HITRUST CSF · ISO 27001/27017/27018 · SOC 2 · CIS Controls + Benchmarks · OWASP ASVS/MASVS/API Security/Top 10/LLM+agentic guidance · PCI DSS where card data · state privacy/breach laws · contractual obligations.

## 4. SECURITY PROGRAM ORGANIZATION
Executive Leadership → Principal Architect → Security Engineering · IAM · Application Security · Cloud/Infra Security · Security Operations · Privacy Engineering · GRC · Incident Response — alongside the Clinical Safety Officer · Privacy Officer · Legal · Platform · DevSecOps · Clinical Informatics · QE. **Early stage: one senior leader may combine functions — responsibility + authority stay explicit.**

## 5. ZERO-TRUST ARCHITECTURE
No implicit trust for any user/device/service/container/app/segment. **Principles:** verify every identity · authenticate every service · authorize every request · evaluate device posture · least privilege · short-lived credentials · segment systems · assume breach · inspect east-west traffic · continuously monitor · revoke rapidly · record high-risk actions · reauthenticate before privileged ops · restrict by tenant/patient/purpose/role/workflow. **Decision inputs:** user/device identity + compliance · tenant · role · patient/encounter context · requested action · resource sensitivity · network/geographic/session risk · auth strength · time · historical behavior.

## 6. IAM (humans, apps, services, agents, machines)
**Human:** unique named accounts · MFA · passkeys · hardware keys for privileged · RBAC/ABAC · PAM · JIT + time-limited elevation · session expiry · device registration · automated offboarding · periodic access reviews · separation of duties · break-glass · auth-event monitoring. **Service:** unique identity · owner · purpose · minimum scope · short-lived credentials · rotation · no interactive login · environment-specific · tenant restrictions · full audit. **Prohibited:** shared admin/dev accounts · reused passwords · creds via chat · routine root · permanent unrestricted tokens · prod creds in source · one integration credential across customers · unmonitored emergency accounts.

## 7. PRIVILEGED ACCESS MANAGEMENT
Privileged surfaces: Hostinger · Linux root · K8s · Docker · DBs · DNS · CAs · secrets · GitHub org · production deploy · backup deletion · audit-system admin · OpenEMR · NextGen · IdP. **Controls:** separate privileged accounts · hardware MFA · approval where appropriate · time-limited · session recording where lawful · activity logging · no standing prod privileges for developers · quarterly entitlement review · immediate revocation on role change · secure break-glass · dual authorization for destructive actions. **No single employee can simultaneously: change prod code + delete prod data/backups + alter audit records + disable monitoring.**

## 8. NETWORK SECURITY ARCHITECTURE
Connect: VPS nodes · AWS · RunPod · clinical facilities · remote devs · customer EMRs · HIEs · labs · PACS/RIS · mobile · support · backups. **Controls:** private service networks · WireGuard VPN · site-to-site · bastion · egress/ingress filtering · segmentation · management separation · DB isolation · container network isolation · WAF · DDoS · DNS security · rate limiting · IP reputation · mTLS · private API endpoints · firewall-as-code · continuous rule review. **Zones:** Public Edge → Reverse Proxy/WAF → App Services → Clinical Integration → AI/Model Services → DBs → PACS/Imaging → Admin → Security Monitoring → Backup/Recovery → Dev/Test → Air-Gapped Recovery. **Clinical, crypto, dev, and corporate systems never share unrestricted network access.**

## 9. HOSTINGER / LINUX HARDENING
Supported distro · minimal packages · SSH keys only · root SSH login disabled · password SSH disabled where feasible · host firewall · controlled auto-updates · file-integrity monitoring · EDR · malware protection · centralized logging · NTP · secure boot where supported · admin via VPN/bastion · CIS-aligned · backup agent · vuln scanning · drift monitoring · disk-encryption evaluation · resource/process monitoring. **No publicly exposed admin panels without strong identity-aware controls.**

## 10. DOCKER / CONTAINER SECURITY
**Build:** approved minimal base images · version pinning · multi-stage · dependency/malware/secret scanning · SBOM · image signing · provenance · private registry · build isolation. **Runtime:** non-root · read-only FS where practical · dropped capabilities · seccomp · AppArmor/SELinux · resource limits · health checks · isolated networks · no Docker socket exposure · no privileged containers without documented exception · restricted mounts · runtime threat detection · centralized logs · automated quarantine. **Orchestration:** namespace isolation · network policies · pod security standards · admission policies · secrets integration · workload identity · signed-image enforcement · quotas · audit · control-plane hardening · backup/recovery.

## 11. APPLICATION SECURITY (SDLC-embedded)
Requirement → threat model → security acceptance criteria → design review → development → SAST → dependency/secret scanning → automated security tests → manual review → pen-test where required → security approval → production monitoring. **Controls:** server-side authorization · input validation · output encoding · parameterized queries · CSRF/XSS/SSRF defenses · file-upload + path-traversal controls · secure sessions · rate limiting · replay protection · idempotency · secure errors · API schema validation · webhook signature validation · secure logging · cryptographic integrity. OWASP Top 10 = the reference standard.

## 12. API & MCP SECURITY
OAuth2/OIDC · mTLS where appropriate · short-lived tokens · audience/issuer/scope/tenant/patient-context validation · schema validation · rate limits · size limits · webhook signing · replay prevention · correlation IDs · versioning · deprecation policy · complete audit. **Every MCP tool defines:** permitted users/agents · role · tenant · patient context · read/write · reversibility · approval · rate limit · timeout · data classification · audit fields · error behavior · emergency-disable mechanism. **Agents never get unrestricted shell/DB/email/clinical access merely because a tool can technically provide it.**

## 13. AI & AGENTIC SECURITY
Protect: Hermes · RAG · routing · tool calling · memory · prompt registries · ingestion · providers · local models · Tavus avatars · AI comms · autonomous agents. **Controls:** prompt-injection + indirect-injection defense · tool allowlists + parameter validation · least-privilege agents · human approval for high-risk actions · output validation · context/patient/tenant isolation · retrieval-source validation · provider review · retention · PHI redaction · secret filtering · iteration/token/cost limits · memory expiration · poisoning detection · model/prompt versioning · AI incident logging · emergency disablement. **Prohibited:** unrestricted prod DB access · self-permission changes · self-approval · retrieved docs overriding policy · identifiable PHI to unapproved models · secrets in prompts · unvalidated generated commands · AI deleting audit records · AI signing notes/prescriptions autonomously.

## 14. CLINICAL DATA / PHI PROTECTION
Classify: demographics · MRNs · diagnoses · meds · labs · imaging · notes · behavioral health · substance-use · insurance · billing · biometrics · audio/video · transcripts · device data · location · messages. **Controls:** minimum necessary · encryption in transit/at rest · fine-grained/field-level authorization · secure deletion · retention · export controls · watermarking · download/copy/print controls · access auditing · break-glass monitoring · DLP · deidentification · tokenization · tenant-specific encryption.

## 15. ENCRYPTION & KEY MANAGEMENT
TLS/mTLS · DB/object-storage/mobile/backup encryption · message encryption · document/code/image signing · digital signatures · VPN tunnels. **Keys:** centralized management · environment/tenant separation · HSM where warranted · rotation · revocation · use auditing · dual control for critical keys · offline recovery keys · no keys beside encrypted data · no private keys in repos · documented compromise procedure.

## 16. SECRETS MANAGEMENT
API keys · DB passwords · OAuth secrets · signing keys · Twilio/Tavus/OpenEMR/NextGen/SMTP/cloud credentials · VPN keys · certificates. **Controls:** Vault-class manager · short-lived dynamic credentials where possible · automated rotation · scoped · environment isolation · no plaintext .env in repos · secret scanning · access logging · emergency revocation · ownership records · expiration monitoring.

## 17. MOBILE SECURITY (with the Flutter developer)
OAuth PKCE · secure token storage (Secure Enclave/Android Keystore) · biometric reauth · device registration/attestation · cert validation · root/jailbreak detection · local DB encryption · remote revocation · selective wipe · screen-lock · PHI-safe notifications · secure deep links · screenshot/clipboard policy · secure logging · mobile security testing. **Prohibited:** API secrets in Dart · tokens in ordinary preferences · PHI in crash logs/push (unless policy permits) · disabled TLS · production PHI in dev builds · permanent offline access without expiration.

## 18. OPENEMR SECURITY
Supported version + patch management · strong auth · RBAC · API scope restrictions · audit logging · secure FHIR · no direct public DB access · no shared admin accounts · no direct DB writes by apps · secure document storage/backups · session controls · vuln scanning · tenant deployment isolation.

## 19. NEXTGEN CONNECT SECURITY
Admin restricted to VPN · strong admin auth · separate customer credentials · mTLS where supported · SFTP key management · channel-level least privilege · protected message store · PHI-safe logs · environment separation · cert monitoring · secure DB · retention policy · controlled reprocessing · change control + version control · production access monitoring. **Interface messages never retained indefinitely just because the engine supports it.**

## 20. COMMUNICATIONS SECURITY
**Chatwoot:** restricted admin · signed webhook validation · secure attachments · role enforcement · conversation access controls · controlled patient matching · retention · no automatic full-chart ingestion. **Twilio:** master creds server-side · short-lived client tokens · webhook signature validation · phone-number access restrictions · recording consent/encryption/retention · fraud monitoring · SMS minimization · emergency-use limitations. **Tavus:** keys server-side · short-lived session creds · AI disclosure · consent · video/transcript retention controls · human escalation · no autonomous clinical decisions · approved processing terms.

## 21. E-PRESCRIBING / EPCS SECURITY
Prescriber identity · proofing · MFA · CS signing · credential issuance/revocation · device enrollment · Rx integrity · audit · vendor integration · session security · delegation boundaries. **Never recreate certified EPCS signing controls independently. Never store a prescriber's signing factor so another person/agent can use it.**

## 22. PACS / RIS / IMAGING SECURITY
Orthanc · OHIF · ThaiRIS · DICOM/DICOMweb · reports · exports · worklists. **Controls:** private network access · authenticated DICOMweb · role-based study access · tenant/facility segregation · metadata review · secure sharing · time-limited viewer links · download controls · audit · retention · deidentification workflow · malware scanning of imports · **no unrestricted public Orthanc interface.**

## 23. MEDICAL DEVICE / BLUETOOTH SECURITY
Device identity · approved registry · secure pairing · encrypted transport · firmware inventory + signature verification · device certs where available · BLE security · replay resistance · input validation · measurement provenance · device revocation · calibration status · lost-device handling · integrity checks. **Consumer/unverified device data never presented as equivalent to approved clinical device data.**

## 24. LOGGING / SIEM / MONITORING
Monitor: auth · privileged activity · API/MCP tool activity · DB access · OpenEMR/NextGen changes · exports · Rx actions · AI activity · model requests · PHI downloads · backup changes · firewall/container/endpoint/DNS/VPN events · DLP indicators. **Tech:** Wazuh · Security Onion · Suricata · Zeek · OpenSearch/Elastic · Grafana/Loki · OTel · Falco · CrowdSec · OSQuery. **Priorities:** informational → low → moderate → high → critical → patient-safety emergency.

## 25. VULNERABILITY MANAGEMENT (continuous)
Asset inventory · scanning (vulnerability/dependency/container/cloud-config/web/mobile/API) · external attack surface · pen-tests · remediation tracking · exception management · executive reporting. **Targets:** actively exploited critical = immediate · critical internet-facing = 24-72h · other critical = 7d · high = 30d · moderate = risk-based. Exceptions carry: system · vuln · risk · compensating control · owner · expiration · approval.

## 26. THREAT MODELING (required for)
New apps/APIs/MCP tools/AI agents/EMR integrations/mobile features/e-Rx/devices/uploads/cloud vendors/major changes. **Categories:** spoofing · tampering · repudiation · disclosure · DoS · privilege escalation · prompt injection · model poisoning · cross-tenant · wrong-patient routing · unauthorized clinical action · audit destruction · supply-chain compromise.

## 27. SECURITY TESTING
SAST · DAST · IAST where appropriate · SCA · secret scanning · IaC scanning · container scanning · API/mobile security testing · pen-tests · red-team · AI/agentic red-teaming · social-engineering exercises · backup restoration exercises · tabletop exercises. **No test result resolved until remediation is verified.**

## 28. INCIDENT RESPONSE
Plan covers: PHI exposure · ransomware · credential compromise · unauthorized access · malware · corruption · EMR misrouting · wrong-patient disclosure · Rx compromise · AI leakage · injection · provider compromise · insider threat · lost device · vendor breach · backup compromise · outage · DoS. **Lifecycle:** prep → detection → triage → containment → evidence preservation → eradication → recovery → notification analysis → post-incident review → corrective action. **Roles:** incident commander · security/technical lead · privacy officer · clinical safety lead · legal · comms · customer liaison · documentation lead.

## 29. BREACH / PRIVACY INCIDENT ASSESSMENT
Evaluate: info involved · actually acquired/viewed · recipients · mitigation · affected count · jurisdictions · contractual/regulatory obligations · patient-safety consequences. **Technical staff preserve facts; legal conclusions coordinated with qualified counsel + the designated Privacy Officer.**

## 30. DIGITAL FORENSICS
Log preservation · disk-image + memory capture · container/cloud/mobile/network evidence · chain of custody · hash verification · time sync · legal hold · external forensic support · evidence access control. **Routine remediation must not destroy evidence before the incident commander authorizes it.**

## 31. BCDR
Protect against: ransomware · corruption · VPS/region failure · credential compromise · backup deletion · provider failure · attack · accidental deletion. **Controls:** encrypted + immutable + offline backups · geographic separation · tested restoration · RPO/RTO · clean-room restoration · backup access separation + deletion protection · DR exercises. **A backup never restored/tested is not a reliable recovery mechanism.**

## 32. AIR-GAPPED RECOVERY
Offline/logically isolated backups · separate admin credentials · offline root-of-trust · malware-scanning station · controlled media transfer · cryptographic verification · recovery docs · emergency comms plan · IaC copies · critical images · license info. **Never shares unrestricted credentials with production.**

## 33. VENDOR & THIRD-PARTY RISK
Review vendors handling: PHI · records · voice/video/transcription · AI · storage · backups · Rx · payments · messaging · support · analytics. **Requirements:** security questionnaire · architecture/data-flow review · BAA determination · subprocessors · data location · encryption · access control · incident-notification terms · retention/deletion · pen-test evidence · SOC 2 or equivalent · BCP · exit plan.

## 34. BAAs
Assess for: hosting/cloud · AI model providers · Twilio · Tavus · support · backups · transcription · analytics · e-Rx · interface · customer-support platforms. **No vendor receives PHI before contractual, security, and technical controls are approved.**

## 35. RETENTION & DESTRUCTION
For: records · drafts · audit logs · interface/chat messages · voice/video/transcripts · AI prompts/responses · backups · security logs · tickets · failed uploads · temp files. **Controls:** defined periods · legal hold · tenant-specific requirements · secure deletion · backup expiration · destruction verification · deletion logs · vendor deletion confirmation. **"Keep everything forever" is not acceptable.**

## 36. PRIVACY ENGINEERING
Purpose limitation · minimization · minimum necessary · role-based access · transparency · consent where required · access accounting · correction workflows · retention limits · secure deletion · deidentification · patient-access support · export controls · privacy-preserving analytics. **Review triggers:** new data category/AI provider/communication channel/mobile permission/biometric use/recording feature/sharing partner/geographic market/analytics/device.

## 37. COMPLIANCE EVIDENCE MANAGEMENT
Evidence: policies · procedures · risk assessments · architecture · asset inventories · access reviews · training · vuln reports · pen-tests · backup tests · incident exercises · vendor assessments · change tickets · security test results · audit logs · encryption evidence · baselines · corrective-action records — **centralized, versioned, access-controlled, mapped to frameworks.**

## 38. RISK REGISTER
ID · asset · threat · vulnerability · likelihood · impact (patient-safety/privacy/financial) · existing controls · residual risk · owner · remediation · due date · acceptance authority · review date. **Risk acceptance is explicit, time-limited, business-owner-authorized — never silently assumed by engineering.**

## 39. SECURITY POLICIES (the library)
Information security · acceptable use · access control · passwords/auth · privileged access · data classification · encryption · key/secrets management · vulnerability/patch management · secure development · change management · incident response · BCDR · vendor management · mobile devices · remote access · logging/monitoring · retention · media destruction · AI security · device security · backup security · physical security.

## 40. SECURITY AWARENESS (role-specific)
**All:** phishing · MFA · PHI handling · secure comms · lost devices · incident reporting · social engineering · remote work. **Developers:** secure coding · secrets · API security · tenant isolation · dependency risk · AI security · logging restrictions · threat modeling. **Admins:** privileged access · Linux/container hardening · backup security · incident preservation · change control. **Clinicians:** patient-context verification · secure messaging · mobile safety · e-Rx security · AI limitations · break-glass · suspicious-activity reporting.

## 41. SECURITY METRICS
Critical/high vulns · patch compliance · MFA adoption · privileged/dormant accounts · failed logins · suspicious sessions · endpoint/asset coverage · backup + restore success · MTTD/MTTC/MTTR · phishing performance · vendor assessments · open risks/exceptions · cross-tenant findings · AI security events · PHI exposure events.

## 42. SECURITY RELEASE GATES (block when)
Critical vuln unresolved · tenant isolation unproven · client-side-only authorization · secrets in code · missing audit logging · PHI to unapproved vendor · missing encryption · high-risk MCP tool without authz controls · known injection → unauthorized action · wrong-patient vulnerability · no backup/rollback · failed pen-test · incomplete EPCS controls · EMR routing could disclose incorrectly.

## 43. PRACTICAL EXAM
Given the NURA architecture package, deliver: threat model · data-flow diagram · zero-trust architecture · network-segmentation design · IAM + privileged-access plan · container security standard · API/MCP security standard · AI + injection controls · PHI data-flow assessment · IR plan · backup/ransomware recovery plan · vendor-risk assessment · HIPAA risk-analysis outline · security release checklist · 90-day remediation roadmap. **Then identify + remediate:** publicly exposed admin interface · shared SSH credential · prod secret in source · overprivileged container · cross-tenant API vuln · unsigned webhook · weak backup permissions · injection path · PHI in app logs · unrestricted MCP tool · insecure external EMR connection · missing audit event.

## 44-46. EXPERIENCE & CREDENTIALS
10+ yrs cybersecurity/infra/privacy/risk · 5+ yrs cloud/SaaS security · healthcare cybersecurity + HIPAA Security Rule · secure SDLC · cloud/container · IAM · IR · vuln mgmt · vendor risk · security architecture · pen-test interpretation · audit/compliance evidence · executive communication. Preferred: multi-tenant healthcare SaaS · OpenEMR · NextGen · FHIR/HL7 · PACS/DICOM · e-Rx · Twilio/comms security · LLM/agentic AI security · K8s · Hostinger-class VPS · HITRUST · SOC 2 · ISO 27001 · medical-device security · clinical IR. Credentials: CISSP/ISSAP/CISM/CCSP/SABSA · OSCP/OSCE · GCIH/GCFA · CKS · AWS Security Specialty · HCISPP · CIPP/CIPM · CRISC · ISO 27001 Lead Implementer/Auditor · HITRUST CSF Practitioner · SOC 2 experience — **supplement, never replace, demonstrated capability.**

## 47. FIRST 90 DAYS
**1-30 (discovery/containment):** asset inventory · PHI data-flow map · privileged-access + secrets inventory · public-exposure review · VPS/Docker/OpenEMR/NextGen security reviews · AI vendor usage · critical-risk register · remediate immediate exposures · incident contacts.
**31-60 (foundation):** IdP standards · MFA everywhere · PAM · secrets management · centralized logging · vuln scanning · secure baselines · network segmentation · vendor-review process · security release gates · initial HIPAA risk analysis.
**61-90 (operational):** pen-test · ransomware tabletop · backup restoration test · AI security controls · MCP tool governance · SIEM alerts · IR procedures · staff training · corrective-action plan · executive security roadmap · approve/conditionally approve the clinical pilot.

## 48. KPIs
Assets inventoried · MFA coverage · time-limited privileged access · centrally managed secrets · containers scanned · critical-vuln remediation time · patch compliance · backup/restore success · logging coverage · MTTD/MTTC · access-review completion · vendor-assessment completion · pen-test remediation · training completion · expired exceptions · cross-tenant findings · unapproved PHI flows · unauthorized AI tool calls · prod secrets in code. **Safety targets: cross-tenant = 0 · wrong-patient = 0 · unencrypted PHI transmissions = 0 · shared prod admin accounts = 0 · unapproved model providers receiving PHI = 0 · unlogged privileged actions = 0 · unrestricted public clinical DBs = 0 · unprotected backups = 0 · autonomous AI privilege escalation = 0.**

## 49-50. PROFILE + THE JD
Required: healthcare security leadership · HIPAA security/privacy · zero-trust · IAM/PAM · cloud/Linux/container security · secure SDLC · IR · vuln mgmt · PHI data-flow protection · vendor risk · compliance evidence · executive communication. Preferred: CISSP/CISM-class · HITRUST · ISO 27001 · SOC 2 · K8s · OpenEMR/NextGen · clinical AI security · FHIR/HL7/DICOM · EPCS · multi-tenant healthcare SaaS.
**The JD:** leads the security and trust program for the NURA clinical platform — with authority to block unsafe releases, isolate compromised systems, revoke access, suspend vulnerable integrations, and require remediation. **The objective: NURA stays secure, private, resilient, auditable, and clinically safe as it grows from an internal platform into a multi-tenant healthcare technology company.**
