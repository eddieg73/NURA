# The NURA Harness & Model Routing Doctrine

The standing role assignment + the model routing table. Established 2026-08-19 (the founder's directive).

## The org roles

| Role | Who | The lane |
|---|---|---|
| The brain | Hermes | The orchestrator: the memory, the crons, the routing, the audit, the Telegram. Dispatches everything, codes nothing heavy itself. |
| The CEO | Atlas (the Paperclip) | The org's execution layer: the delegation, the role cards, the research-gated governance (the cto-execution-governance), the team management. Reports to the founder through the Hermes. |
| The dev team | The 9+6 agents (the Mobile Dev, the Backend, the UIUX, the QA, the DevOps CI, the iOS Release, the Security, the PM, the Growth + the original 6) | The workers. Each gets the models routed by the work type. |
| The sovereign coder | dsh (the DeepSeek Harness) | The default coding lane: the local Ollama, $0, the no external calls. The daily build workhorse. |
| The Rust speed lane | Grok Harness (the grok-build) | STUDY ONLY — the source sits in the docs library for the idea-mining (the plan mode, the skillify). No compile, no runtime. The founder's verdict 08-19: "we don't need the grok build." |
| The premium reviewer | Claude Code (the real, the paid) | The safety-critical + the clinical code review only. The paid lane, the spend tracked, the sparing. |
| The free Rust reviewer | ClawCode (the open-source Rust rewrite) | The MIT, the 42 tools, the multi-provider. COMPILED 08-19 (the CLAW_API_BASE env patch applied). The point-at-Ollama config = the named queue item. |

## The model routing (by the work being done)

| Work type | Model | Where |
|---|---|---|
| The quick ops, the light tasks, the fast checks | qwen2.5:3b | local Ollama |
| The general reasoning, the chat, the drafting | qwen3:8b | local Ollama |
| The long-context agent jobs (the 64k+ crons) | llama3.1:8b | local Ollama |
| The clinical work (the notes, the coding, the triage) | med42 · biomistral | local Ollama (the Lab) |
| The vision (the screenshots, the imaging) | qwen3-vl:8b · minicpm-v | local Ollama |
| The sovereign coding (the no-external builds) | deepseek-r1:8b (the via the dsh) | local Ollama |
| The premium review (the clinical/security gates) | Claude (the sealed key) | Anthropic — the paid, the sparing |
| The free API boost (the heavy one-offs) | NVIDIA NIM llama-3.1-8b · the OpenRouter free (the laguna, the nemotron-3-super-120b, the gemma-4-31b) · the HF Qwen3.5-72B | free tiers only |
| The on-device routing (the LOM lane) | Needle 2 (the 14MB tool-caller) | the phone/glasses/edge |

## The routing rules
1. The local-first always. The free API tiers only when the local's the not enough. The paid (the Claude) only for the safety-critical review.
2. The Hermes routes every task; the agents never self-select beyond the lane.
3. The audit trail: the every model call's the logged with the actor + the work type (the sovereign audit schema).
4. The clinical outputs always carry the DRAFT/provider-gated label, the regardless of the model.
