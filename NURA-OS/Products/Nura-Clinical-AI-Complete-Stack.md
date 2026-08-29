# NURA CLINICAL-AI — THE COMPLETE STACK GRAB (2026-08-05, founder canonical)

**The 10-section stack: clinical-text extraction · EHR-native CDS · FHIR testing · imaging intelligence · model gateway · vector retrieval · observability/evaluation · agent safety · synthetic patients · terminology assets.**

## The components
1. **Clinical text extraction**: apache/ctakes (diagnoses/meds/symptoms/procedures/anatomy/negation/history/temporality/concepts + FHIR components — Java/MEDBASE-fit — DEFAULT dictionary = UMLS-license!) · CogStack/cogstack-nlp (the MedCAT home — the archived original → the newer project — entity-linking + SNOMED/UMLS normalization + contextual status + patient timelines — review the model-pack + terminology licenses!).
2. **EHR-native CDS**: HL7/cds-hooks (the vendor-neutral triggers — prescribing/chart-open/order-entry!) · HL7/fhirpath.js (the FHIR-resource querying) · smart-on-fhir/Swift-SMART (the iOS SMART-client foundation) · microsoft/smart-on-fhir-app-starter-kit.
3. **FHIR testing/certification**: inferno-framework/inferno-reference-server (the simulated US Core/SMART server!) · fhir-validator-app + the Inferno test kits (the conformance before Epic/Oracle/athenahealth!).
4. **Imaging intelligence**: the MONAI family — Project-MONAI/MONAI · MONAILabel · monai-deploy-app-sdk · model-zoo (training/annotation/deployment/DICOM/inference/bundles!) · pydicom/deid (de-identification — "best effort" — validate against burned-in pixel PHI + private tags!).
5. **Model gateway**: BerriAI/litellm (the ONE OpenAI-compatible gateway — 100+ providers, routing, virtual keys, load-balancing, budgets, guardrails, fallbacks — review the mixed OS/commercial licensing!).
6. **Vector retrieval**: qdrant/qdrant ✓ (Apache-2.0 — ALREADY LIVE on the Clinic!) — the collections: clinical-guidelines · patient-memory · medical-literature · practice-protocols · payer-rules · device-manuals.
7. **Observability/evaluation**: langfuse ✓ (ALREADY on the Lab — MIT-core!) · Arize-ai/phoenix (OTel traces + retrieval-eval + experiments!) · vibrantlabsai/ragas (RAG-eval + synthetic test-sets!) — the CUSTOM clinical metrics: unsupported medical assertions · citation correctness · medication-dose consistency · allergy contradictions · missing emergency escalation · note completeness · ICD/RxNorm mapping accuracy · patient-vs-provider attribution.
8. **Agent safety/access**: guardrails-ai/guardrails (structured output + validators!) · open-policy-agent/opa (declarative policy — e.g. no psychotherapy-notes for the scheduling agent, no prescriptions for the scribe!).
9. **Synthetic patients**: synthetichealth/synthea ✓ (ALREADY CLONED — longitudinal synthetic patients → FHIR/Bulk-FHIR/C-CDA/CSV — Apache-2.0 — the PHI-free test bed!).
10. **Terminology**: RxNorm Current Prescribable Content (download WITHOUT the full UMLS license — the NLM-normalized names + RXCUIs = public-domain federal!) · the full RxNorm = the free UMLS license (the proprietary-incorporated-terms!) · SNOMED-CT US Edition = via UMLS (US-use free, the registration/reporting/redistribution conditions apply!).

## The status map
- Already live: qdrant (the Clinic) · langfuse (the Lab) · synthea + DocsGPT + MedRAG + biomcp + medspacy + medplum + hapi + whisper + pyannote (the nura-clinical-ai workspace!)
- To clone (the batch): ctakes · cogstack-nlp · cds-hooks · fhirpath.js · Swift-SMART · smart-on-fhir-app-starter-kit · inferno-reference-server · fhir-validator-app · MONAI (x4) · deid · litellm · phoenix · ragas · guardrails · opa
