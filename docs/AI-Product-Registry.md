# NURA AI Product Registry (AI tool/lane inventory)

> Governance standard: every AI tool/product/lane is registered in the central
> inventory with lifecycle status (Design → Evaluation → Implementation → Monitoring),
> an owner, a permission scope, and a PHI classification. This is the operating
> register that the Architecture Review Board (ARB) and the risk-tiered approval
> process operate against. Follows `cto-execution-governance` §6 and
> `nura-operational-best-practices` §10. Last updated: 2026-09-02.

## I. Sovereign local model lane (Ollama @127.0.0.1:11434) — PHI-capable (local, $0)
| Model | Type | Dims | Status | Notes |
|---|---|---|---|---|
| `qwen2.5:3b` | general | — | Implemented | edge/fallback |
| `qwen3:4b` | general | — | Implemented | |
| `qwen2.5-coder:7b` | code | — | Implemented | |
| `qwen3:8b` | reasoning | — | Implemented | MoA reference model |
| `deepseek-r1:8b` | reasoning | — | Implemented | MoA reference model |
| `llama3.1:8b` | general | — | Implemented | mem0 LLM (local) |
| `biomistral:latest` | clinical | — | Implemented | |
| `med42:latest` | clinical | — | Implemented | lab-intake Med42 lane |
| `meditron:latest` | clinical | — | Implemented | |
| `minicpm-v:8b` | vision | — | Implemented | |
| `qwen3-vl:8b` | vision | — | Implemented | |
| `nomic-embed-text` | embedder | 768 | **Implemented** | mem0 embedder (local, sovereign) |

## II. Configured inference lanes (gateway model stack)
| Provider | Model | Scope | PHI? | Status |
|---|---|---|---|---|
| **deepseek** (primary/active) | `deepseek-v4-flash-vision-exp` | general | No | Implemented (active session default) |
| **openrouter** | `poolside/laguna-s-2.1:free`, `nvidia/nemotron-3-super-120b:free`, `google/gemma-4-31b-it:free` | free tiers | **No** (never PHI) | Implemented |
| **deepseek (OSS)** | `deepseek-ai/DeepSeek-V3.2`, `deepseek-reasoner` | reasoning | No | Implemented |
| **Qwen OSS** | `Qwen/Qwen3.5-72B-Instruct` | reasoning | No | Implemented |
| openai | `gpt-5-mini` etc | — | — | **Credits exhausted** (429) — use local/DeepSeek |

## III. Memory & knowledge lanes
| Lane | Store | Embedder | Status |
|---|---|---|---|
| Kernel | MEMORY.md/USER.md | — | Implemented |
| mem0 semantic | Qdrant server `mem0` | nomic-embed-text (768) | **Implemented 09-02** (server mode, no embedded lock, no credits) |
| RAG nura-docs | Qdrant `nura-docs` | fastembed bge-small (384) | Implemented (weekly reindex) |
| Episodic | session DB + daily-notes + lessons | — | Implemented |
| Vault | Obsidian (source of truth) | — | Implemented |

## IV. Agentic / orchestration lanes
| Lane | Engines | Status |
|---|---|---|
| Multi-agent delegation | `delegate_task` (spawn/list/steer/stop) | **Verified 09-02** — depth 1 (nesting off) |
| MoA (mixture of agents) | `moa.presets.default` (qwen3:8b + deepseek-r1:8b refs) | Configured |
| NATS/pub-sub | event backbone | Implemented (per architecture constitution) |

## V. Lifecycle gate — what each entry means
- **Design**: spec drafted; not built.
- **Evaluation**: benchmarked/red-teamed against a gate (clinical models need Clinical Governance Board approval + second-clinician isolation test).
- **Implementation**: wired + working.
- **Monitoring**: post-deploy drift/error/near-miss watch (continuous).
- PHI-class lanes **must** run local ($0) or a lane that does not train on prompts. Free openrouter tiers are dev/prototyping only.

## Registry governance
- **Owner:** Hermes (CTO) for infra/memory/general; Clinical Governance Board for clinical lanes.
- **Register before deploy** (design → entry added → status updated through lifecycle).
- **Audit:** reconcile registry vs live inventory (this file) monthly; any lane in production not in the registry = deviation (fix, don't ignore).
- **Approval:** risk-tiered. Clinical/operational AI = separate streams, never one envelope.
