# NURATECH DEFENSIBILITY STACK — THE CLINICAL LOGIC/TERMINOLOGY/ANALYTICS LAYER (2026-08-05, founder canonical)

**The next valuable snatch: not another chatbot shell — the clinical logic, evidence, permissions, terminology, and analytics infrastructure that creates defensibility.**

## The 8 layers
1. **Computable clinical rules — CQL** (cqframework/clinical_quality_language + clinical-reasoning + vscode-cql): the standardized machine-executable CDS + quality-measure logic (the CQL compiler, CQL-to-ELM translator, runtime, examples — Apache-2.0!). Uses: contraindication/allergy checks · weight-loss-med eligibility · lab-monitoring rules · postoperative follow-up · HCC + quality-measure alerts · prior-auth criteria · evidence-based order sets. **The LLM interprets the encounter; CQL adjudicates the deterministic rules — the anti-hallucination spine.**
2. **A real terminology server — Snowstorm** (IHTSDO/snowstorm): SNOMED International's open-source server (Elasticsearch + FHIR-terminology API + the SNOMED API — Apache-2.0, the content = its own license!). The coding-normalization layer: "heart attack" → MI → SNOMED concept → ICD-10-CM → FHIR Condition — controlled vocabulary instead of approximate codes.
3. **Scientific evidence synthesis — PaperQA2** (Future-House/paper-qa): the Apache-2.0 scientific RAG with in-text citations — metadata-aware retrieval, LLM reranking, contextual summaries, iterative agent searching, local models, Crossref/Semantic-Scholar metadata. The NURA Evidence Agent: supporting/conflicting studies · retraction checks · quality-graded literature · evidence tables · guideline-vs-primary separation · page-level citations · inadequacy identification — "a serious physician research assistant."
4. **Scientific PDF intelligence — GROBID** (grobidOrg/grobid): PDFs → structured TEI/XML (titles/authors/affiliations/abstracts/sections/figures/citations/DOI/PMID — Docker + REST + Java — Apache-2.0). The pipeline: Journal PDF → GROBID parsing → reference/metadata resolution → PaperQA2 extraction → NURA synthesis — beats dumping raw PDF text into a vector DB.
5. **Longitudinal clinical analytics — the OHDSI stack** (CommonDataModel · WhiteRabbit · Atlas · Achilles · DataQualityDashboard · PatientLevelPrediction): the OMOP Common Data Model — cohort identification · outcomes research · medication-effectiveness · complication surveillance · patient-level risk prediction · practice benchmarking · trial feasibility · de-identified multi-practice analytics. **FHIR = the transactional model; OMOP = the analytic/research model.**
6. **Identity + agent-level permissions** (keycloak/keycloak + openfga/openfga): Keycloak = auth/federation/2FA/administration (Apache-2.0) · OpenFGA = relationship/attribute-based authorization (HTTP+gRPC+SDKs — agent/RAG authorization = the documented use case!). The matrix: Scribe (read encounter ✓ draft SOAP ✓ sign ✗ prescribe ✗) · Coding (read finalized ✓ recommend ICD-10 ✓ psychotherapy ✗ change-docs ✗) · Prescription (prepare order ✓ allergy-check ✓ controlled-substance-transmit ✗ without the authorized signer).
7. **Tamper-evident audit — immudb** (codenotary/immudb): the append-only cryptographically-verifiable ledger (KV/document/SQL — Apache-2.0). Store: transcript hash · retrieved-evidence hash · model+version · prompt-version · recommendation hash · human edits · signed-note hash · medication/order actions · consent events · override reasons — hashes + references, NOT redundant PHI.
8. **Clinical-model evaluation — MedHELM** (Pacific-AI-Corp/medhelm + the HELM study): the standardized evals for CDS, note-gen, patient-communication, research, administrative tasks (PubMedQA, med-questions, hallucination-eval, transcript-summarization, patient-education — dataset licenses individually reviewed!). HealthBench = studied-not-incorporated (CC BY-NC!). The proprietary NuraTech suite: hallucinated contraindications · incorrect dosing · missing allergies · missed urgent escalation · unsupported citations · fabricated labs · speaker confusion · procedure laterality · over/undercoding · improper controlled-substance recommendations.

## The resulting architecture (canonical)
```
NURA/Veronica interface
 → ambient transcription + speaker separation
 → clinical NLP + terminology normalization
 → Snowstorm terminology server
 → PaperQA2 + GROBID evidence engine
 → CQL deterministic clinical rules
 → LLM clinical synthesis
 → FHIR transactional record
 → OMOP longitudinal analytics
 → Keycloak + OpenFGA authorization
 → immutable audit evidence
 → MedHELM-based regression testing
```

## The immediate commercial value (the founder's ranking)
**CQL · Snowstorm · PaperQA2 · GROBID · OpenFGA · the OHDSI stack = the components that transform the product from an AI wrapper into a governed clinical intelligence platform.**
