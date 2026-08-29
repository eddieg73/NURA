# PRINCIPAL AI/ML, CLINICAL RAG & MODEL ORCHESTRATION ENGINEER — the role spec (2026-08-04, founder canonical)

**Position:** Principal AI/ML Engineer for Clinical RAG and Agent Orchestration
**Alt:** Lead Clinical AI Engineer / Principal Medical LLM Engineer / Director of Clinical AI Systems / Senior AI Agent and Retrieval Architect / Hermes Intelligence Platform Lead
**Reports to:** VP AI Engineering · **Funnel:** the AI hiring manager · **Signer:** the founder

## 1. MISSION
Design, build, evaluate, secure, and maintain the intelligence layer of the Hermes Platform Kernel — ensuring NURA's AI is: evidence-grounded · clinically constrained · traceable · versioned · measurable · auditable · cost-controlled · hallucination-resistant · injection-protected · clinician-supervised · appropriate for the workflow. Build the systems that retrieve evidence, reason across structured + unstructured clinical data, call approved tools, generate drafts, route among specialized agents, and escalate to humans when required.

## 2. CORE OWNERSHIP
Clinical RAG · medical knowledge ingestion · embedding pipelines · vector search · hybrid retrieval · reranking · knowledge graphs · prompt + policy management · model routing · multi-agent orchestration · tool calling · MCP integration · clinical output schemas · confidence/uncertainty · AI evaluation · hallucination reduction · safety guardrails · human-review workflows · token/cost optimization · local + hosted model deployment · AI observability · AI incident investigation.

## 3. HERMES INTELLIGENCE ARCHITECTURE
NURA apps → Hermes AI Gateway → identity/tenant/patient validation → clinical policy engine → intent classification → workflow + agent selection → knowledge retrieval → tool execution → model routing → structured-output validation → safety + evidence review → human approval where required → OpenEMR/Chatwoot/Perfex/external EMR workflow. A governed intelligence platform, not a chatbot.

## 4. CLINICAL AI OPERATING MODEL
Preserve boundaries: data retrieval vs interpretation vs reasoning support vs recommendation vs provider decision vs authorization vs signing vs order execution vs Rx transmission. **Hermes may assist but never obscure who made the final decision.**
**Permitted:** summarize records · draft notes · extract facts · identify missing documentation · suggest differentials · must-not-miss · summarize lab/imaging · identify med discrepancies · retrieve literature · draft patient instructions/messages · recommend follow-up · coding suggestions · care gaps · prioritize queues.
**Restricted (never autonomous):** sign notes · final diagnosis · transmit Rx · place orders · release critical findings · definitive patient advice · amend signed records · approve claims · override deterministic safety rules · bypass clinician review · sole basis for an emergency decision.

## 5. CLINICAL RAG ARCHITECTURE
Pipeline: request → patient/encounter context → query classification → rewriting → source selection → semantic + keyword retrieval → metadata filtering → reranking → evidence extraction → context assembly → generation → citation/grounding validation. Methods: dense vector · sparse keyword · hybrid · metadata filter · semantic + cross-encoder rerank · graph · temporal · patient-specific · terminology expansion · query decomposition · multi-hop.

## 6. MEDICAL KNOWLEDGE SOURCES
Public: PubMed/PMC · ClinicalTrials.gov · FDA drug/device · DailyMed · MedlinePlus · CDC · NIH · CMS · AHRQ · USPSTF · RxNorm · LOINC · SNOMED · ICD-10 · NDC · NLM terminology. Licensed: OpenEvidence · UpToDate/DynaMed (where licensed) · Elsevier · Lexicomp · Micromedex · society guidelines · institutional protocols. Internal: NURA policies · workflows · SOPs · templates · pathways · formulary · critical-value policies · escalation procedures · deidentified QI data. Maintain provenance, licensing boundaries, version dates, tenant restrictions.

## 7. KNOWLEDGE INGESTION PIPELINE
Source → license/access validation → download → malware/file validation → text/metadata extraction → classification → clinical sectioning → chunking → terminology normalization → embeddings → indexing → quality validation → publication. Metadata per object: source title/publisher/author/dates/URL/type/specialty/population/evidence level/jurisdiction/language/license/tenant visibility/version/expiry/embedding + chunking + pipeline versions.

## 8. CLINICAL CHUNKING
Never arbitrary fixed-size only. Segment by heading/recommendation/population/indication/contraindication/dose/monitoring/evidence grade/question/procedure step/warning/table/figure/reference. Medication monographs preserve: med-indication-dose-route-frequency-age-weight-renal-hepatic-contraindication-interaction-monitoring-pregnancy-adverse-effects.

