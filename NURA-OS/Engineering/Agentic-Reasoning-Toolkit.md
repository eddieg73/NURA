# NURA Agentic-Reasoning Toolkit (surveyed 2026-08-16, all pushed Jul-Aug 2026)

GitHub's current best agentic-reasoning + research tools, mapped to the NURA stack.

## The pairing (Hermes ↔ NotebookLM class)
- **LRriver/NotebookLM-Lite** — open-source NotebookLM alternative: self-hosted RAG, document Q&A, citations, notes, mind maps, flashcards, study guides, infographics, AI podcast/audio overviews. THE self-hosted NotebookLM replacement → pairs with Hermes like the NotebookLM MCP does, but sovereign. (updated 08-15)

## Deep-research / agentic reasoning
| Repo | What it gives us |
|---|---|
| **DavidZWZ/Awesome-Deep-Research** | ACL 2026 KnowFM curated map of the ENTIRE agentic deep-research field — the index of everything |
| **EverMind-AI/Raven** | Memory-first, self-improving agent harness, MiroThinker deep research (pushed 08-16 — hottest) |
| **iblameandrew/open-deepthink** | Multi-agent research lab — data distillation + long evolutionary collaborative reasoning (08-15) |
| **openJiuwen-ai/deepsearch** | Knowledge-enhanced deep search, chunk-level citations, traceable reasoning |
| **Haohao-end/openagent** | "Deep Research + Dify as one" — deep reasoning loops, visual workflows, RAG, A2A delegation |
| **Cerno-AI/Cerno-Agentic-Local-Deep-Research** | Local-first research platform, cloud↔self-hosted model switching, step-traceable |
| **heurist-network/heurist-agent-framework** | Reasoning + tool use + memory + deep research + MCP + agents-as-a-service |

## How it fits NURA
- NotebookLM-Lite → the sovereign RAG Q&A (DocsGPT's sibling; citations + study guides for clinical education)
- Raven/open-deepthink → the self-improvement + multi-agent research lanes (the reflexion phase)
- Awesome-Deep-Research → the field map to keep re-mining monthly
- n8n corpus → /opt/data/n8n-knowledge/n8n-llms-full.txt (683KB complete docs, 08-16)

## n8n knowledge state (2026-08-16)
- FULL official docs corpus on disk: /opt/data/n8n-knowledge/n8n-llms-full.txt (grep-able: AI Agent 8×, OAuth2 30×, LangChain 4×)
- Live instance: Edge code-n8n-1, 53 workflows catalogued, 20 active
- Skills: n8n-lane-ops · n8n-container-ops · n8n-workflow-authoring · n8n-cli-ops
