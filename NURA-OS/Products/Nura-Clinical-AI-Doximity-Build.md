# NURA CLINICAL-AI — THE DOXIMITY-CLASS KNOWLEDGE & PHYSICIAN-NETWORK BUILD (2026-08-05, founder canonical)

**The core trio (the founder's valuation): DocsGPT's application shell + BioMCP's biomedical tool interface + MedRAG's medical retrieval methodology — the foundation. The build: import the MedRAG textbook + StatPearls corpora into the prompts, indexes, clinical content, branding, and the physician-network data — the NURA-class Doximity.**

## The knowledge import (the corpora)
1. **MedRAG corpora** (the gzxiong/MedRAG): the medical retrieval corpora — the StatPearls (the clinical reference articles!) · the PMC-OpenAccess subset · the textbook corpora · the PubMed abstracts — the download via the repo's corpus scripts / the HuggingFace datasets.
2. **StatPearls**: the clinical reference articles (the peer-reviewed, the NCBI — the retrieval-ready!) — the flagship clinical content for the index.
3. **The import pipeline**: corpora → the DocsGPT ingestion (the document parsing + the embeddings + the vector index — all-mpnet-base-v2 local!) → the retrieval-lane (the MedRAG methodology: the query-rewrite + the reranking + the evidence-grounded answers!) → the BioMCP live-tools for the freshest literature.

## The Doximity-class build (the physician network + the brand)
- **The prompts**: the clinical-QA + the consult-style interactions (the DocsGPT's agent shell with the MedRAG-grounded retrieval + the citations).
- **The indexes**: the vector stores (the corpora + the vault's products + the protocols when they land).
- **The clinical content**: StatPearls + the textbook + the FDA/formulary lanes + the NURA protocols.
- **The branding**: the NURA physician-facing brand (the network = the physician-app surface).
- **The physician-network data**: the NPPES/NPI registry (the provider-directory lane — the public registry — the NPI 1154381580 = the founder's own entry ✓) + the practice-data (the CMS Provider Data Catalog!) — the network = the physician-directory + the content + the consult-lanes.

## The build order
1. The MedRAG corpus download (StatPearls + the textbook + the PMC-subset) — the scripts in the MedRAG repo
2. The DocsGPT ingestion (the corpus → the index — the local embeddings)
3. The MedRAG retrieval methodology wired (the rerank + the evidence checks)
4. The BioMCP tools live (the MCP-lane to Hermes + the DocsGPT)
5. The physician-network layer (the NPI-directory + the profiles + the content-bundles)
6. The brand surface (the Doximity-class UI on the DocsGPT shell)