## 9. PATIENT-SPECIFIC CONTEXT RETRIEVAL
Sources: OpenEMR · external EMR · FHIR · labs · meds · allergies · problems · notes · imaging · discharges · messages · care plans · prior auths · claims (permitted) · RPM. Rules: verify tenant/user/patient · limit to the active task · minimum necessary · avoid unrelated historical PHI · preserve timestamps · distinguish current vs stale · identify conflicts · provenance · redact before external queries.

## 10. PHI CONTROLS
Classification · prompt redaction · data minimization · tenant model policy · vendor BAA · regional routing · encryption · access logging · retention · zero-retention where available · deidentification · synthetic testing · output redaction · consent/purpose enforcement. **External evidence query rule: the clinical question, never identifiers.** Unsafe: "John Smith, DOB ..., creatinine 2.1 — what antibiotic?" Safer: "Evidence-based oral antibiotic options for an older adult with reduced renal function and uncomplicated UTI." Application happens inside the protected environment.

## 11. MODEL ROUTING
Classification → small/low-latency · extraction → deterministic/constrained · summarization → high-accuracy · evidence synthesis → advanced + RAG · coding → terminology-aware + rules · speech → medical speech model · image/doc → multimodal · offline → quantized local · bulk → cost-optimized · high-risk → strongest + human review. Factors: risk · latency · context · cost · availability · tenant policy · sensitivity · BAA · language · tools · structured-output reliability · eval score · load.

## 12. MODEL PLATFORMS
OpenAI · Anthropic · Gemini · Llama · Qwen · Mistral · DeepSeek (approved) · Ollama · vLLM · HF · RunPod · AWS Bedrock · self-hosted clinical. **No model enters production on demo performance alone — it passes the defined evals for the intended use.**

## 13. MULTI-AGENT ARCHITECTURE
Hermes Supervisor → Documentation · Evidence Retrieval · Medication Reconciliation · Laboratory Review · Imaging Report · Coding Support · Care-Gap · Patient Communication · Referral · Population Health · Interface Exception · Compliance Review agents. Each: purpose · allowed inputs/tools · prohibited actions · output schema · escalation · max iterations · token budget · timeout · audit · eval suite · version.

## 14. AGENT PERMISSION MODEL (tool allowlists)
Documentation Agent MAY: read authorized chart data, retrieve evidence, draft, save draft, create review task. MAY NOT: sign, send to external EMR, prescribe, order, delete source records, change permissions. Patient Communication Agent drafts — authorization required before sending clinical content.

## 15. MCP RESPONSIBILITIES
Build/govern MCP for OpenEMR · NextGen · Chatwoot · Perfex · Twilio · Tavus · Orthanc · OHIF · ThaiRIS · PubMed · FDA · DailyMed · OpenEvidence · terminology · Postgres · Qdrant · Redis · S3 · GitHub · policy repos. Every tool defines: name · purpose · input/output schema · required role + tenant scope · patient-context requirement · read/write · reversibility · approval · rate limit · timeout · audit · error behavior.

## 16. PROMPT ARCHITECTURE (prompts = versioned software)
Components: system policy · role · boundaries · tool permissions · output schema · evidence + uncertainty requirements · escalation · prohibitions · tenant + specialty instructions · citation rules. Governance: versioned · peer-reviewed · tested · CI/CD-released · model-version associated · eval-associated · reversible · auditable. **No manual production prompt edits.**

## 17. STRUCTURED CLINICAL OUTPUT CONTRACT
{request_id, tenant_id, patient_id, encounter_id, workflow, status:"draft", facts[], patient_reported_information[], clinical_interpretations[], ranked_differential[], must_not_miss[], recommendations[], uncertainties[], missing_information[], evidence[], safety_flags[], model{provider,name,version}, prompt_version, retrieval_version, created_at, requires_clinician_review:true}. **The model never validates its own output — a separate schema validator + policy engine.**

## 18. CONFIDENCE & UNCERTAINTY
Never present unsupported numeric confidence as scientific certainty. Express: evidence strength · retrieval quality · completeness · contradictions · missing data · model/guideline disagreement · temporal staleness · applicability. Example: "Evidence support: Moderate · Data completeness: Limited · Key uncertainty: current renal function not available · Clinician review: Required."

## 19. HALLUCINATION REDUCTION
Retrieval-before-generation · source whitelisting · citation validation · claim-to-source matching · structured output · terminology + medication DB validation · rule checks · abstention · multi-model comparison · human review · contradiction + staleness detection · post-generation fact-checking. **The model may state the information is insufficient.**

## 20. EVIDENCE CITATION
Each significant claim links to: source · date · passage · recommendation strength · evidence grade · population applicability · retrieval/rerank scores · source version. UI lets the provider inspect evidence without exposing internal reasoning.

