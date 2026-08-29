# NURA Agent-OS — Build Plan (2026-08-29)

Owner: Eddie (founder) · Architect: Hermes (CTO) · Admin: Hermes (CAO)
Status: PLAN — grounded in verified source (CoreCoder 1,081-LoC Python; microsoft/agent-framework 13k★)

## First principles (the 10-year forward thesis)
Models commoditize (Grok, Llama, DeepSeek, NVIDIA Nemotron — all open-weight). The DURABLE moat is not a model —
it is the **orchestration fabric + memory + interop (MCP) + integrated process**. We OWN that; we PLUG the model.
This is SpaceX-style integrated systems engineering: one Agent-OS, one interchangeable runtime, no vendor lock.
(The 512K-line Claude Code is Anthropic's leaked TypeScript IP — we do NOT copy it; we build the clean Python
re-implementation and study the architecture only.)

## The harness core — fork CoreCoder (MIT, 1,081 LoC Python)
`he-yufeng/CoreCoder` is the ideal ownable base. Its architecture (verified):
- **Agent loop** (`agent.py`): `user → LLM(with tools) → tool calls? → execute → loop`, stops on plain text. Simple, correct.
- **LLM layer** (`llm.py`, 361 LoC): OpenAI-compatible. **"Switch provider by changing OPENAI_BASE_URL + OPENAI_API_KEY. That's it."** Plus a LiteLLM backend for 100+ providers. → **no-vendor-lock is built in.**
- **Tool interface** (`tools/base.py`): `Tool` ABC (`execute(**kwargs)`, OpenAI function schema). Each tool = a callable capability → maps to **MCP**.
- Modular: `agent.py` · `llm.py` · `session.py` · `context.py` · `prompt.py` · `tools/{bash,edit,agent,todo}.py`.

## The NURA integration (what we ADD to the fork)
1. **Pluggable sovereign model lanes** (the LLM layer swap) — route to: dock Ollama `:11435` (qwen2.5:3b, free), DeepSeek (live brain), Grok (open, when key), NVIDIA Nemotron. No Anthropic lock. Adapt `llm.py` OPENAI_BASE_URL to our router.
2. **MCP interop** (the NemoClaw "agent-runs-agent" insight) — expose every NURA tool as an MCP server so Hermes + sub-agents + external agents all interoperate on ONE protocol. The Tool ABC becomes an MCP-tool bridge.
3. **Memory** — wire the four-node clock (WRITER/DECAY/RENEWER/GRAVE) + the Obsidian vault + Qdrant as the agent's durable memory. CoreCoder's `ContextManager` + session → persist to Qdrant/vault.
4. **Multi-agent orchestration** — `microsoft/agent-framework` (13k★) as the orchestration layer for multi-agent work (the fabric). CoreCoder = the single-agent harness; agent-framework = the multi-agent orchestration/mesh on top.
5. **The clinical edge** — NVIDIA `BioNeMo` + NeMo toolkit for healthcare agents (optional, when clinical work needs domain agents).

## Build order
- **P0 scaffold (this repo):** fork CoreCoder → NURA Agent-OS harness (`agentos/`) — the agent loop + LLM layer pointed at our sovereign router + MCP tool bridge. Prove a single agent call through our lanes.
- **P1 memory:** wire the clock + vault + Qdrant as durable memory.
- **P2 orchestration:** integrate microsoft/agent-framework for multi-agent meshes.
- **P3 domain:** BioNeMo/clinical agents on top.

## The IP doctrine (non-negotiable)
- Fork CoreCoder (MIT) = clean. We own our integrated process. Never copy the leaked Anthropic TS.
- Public releases use NURA names; OSS we build on stays internal-only (import doctrine). No vendor-name disclosure in Reg A/public.

## Evidence (verified this session)
- CoreCoder: MIT, 1,081 LoC, clean modular agent/tool/LLM layers (read agent.py, llm.py, tools/base.py).
- microsoft/agent-framework 13,192★ Python · swarms 7,104★ · MetaGPT 70k★ · autogen 60k★.
- NVIDIA NemoClaw 22,303★ (agent interop) · NeMo-Agent-Toolkit 2,605★ · BioNeMo 435★.
- xai-org/grok-1 52,198★ (open) · clawcodex 883★ (full Python Claude-Code rebuild).

## B2 storage
`nura-documents/agent-os/` (orchestration | agent-harness | model-lanes | interop-mcp | architecture) — created + manifest uploaded.

## Status / next
Plan laid + grounded. NEXT (P0): scaffold the `agentos/` harness — fork CoreCoder's loop, LLM layer against our sovereign router, MCP tool bridge — and verify a real agent call end-to-end.
