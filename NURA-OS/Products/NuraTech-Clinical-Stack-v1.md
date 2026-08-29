# NURATECH CLINICAL STACK v1 — THE CANONICAL COMBINATION (2026-08-05, founder)

**The strongest NuraTech stack: DocsGPT (interface + RAG shell) · cTAKES/CogStack (clinical structuring) · BioMCP (evidence retrieval) · LiteLLM (model routing) · Qdrant (retrieval) · Presidio (PHI controls) · Langfuse (auditability) · HAPI FHIR + CDS Hooks (OpenEMR integration).**

## The component roles
| Component | Role | Status |
|---|---|---|
| **DocsGPT** | the interface + the RAG shell (the agent layer + the chat) | deploying on the Clinic (/docker/docsgpt) |
| **cTAKES / CogStack** | the clinical structuring (entities, negation, temporality, concepts — the note normalization) | cloned — the UMLS-dictionary note! |
| **BioMCP** | the evidence retrieval (the live biomedical MCP tools) | cloned — the MCP-wiring pending |
| **LiteLLM** | the model routing (ONE OpenAI-compatible gateway — the 100+ providers, budgets, fallbacks) | cloned — the gateway-build pending |
| **Qdrant** | the retrieval (the vector store — the collections: guidelines/patient-memory/literature/protocols/payer-rules/device-manuals) | LIVE on the Clinic ✓ |
| **Presidio** | the PHI controls (the PII redaction + the anonymization at the ingest boundary) | cloned — the analyzer-build pending |
| **Langfuse** | the auditability (the tracing, prompt-versioning, evaluation, the user-feedback) | LIVE on the Lab ✓ |
| **HAPI FHIR** | the OpenEMR integration rail (the FHIR R4 server) | cloned — the docker pending |
| **CDS Hooks** | the OpenEMR workflow triggers (prescribing/chart-open/order-entry → NURA!) | cloned — the hooks-implementation pending |

## The wiring order (the A-to-Z build queue)
1. **LiteLLM** — the model gateway FIRST (the single entry for every model lane — the routing + the budgets + the fallbacks — the DocsGPT + the agents all speak one OpenAI-compatible API)
2. **Presidio** — the PHI boundary (every ingest: redact/flag before the store — the analyzer + the anonymizer + the custom NURA-entities)
3. **Qdrant collections** — the schema: clinical-guidelines · patient-memory · medical-literature · practice-protocols · payer-rules · device-manuals
4. **DocsGPT** — the shell wired to LiteLLM + Qdrant (the RAG-lane live)
5. **cTAKES/CogStack** — the clinical structuring (the note-normalization pipeline → the concepts → the index)
6. **BioMCP** — the evidence tools (the MCP-lane to Hermes + the DocsGPT)
7. **Langfuse** — the tracing on every lane (the auditability — the MIT-core ✓)
8. **HAPI FHIR** — the server + the client registration (the OpenEMR's FHIR rail)
9. **CDS Hooks** — the workflow triggers (the OpenEMR hooks → the NURA recommendations → the provider review)
10. **The e2e**: synthetic patient → the encounter → the note → cTAKES-structure → the DocsGPT summary → BioMCP-evidence → the Qdrant-retrieval → the LiteLLM-routed answer → the Langfuse-trace → the Presidio-clean → the OpenEMR via HAPI/CDS → the provider review

## The governance (the clinical constitution, unchanged)
- The pipeline output = the draft (the labels) · the provider review before the EMR · the citations = version+date+source · the PHI = Presidio-cleaned + never in the dev lanes · OpenEMR = the source of truth (API-only) · Langfuse = the audit-trail for every clinical output.
