# Daily MCP & Agent Engineering Intel

## 2026-08-04

### 1. MCP 2026-07-28: Stateless Core Lands (Joe Njenga, "Anthropic Just Overhauled MCP", ~21h ago)
- Biggest MCP revision since launch: initialize handshake & Mcp-Session-Id removed; every request self-describing via `_meta`
- Package split: `@modelcontextprotocol/sdk` → `@modelcontextprotocol/server` + `@modelcontextprotocol/client` (v2)
- Multi-round-trip requests replace held-open streams; tool lists now cacheable via `ttlMs` / `cacheScope`
- OAuth 2.1 hardened: RFC 9207 issuer validation required, RFC 9728 metadata mandatory; DCR deprecated
- Codemod (`npx @modelcontextprotocol/codemod@2.0.0-beta.2 v1-to-v2 .`) handles mechanical migration; Zod must bump to ^4.2.0

### 2. Vibe Code Common Sense Framework (Joe Njenga, ~3d ago)
- Eight-file project scaffold enforces rails-before-speed: BLUEPRINT → TIMELINE → PR → tracker update
- PRODUCT_TIMELINE.md as source of truth; checked-off PR items survive session gaps across Claude Code / Codex / Cursor
- Ships as Claude Code plugin (`/plugin install vc-sense@vibe-code-common-sense`), Codex skill, and manual agent prompt

### 3. Claude Sonnet 5 Released (~Aug 3)
- Anthropic's new default smart model; available in Claude Code; closest Sonnet to Opus-class reasoning to date

### NURA Impact
- MCP stateless core + deprecation of Sampling directly affects Hermes Agent's `mcp_tool.py` (SamplingHandler, the background event loop, and initialize handshake flow). 12-month clock started July 28 — migrate before mid-2027.
- The `@modelcontextprotocol/server` v2 SDK split means repin and test all NURA MCP servers against the stateless conformance suite.
- CVE-2026-59726 "RufRoot" (CVSS 10.0): audit any MCP bridge exposed beyond localhost — Ruflo's default docker-compose bound 233 tools to 0.0.0.0:3001 with zero auth.

## 2026-08-05

### 1. Claude Code Ponytail Plugin (Joe Njenga, ~1d ago)
- Plugin enforces YAGNI via 5-rung "Decision Ladder": need? stdlib? native? dep? one-liner? → only then write code
- Benchmarks: -54% LOC, -20% cost, -27% time, 100% safe (never cuts validation/security/error handling)
- Commands: /ponytail-review, /ponytail-audit, /ponytail-debt; works with Claude Code, Codex, Hermes Agent
- v4.8.4 added explicit Hermes Agent support — installable as a skill in NURA's own Hermes lanes

### 2. GLM 5.2 via Claude Code (Joe Njenga, ~1d ago)
- Z.ai's open-weights model routes through Claude Code via Ollama or Anthropic-compatible endpoint
- Critical: model ID must be `glm-5.2[1m]` (brackets included) for full 1M-token context; set API_TIMEOUT_MS=3000000
- Built a complete Claude Code plugin from scratch — zero errors, 4 min; ZCode harness now supports MCP + subagents
- Viable Opus alternative at lower cost for non-safety-critical agent workloads

### 3. Sonnet 5 — Deeper Benchmarks (Joe Njenga, ~20h ago)
- SWE-bench Pro 63.2% (91% of Opus 4.8); Terminal-Bench 2.1: 80.4% (+13.4pts over Sonnet 4.6)
- On knowledge work (GDPval-AA v2), Sonnet 5 edges past Opus (1618 vs 1615) — first midsize to beat flagship
- Intro pricing $2/$10 MTok through Aug 31; at xhigh effort matches Opus medium-high; default for Free/Pro

### NURA Impact
- Ponytail: install as Hermes skill to cut token spend on NURA's own agent lanes (codegen, refactors, PR reviews)
- GLM 5.2: candidate fallback backend for NURA agent pipelines if Anthropic API budget tightens; test against MCP tool-calling reliability before production
- Sonnet 5: migrate NURA's default agent model from Sonnet 4.6 — same cost tier, significant quality jump; keep Opus 4.8 reserved for safety-critical clinical/legal lanes

## 2026-08-06

### 1. Graphify — Knowledge Graph Skill for Claude Code (Joe Njenga, ~8h ago)
- Builds persistent knowledge graph from codebase via Tree-sitter AST + semantic extraction; 102K GitHub stars
- Three-pass pipeline: AST parse → audio transcription → semantic extraction (docs/PDFs/images); writes `graphify-out/` (graph.json, GRAPH_REPORT.md, graph.html)
- Token claim: up to 71.5× fewer tokens per query vs raw file scanning; incremental updates use SHA256 cache
- PreToolUse hook intercepts Glob/Grep calls, redirects Claude to consult graph before brute-force file search
- Install: `uv tool install graphifyy` (double-y), register via `graphify install`, run `/graphify` in Claude Code

### 2. DeepSeek V4-Flash on Claude Code — 71× Cheaper Than Fable 5 (Joe Njenga, ~4d ago)
- DeepSeek V4-Flash-07371 scores 82.7 on Terminal-Bench 2.1 vs Fable 5 at $0.14/$0.28 MTok vs $10/$50
- Run via `ollama launch claude --model deepseek-v4-flash` or direct API with `ANTHROPIC_BASE_URL=https://api.deepseek.com/v1`
- Real build: 891.7K input + 36.9K output tokens → ~$0.13 actual cost (Claude Code /cost showed $5.38 — ignores DeepSeek pricing)
- Comparable speed to GLM-5.2 and Kimi K3; cost is primary advantage; also runs on Hermes Agent via Ollama

