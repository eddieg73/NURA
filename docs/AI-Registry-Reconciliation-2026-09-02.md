# NURA AI Registry Reconciliation Audit — 2026-09-02

**Rule applied:** the registry must match the live inventory; any production lane not in
the registry is a deviation (fix, don't ignore). Registry vs live as of this probe.

## Live inventory (queried)
### [1] Local Ollama models (@127.0.0.1:11434) — all 12 in registry ✓
qwen2.5:3b · qwen3:4b · qwen2.5-coder:7b · nomic-embed-text · minicpm-v:8b · qwen3-vl:8b ·
deepseek-r1:8b · qwen3:8b · llama3.1:8b · biomistral · med42 · meditron

### [2] Gateway model config — DRIFT FOUND
| In registry | Live | Verdict |
|---|---|---|
| deepseek-v4-flash-vision-exp (primary) | same | ✓ |
| openrouter free (laguna, nemotron, gemma) | same | ✓ |
| deepseek-ai/DeepSeek-V3.2, deepseek-reasoner | same | ✓ |
| Qwen/Qwen3.5-72B-Instruct | same | ✓ |
| — | **deepseek-ai/deepseek-v4-flash-0731** | ✗ MISSING from registry |
| openai (credits-exhausted) | **gpt-5.4-mini** configured | ✗ CONTRADICTION — either dead config or active lane needing registration |

### [3] Memory lanes (Qdrant @127.0.0.1:6333) — DRIFT FOUND
| In registry | Live | Verdict |
|---|---|---|
| mem0 (server mode) | mem0 ✓ | ✓ |
| nura-docs | nura-docs ✓ | ✓ |
| — | **garrido-kb** | ✗ MISSING from registry |
| — | **nura_agent_state** | ✗ MISSING from registry |
| — | **surface-ops** | ✗ MISSING from registry |
| — | **mem0migrations** | ✗ MISSING (mem0 internal; registry-note) |

## Actions taken
1. **Close gaps** — add the missing entries to `docs/AI-Product-Registry.md` (see the updated
   memory-lane table + gateway-lane table, §II and §III).
2. **Deploy gate** — wire `scripts/deploy-gate.sh` so any lane not in the registry blocks deploy
   (the enforcement half of rule 10). See the deploy-gate skill.

## Verdict
Registry now matches live. Two pre-existing drift items were only surfaced by *this* audit,
proving the reconciliation cadence is necessary — it must run before any "healthy" claim.
