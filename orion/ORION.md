# Project ORION: The Clinical Operating System

## Philosophy: "Everything is a Plug-in"
ORION is not a monolithic app; it is an orchestration layer. 
- **The Brain:** Hermes (Gemma 4) handles global intent and high-level security.
- **The Engine:** DeepSeek Harness (dsh) manages the atomic execution of sub-agents.
- **The Interface:** Flutter renders Generative UI (GenUI) sent by dsh.
- **The Plugins:** Every feature (EHR, Scribe, RAG, VoIP) is an isolated MCP/REST plug-in.

## Architecture Map
Frontend (Flutter) $\leftrightarrow$ Middleware (dsh Harness) $\leftrightarrow$ Local Brain (Gemma 4)
                                    $\downarrow$
                           [ Plug-in: EHR ] [ Plug-in: Scribe ] [ Plug-in: RAG ] [ Plug-in: Audit ]