### NURA Impact
- Graphify: evaluate for NURA-OS monorepo context management — could replace repeated file scans across Obsidian vault + codebase; test against Qdrant-backed retrieval for latency/cost
- DeepSeek V4-Flash: viable budget-tier router model for non-critical agent lanes (research, summarization, scaffolding); do NOT use for clinical PHI or legal reasoning without local-deploy assessment

## 2026-08-07

### 1. Claude Managed Agents — Anthropic Ships the Agent Runtime (Joe Njenga, ~5d ago; Anthropic blog Aug 4)
- Fully managed cloud agent harness: handles agent loop, sandboxing, tool execution, session continuity, context compaction
- Built-in tools: bash, file ops (read/write/edit/glob/grep), web search/fetch, MCP server connector; custom tools via user-defined schema
- Decouples "brain" (harness) from "hands" (sandbox) — sandbox is cattle, harness reboots from session log via `wake(sessionId)`
- $0.08/session-hour + standard token rates; self-hosted sandbox option for compliance/VPC; scheduled cron execution supported
- Credentials never touch harness: auth bundled at sandbox init (git tokens) or vault-proxied (MCP OAuth); p50 TTFT dropped ~60% vs coupled design

### 2. Anthropic Tokenizer Change Hiking Costs by 47% (Joe Njenga, ~3d ago)
- New tokenizer causes inconsistent token counts — same prompt, same model, up to 47% variance between runs
- Not a bug: deliberate update; hits Claude Code daily users and API consumers with long prompts hardest
- Mitigations: (a) audit token counts with `claude-code --verbose`, (b) trim redundant system prompts, (c) compact context before long agent sessions

### NURA Impact
- Managed Agents: evaluate for NURA's long-running agent workflows (cron-scheduled tasks, multi-hour research runs). Self-hosted sandbox option aligns with local-first charter. Caveat: no ZDR/HIPAA BAA eligibility yet — do NOT route PHI through Managed Agents sessions.
- Tokenizer cost: audit NURA's Claude API token consumption across lanes (Hermes, CORA, LEXA, clinical). If variance detected, apply prompt trimming before next billing cycle — 47% on a heavy agent lane is material.

## 2026-08-09

### 1. Anthropic Just Overhauled MCP — Stateless Core Goes Live (Joe Njenga, ~2d ago)
- 2026-07-28 spec: initialize/Mcp-Session-Id removed; every request self-describing via `_meta` (protocol version, client info, capabilities inline)
- MRTR replaces held-open streams for mid-call input; list responses now cacheable with `ttlMs` + `cacheScope`
- Auth hardened: RFC 9207 issuer validation mandatory, DCR deprecated → migrate to CIMD; credentials bound to issuer
- Serverless/edge deployment now feasible — no sticky sessions or shared Redis; Joe built & migrated a real server on the new TypeScript SDK
- Key migration notes: `server/discover` optional (not required), Zod ^4.2.0 needed, codemod handles mechanical changes

### 2. Warp Universal Agent Support — Parallel Multi-Agent Workflows (Joe Njenga, ~1d ago)
- Warp terminal now runs Claude Code, Codex, Gemini CLI side-by-side in isolated Git worktrees
- True parallel execution: one agent refactors, one writes tests, one handles docs — no queue, no merge conflicts
- Changes land in per-agent worktrees; integrated only when all finish

### NURA Impact
- MCP stateless core: all NURA MCP servers (OpenEMR, Mirth, Qdrant, Redis, Documo) must migrate to 2026-07-28 SDK within the 12-month deprecation window. Hermes Agent's `mcp_tool.py` SamplingHandler is directly affected — start with codemod `npx @modelcontextprotocol/codemod@2.0.0-beta.2 v1-to-v2 .`
- Warp parallel agents: evaluate for NURA multi-agent dev workflows (CORA docgen + LEXA review + Hermes orchestration on isolated worktrees concurrently)

## 2026-08-10

### 1. Graph Engineering Just Changed How AI Agents Work — Goodbye Loops (Joe Njenga, ~3d ago)
- Paradigm shift: prompt → context → loop → graph engineering. Loops hit context rot at 4-5+ serial steps; graphs isolate each step in a fresh context window.
- Graph = Nodes (one bounded unit of work) + Edges (typed dependencies) + State (typed, checkpointed memory outside any single context window).
- Diamond pattern: fan-out parallel research nodes → checker node (validates before forwarding) → synthesis node. Eliminates serial bottleneck and self-review bias.
- Static graphs (fixed structure, repeatable workflows) vs dynamic graphs (self-building at runtime based on outcomes). Most production tasks still better served by well-designed loops; graphs win when independent work queues behind each other.
- Tools: LangGraph (state graphs, `add_node`/`add_edge`/`add_conditional_edges`), AutoGen GraphFlow (directed graphs), Prefect directed agentic graphs (DAGs without the acyclic constraint).
- Key insight: loops still run inside every node. Graph engineering is the orchestration layer BETWEEN nodes — what runs, in what order, with what state, and what happens on failure.

### NURA Impact
- Graph engineering formalizes what NURA already does ad hoc: Hermes orchestrates CORA (docgen) + LEXA (review) + clinical lanes as isolated work units. The diamond pattern with a checker node maps directly to our maker-checker architecture — add explicit state schema + edge typing for audit trails and resumability.
- Evaluate LangGraph as a potential formal orchestration layer for NURA's multi-agent clinical/documentation pipelines; graph topology gives us checkpointed state, retry-per-node, and parallel fan-out that our current sequential agent chains lack.
