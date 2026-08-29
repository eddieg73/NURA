# NURA CLINICAL AI — THE AMBIENT PIPELINE ARCHITECTURE (2026-08-05, founder canonical)

**The end-to-end clinical-AI flow: provider question / ambient encounter → ASR + diarization → clinical NLP → agent layer → live retrieval → evidence validation → EMR → FHIR.**

## The pipeline (the founder's flow)
```
Provider question or ambient encounter
        ↓
Whisper + pyannote          (the speech-to-text + the speaker diarization)
        ↓
medspaCy                   (the clinical-NLP normalization — entities, sections, concepts)
        ↓
DocsGPT                   (the interface + the agent layer — the RAG + the chat)
        ↓
BioMCP                    (the live literature retrieval — the biomedical MCP)
MedRAG                    (the medical retrieval + the reranking)
        ↓
Citation + evidence validation layer   (the source/version/date checks — the data-catalog doctrine)
        ↓
MEDBASE / OpenEMR         (the clinical source of truth — API-only)
        ↓
HAPI FHIR or Medplum      (the FHIR R4 layer — the interoperability rail)
```

## The component map (the repos + the roles)
| Repo | Role | Status |
|---|---|---|
| DocsGPT | the RAG interface + the agent layer | deploying on the Clinic (the build running) |
| whisper | the ambient ASR (the encounter audio → text) | cloned — the pip + the model pending |
| pyannote-audio | the speaker diarization (who said what) | cloned — the HF-token + the model pending |
| medspacy | the clinical-NLP normalization (the entities/sections) | cloned — the pip + the en_core_sci models pending |
| biomcp | the biomedical MCP server (the live literature) | cloned — the MCP wiring to Hermes pending |
| MedRAG | the medical retrieval + the reranking (the evidence-ranked) | cloned — the index + the eval pending |
| synthea | the synthetic test patients (the PHI-free e2e testing!) | cloned — the Java + the data-gen pending |
| medplum | the FHIR R4 server + the app platform | cloned — the docker deploy pending |
| hapi-fhir-jpaserver-starter | the alternative FHIR R4 JPA server | cloned — the docker deploy pending |
| MEDBASE / OpenEMR | the existing clinical source of truth | LIVE on the Clinic ✓ |

## The build order (the A-to-Z queue)
1. DocsGPT (in-flight) → the knowledge ingestion
2. Synthea → the synthetic-patient corpus (the e2e-testing bedrock — PHI-free!)
3. HAPI-FHIR or Medplum → the FHIR rail (the docker + the client-registration)
4. medspaCy → the clinical NLP lane (the models + the normalization)
5. Whisper + pyannote → the ambient scribe (the ASR + the diarization — the founder's voice!)
6. BioMCP + MedRAG → the evidence lanes (the MCP-wiring + the reranking index)
7. The citation/validation layer → the data-catalog doctrine applied (the source/version/date!)
8. The e2e test: synthea-patient → the ambient audio → the transcript → the normalized note → the DocsGPT summary → the evidence-checked → the OpenEMR draft → the FHIR export → the clinician review

## The governance (unchanged — the clinical constitution)
- The pipeline output = the DRAFT (the labels: Confirmed/Reported/Observed/Inferred/Requires-verification)
- The provider review BEFORE any note enters the EMR
- The citations = the version + the date + the source (the retrieval-timestamp!)
- Synthea only for the testing — never real PHI in the dev lanes
- OpenEMR = the source of truth — API-only, never DB writes