## 21. PROMPT-INJECTION DEFENSE
Attack surfaces: notes · documents · websites · emails · messages · PDFs · API responses · FHIR · DICOM metadata · external knowledge. Defenses: retrieved content = data not policy · system/retrieved separation · sanitized tool outputs · restricted tools · URL/destination validation · write-approval · instruction-like detection · max tool depth · secret retrieval blocks · tenant boundaries · suspicious-content recording · red-teaming.

## 22. DETERMINISTIC CLINICAL SAFETY LAYER
LLMs are not the only mechanism for high-risk checks. Deterministic rules for: critical labs · allergies · duplicate meds · interactions · max doses · renal/pediatric dosing · pregnancy contraindications · CS restrictions · emergency escalation · required authentication · wrong-patient · duplicate submission. **Rules versioned + separately testable.**

## 23-26. EVALUATION FRAMEWORK
Categories: factual accuracy · relevance · grounding · citation correctness · completeness · hallucination rate · safety · bias · terminology · structured validity · tool-selection · patient-context · wrong-patient resistance · injection resistance · latency · tokens · cost · provider acceptance/correction.
**Dataset:** synthetic + deidentified + typical/complex/rare + must-not-miss + conflicts + incomplete + med errors + abnormal/critical labs + imaging + pediatric/geriatric/pregnancy/psych + multilingual + adversarial + injection — each with expert-reviewed rubrics.
**Golden sets per workflow** (summarization, med-rec, differentials, classification, discharge extraction, coding, triage, referrals, care gaps, escalation, retrieval) — changes ship only above thresholds.
**Human evaluation:** blinded clinical review — correctness · completeness · usefulness · harm potential · unsupported statements · missed urgent diagnoses · evidence/documentation quality · time saved · corrections. **Disagreement is analyzed, not averaged away.**

## 27. AI RELEASE PROCESS
Proposed change → automated unit/retrieval/safety evals → adversarial → clinical expert review → shadow deployment → limited pilot → production approval → post-release monitoring. High-risk workflows: staged rollout + rollback.

## 28. AI OBSERVABILITY
Requests by workflow · model · prompt version · retrieval sources/quality · schema failures · tool-call failures · hallucination indicators · citation failures · provider edits/rejections · escalation rate · latency · tokens · cost · cache hit · agent loops · timeouts · safety violations. **No PHI in general telemetry without approved safeguards.**

## 29. AI INCIDENT RESPONSE
Events: unsafe recommendation · hallucinated citation · wrong-patient · cross-tenant · unauthorized tool · injection · leakage · provider outage · unexpected behavior · excessive cost · infinite loop · corrupted index · stale guideline · escalation failure. Actions: disable workflow · preserve logs · identify impacted requests · notify clinical safety · determine patient impact · roll back · correct index · RCA · update evals · validate before reactivation.

## 30. LOCAL & SELF-HOSTED MODELS
Ollama · vLLM · RunPod · K8s · Docker · GPU servers · quantized mobile · Core ML · ONNX · llama.cpp. Uses: offline dictation · local summarization · low-risk classification · PHI-sensitive workloads · bulk background · cost · outage resilience. **A local model is not automatically safer — it still needs evaluation, access control, patching, monitoring, governance.**

## 31. SPEECH & VOICE AI
Medical dictation · diarization · real-time/telephone transcription · ambient documentation · multilingual · clinical vocabulary · audio quality · consent · redaction · transcript confidence. Tech: Whisper variants · medical speech APIs · self-hosted · Twilio media streams · WebRTC. **The transcript stays distinct from the clinician-approved note.**

## 32. MULTIMODAL
Scanned docs · forms · lab PDFs · discharge extraction · insurance cards · medication labels · photo classification · imaging report summarization. **Independent diagnostic image interpretation requires separate validation, governance, intended use, and possibly regulatory analysis.**

## 33. AI MEMORY ARCHITECTURE
Distinguish: prompt context · conversation memory · workflow state · patient longitudinal · provider preferences · tenant policies · clinical knowledge · operational memory. Rules: patient-scoped · tenant-isolated · provenance · stale expiry/review · signed records never overwritten · preferences never override safety · conversation summaries never auto-become clinical facts.

## 34. TOKEN & COST GOVERNANCE
Context compression · retrieval limits · summarization · duplicate elimination · prompt/semantic caching · model-by-task · iteration/tool-call/response limits · background batching · local routing · cost dashboards · tenant/workflow budgets · abuse detection. **Never resend the whole chart or full conversation every turn.**

