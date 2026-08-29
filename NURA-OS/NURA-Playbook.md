# The NURA Playbook — the complete operating manual

The CTO-grade playbook: the how the Hermes + the NURA + the OMI + the DeepSeek harness work together. The standing document, the updated 08-20.

## The stack — the one picture

| Layer | The tool | The role |
|---|---|---|
| The brain | Hermes (the me) | The orchestrator: the memory, the routing, the crons, the Telegram, the delegation, the audit |
| The identity | NURA | The command persona: the Jarvis backbone, the EMH clinical voice, the plain-speech law |
| The capture | OMI | The wearable: the ambient audio, the screen, the conversations → the memory |
| The sovereign coder | dsh (the DeepSeek harness) | The coding lane: the local Ollama, the $0, the builds and the fixes |
| The reviewer | ClawCode (the Rust Claude) | The free review lane, the compiled, the point-at-Ollama queued |
| The paid reserve | Claude Code | The safety-critical review only, the spend tracked |
| The study shelf | Grok (the open source) | The idea-mining only, the no runtime (the founder's verdict) |
| The CEO | Atlas (the Paperclip) | The org execution, the delegation, the governance |
| The workers | The dev team + the 38 specialty brains | The Paperclip agents, the routed by the work type |

## The OMI integration — the capture loop

1. The wearable captures (the pendant's the ambient audio, the Glass's the vision on the ESP32-S3).
2. The app surfaces (the Scribe tab = the live transcription, the Memory section = the searchable 2nd brain).
3. The MCP exposes (the search_memories, the get_conversations, the get_action_items, the get_knowledge_graph).
4. The Hermes consumes (the MCP registration → the memory tools in the toolbox).
5. The vault stores (the Obsidian = the memory authority).
6. The Notion mirrors (the daily record complete).

The sovereign swaps: the whisper for the Deepgram, the local Ollama for the API keys, the Qdrant for the Pinecone, the vault graph for the Neo4j.

## The dsh integration — the coding loop

1. The work arrives (the founder's ask or the cron).
2. The route: the sovereign coding → the dsh via the dsh_run MCP tool or the /dsh endpoint (the proven live).
3. The harness runs against the local Ollama (the deepseek-r1:8b).
4. The Hermes reviews the output before the anything touches the production.

## The memory architecture

- The vault = the authority. The specs, the peer cards, the doctrines, the status.
- The mem0 = the semantic layer (the repair on the queue).
- The session DB = the conversation history (the session_search).
- The Notion = the mirror (the dashboards, the tasks, the legal).
- The AUTO-DREAM = the nightly consolidation (the workday replay).
- The daily reflection + the weekly Moltbook mining + the daily skill hunt = the learning loops.

## The clinical laws (the non-negotiable)

- The provider-gated: the every clinical output carries the DRAFT — PROVIDER APPROVAL REQUIRED. The AI drafts, the clinician signs.
- The consent: the explicit before the recording, the OMI's the LED's the not the consent.
- The BAA: the vendor register before the any PHI touches the any external lane.
- The eMedical: the single-session, the FHIR-API-only, the audit scripts logout.
- The OpenEMR: the API only, the never the DB writes.

## The routines (the standing)

- The 06:00 EST — the Daily Executive Intelligence Brief (the EIB: the BLUF, the four pillars, the action matrix).
- The 08:00 + the 18:00 — the executive weather brief (the three sites, the pilot data).
- The alerts — the on the change only, the anti-flood law.
- The nightly — the AUTO-DREAM + the build-queue triage + the obsidian-nightly.
- The weekly — the Moltbook mining, the space audit, the drift audit.
- The monthly — the evolution review, the license watch.

## The laws (the founder's standing)

- The NO-MONEY: the local-first, the free tiers, the OpenRouter off.
- The Mars-grade: the off-grid, the self-healing, the auditable, the sovereign.
- The pre-build-triage: the no builds without the duplicate/sense gates.
- The verify-before-declare: the receipts, the not the prose.
- The anti-flood: the critical-only chat, the status → the dashboard.
