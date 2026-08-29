# NURA Coding Harness — the Architecture Distillation (2026-08-16)

Three line-by-line audits (48,988 LOC read: Clawd-Code 17,765 · from-scratch 6,508 · learn-harness 22,715 + the Tinkeringg port). The verdicts + the patterns we adopt.

## The verdicts
- **Clawd-Code**: educational — a real REPL + a dead porting scaffold (mirrors a missing TS archive, ~30 placeholder packages). OpenAI-compatible path works with Ollama. NOT production.
- **from-scratch**: the architecture goldmine — TS+Python mirror images (byte-parity tested), the full Claude-Code mechanism: loop, tools, subagents, the /goal evaluator, the permission gate, the cache-aware compaction.
- **learn-harness**: the teaching track — 17 chapters, 213+88 tests green. Thesis: "Agency comes from the model; the harness is the vehicle."

## The 8 patterns to adopt (with sources)
1. **The loop as contract** — `while True`: LLM → tool_use? → execute → append results → repeat; permission = one `continue`, hooks = one call, compaction slots BEFORE the LLM call (learn-harness s01:87-117, s03:211-214; from-scratch agent.ts)
2. **The prompt-based Stop-hook evaluator** — a small separate model judges the goal condition each turn; the transcript is sent as data between user messages (injection-proof), three-state verdict, parse fail → not-met (from-scratch autonomy.ts:37-99)
3. **The two-stage permission gate, fail-closed** — deny-list → read-only fast path → reasoning-blind projection → cheap gate model → adjudicator that weighs user intent → denial counters → human fallback (autonomy.ts:302-464)
4. **Fork-return subagents with inherited permission mode** — isolated context, stdout capture, token fold-back, permission-laundering prevention (agent.ts:1574-1605; subagent.ts)
5. **Static/dynamic prompt split for prefix caching** — one cache_control on the immutable core, one on the last message, applied to a copy; CLAUDE.md as user-message context, never system (prompt.ts:188-244)
6. **Zero-cost context compression** — utilization-gated budget → dedupe/snip with hot-cache grace → idle-gated micro-compaction (agent.ts:1110-1335; learn-harness s08:419-426)
7. **File-backed durable state** — atomic tmp+os.replace, flock, open("x") ID allocation, rollback on failed persistence (learn-harness s13:70-89, s12:355-438)
8. **Typed mailbox protocols** — JSONL message bus + request-id state machines; approvals version-stamped; summaries re-injected as untrusted "Reference state" vs "Authoritative request" (s13:783-1019, s08:63-67)

## The NURA build map (what we own vs what we build)
- Loop: Hermes' own agent loop = already the contract ✓ → add the permission-continue discipline
- Evaluator: the goal-gate = a local qwen2.5 call (we have the model lane) — NEW, build
- Permission gate: the deny-list + fail-closed = the safety doctrine, codify — NEW, build
- Subagents: delegate_task = the fork-return (isolated context, verified returns) ✓ → add the permission-inheritance rule
- Prompt caching: n/a for the Ollama lane (no cache API) — the compaction patterns instead
- Durable state: the black-box JSONL + the file-write discipline ✓ → adopt the atomic-replace pattern
- Mailbox: the mesh-router + the board = the bus ✓ → add the version-stamped approvals

## The decision
Build the NURA harness as a THIN layer: the loop + the evaluator + the gate, running on the Lab Ollama (qwen2.5:3b for the loop, the tiny gate = the same model), MCP lanes as the tools, the black-box as the memory. No new framework dependency — the patterns are the framework.