## 35-38. SKILLS, PLATFORMS, TERMINOLOGY, COMPLIANCE
AI/ML: LLMs · transformers · embeddings · fine-tuning/LoRA/QLoRA · quantization · RAG · reranking · knowledge graphs · NLP/NER/IE/classification · evaluation · serving · GPU optimization. Programming: Python/SQL/TypeScript/Bash required; Go/Rust/Java/Dart/C++ preferred. Frameworks: LangGraph · LangChain · LlamaIndex · DSPy · OpenAI Agents SDK · HF Transformers · PyTorch · vLLM · Ollama · Ray · MLflow · LangSmith · OpenTelemetry. Data: Postgres · Qdrant · Redis · Supabase · S3 · OpenSearch/ES · graph DBs · feature stores · warehouses · queues. Terminology: SNOMED · ICD-10 · LOINC · RxNorm · NDC · CPT · HCPCS · UCUM · FHIR/US Core · C-CDA · abbreviations · med nomenclature · reference ranges. Compliance: HIPAA/HITECH · minimum necessary · BAAs · HITRUST · SOC 2 · ISO 27001 · NIST AI RMF · model risk · threat modeling · injection defense · retention · vendor risk.

## 39-41. EXPERIENCE & CREDENTIALS
7+ yrs software/data/ML · 3+ yrs production LLM/NLP · production RAG + serving · eval systems · regulated/high-risk apps · multiple providers · tool/agent systems · sensitive data · distributed systems · clinician collaboration. Preferred: clinical NLP · interop · OpenEMR · FHIR · terminology · med safety · guidelines · ambient documentation · medical speech · healthcare AI eval · human factors · FDA-regulated · multi-tenant SaaS · self-hosted GPU. Credentials: grad CS/ML/biomedical informatics · AWS ML · Google PMLE · Databricks ML · NVIDIA · HL7/FHIR · HIPAA · CISSP/CCSP · ISO 27001 — **secondary to demonstrated production capability.**

## 42. PRACTICAL EXAM
Build a clinical RAG workflow that: accepts a synthetic patient summary · strips identifiers before external retrieval · hybrid-search + reranks an approved knowledge set · produces a structured summary separating facts from interpretations · ranked differential + must-not-miss · uncertainty · citations · refuses when evidence is insufficient · calls one approved tool · blocks one unauthorized call · detects a prompt injection · logs model/prompt/retrieval/tool versions · measures latency/tokens/cost · automated evals · rollback strategy · documents clinical limitations. **Evaluation: grounding · retrieval quality · security · architecture · structured reliability · hallucination control · citation accuracy · tool safety · eval quality · cost awareness · code · docs · limitation explanations.**

## 43. FIRST 90 DAYS
**1-30:** inventory AI workflows · model/prompt/knowledge registries · clinical output schema · audit requirements · eval harness v1 · PHI routing · token/cost monitoring · review existing agents.
**31-60:** hybrid retrieval + reranking · citation validation · approved sources · patient-context retrieval · injection defenses · structured validation · model routing · golden datasets · Qdrant + Postgres integration.
**61-90:** deploy Documentation/Evidence/MedRec agents · OpenEMR + NextGen tools · Chatwoot drafting · clinician evals · adversarial testing · shadow deployment · limited provider pilot · performance + safety report.

## 44. KPIs
Citation accuracy · grounded-claim rate · hallucination rate · structured validity · provider acceptance/correction · critical omission · unsafe recommendations · injection resistance · retrieval precision/recall · latency · cost/tokens per workflow · tool-call accuracy · agent-loop failure · model uptime · eval coverage · detection + rollback times. **Safety targets: cross-patient retrieval = 0 · cross-tenant = 0 · autonomous signature = 0 · autonomous Rx = 0 · fabricated citations = 0 · unlogged executions = 0 · unversioned prompts = 0 · unauthorized tool execution = 0.**

## 45-46. PROFILE + THE JD
Required: production LLM/RAG · advanced Python · vector/hybrid retrieval · routing/serving · agent/tool architecture · structured validation · evaluation · injection defense · sensitive-data security · observability + cost governance. Preferred: clinical NLP · FHIR/OpenEMR · terminology · healthcare AI safety · self-hosted GPU · medical speech · knowledge graphs · multi-tenant SaaS.
**The JD:** The Principal AI/ML, Clinical RAG, and Model Orchestration Engineer leads the Hermes intelligence platform — transforming LLMs into governed clinical-assistance systems, not uncontrolled conversational tools. Every output carries patient context, evidence provenance, uncertainty handling, tool restrictions, versioning, evaluation, and clinician oversight. **The objective: clinically useful without letting speed, automation, or capability compromise safety, privacy, provider authority, or documentation integrity.**

**Founder note (08-04):** the next team member = the **Senior Web Frontend & Provider Dashboard Architect** — the NURA clinician dashboard, admin portal, Paperclip operations interface, real-time work queues, and browser-based charting experience.
