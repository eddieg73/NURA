# Agent Platforms Intel Feed

Daily sweep of agent platforms, MCP ecosystem, and user-facing agent tools. Compiled by the NURA agent-platforms intel cron.

---

## 🤖 Agent Platforms Daily — Sat Aug 15, 2026

**🔥 Top 3 adopt-this-week**

1. **Hermes v0.20.1 (v2026.8.13)** · Our own platform's "Herald" era: streaming voice with barge-in + wake words, A2A v1.0, signed outbound webhooks, grounded-citations skill, desktop plugin SDK · Upgrade NURA's agent core for voice and verifiable research citations · github.com/NousResearch/hermes-agent/releases
2. **easydocforms MCP** · Patient-intake MCP server: blank PDF → fill link → completed PDF; PHI never enters agent context · Usable today for NURA intake workflows without HIPAA exposure in agent transcripts · mcp.so (new arrival, ~2 days old)
3. **Medplum MCP** · Healthcare FHIR dev platform's MCP server, trending #1 on mcp.so this week ⚠️ (capabilities unverified — evaluate against our OpenEMR stack before adopting) · mcp.so

**🆕 New MCP servers/plugins**

- GitHub MCP Server v1.9.0 (Aug 10): semantic `search_issues`, new `find_duplicate` tool
- Zotero MCP — 13,086 dl/mo, week's biggest adoption arrival (research/library access)
- whats-running-mcp — live machine ground truth (processes/ports/daemons) for agent fleets; fits the CTO infra-monitoring mandate
- pmb — local-first persistent memory for coding agents over MCP (SQLite, Apache-2.0, 286★)
- claude-real-video — any LLM watches and searches local video
- skills.sh **Skill Packs** (Aug 4) + ClawHub native plugin/package catalog — one-command bundled installs

**📦 Platform releases**

- Hermes v0.20.0 "Herald" (Aug 3) → v0.20.1 patch rollup (Aug 13)
- Claude Code Week 32: cross-session messaging; self-hosted runners (Team/Ent beta); auto mode becomes default Aug 14
- openai-agents-python v0.21.0 (today): provider-neutral testing APIs; v0.20.0 default model = gpt-5.6-luna
- Google ADK v2.7.0 (Aug 13): model-declared capabilities, tools can return media, Jinja2 instruction templates
- OpenClaw 2026.8.1-beta.2 (today); 2026.7.1 stable = Control UI overhaul + GPT-5.6 support
- LangGraph 1.2.11 (Aug 11): per-node `trace_policy`

**💎 Misc user-facing finds**

- HF **Agentic Resource Discovery (ARD)** spec + Discover tool: natural-language search across MCP servers/skills; live MCP endpoint at huggingface-hf-discover.hf.space/mcp
- MCP security: independent scan (state-of-mcp-security) found 87% of scanned servers expose medium+ hardening issues — audit third-party MCPs before install
- Volume check: 1,074 new MCP servers published week of Aug 3–9 (down 8% WoW)

**⏭️ Watchlist**

- ARD spec adoption (Linux Foundation; Google/MS/GoDaddy/HF contributors)
- OpenEnv (Meta+HF agentic-RL environment standard; MCP first-class; "Harbor" unification of coding-agent training paths)
- MCP Python SDK v2 migration wave (openai-agents v0.20+ supports v1+v2; httpx2 transport changes)

---

## 🤖 Agent Platforms Daily — Sun Aug 16, 2026

**🔥 Top 3 adopt-this-week**

1. **ZeroGPU MCP Server** · Offload summarize/classify/entity-extract/PII-redact to small edge models via MCP, with per-call savings breakdown · NURA's Documo intake pipeline could pre-scrub PHI and pre-process docs cheaply before they hit agent context · huggingface.co/blog/its-maddy-a/zerogpu-mcp
2. **Browse.sh** · 100+ curated site-specific browser playbooks + `browse` CLI; installable into Hermes via the browse-sh Skills Hub source · Durable payor-portal/gov-site workflows instead of per-run rediscovery · browse.sh ⚠️ launch date unverified
3. **Microsoft 365 MCP Server** · Graph API surface for agents (mail/calendar/SharePoint); 133k dl/mo, now #2 API-integration server · Inbox/calendar automation usable by a solo founder today · mcphq.ai

**🆕 New MCP servers/plugins**

- MongoDB Atlas Managed MCP (Aug 13) — fully hosted; OAuth 2.1 user-delegation + audit parity; 30k npm installs/wk
- Azure DevOps Remote MCP — GA (Aug 6); Entra auth; Copilot Studio support
- Argent — drive iOS sims/Android emulators/TVs from coding agents; 210k dl/mo (week's top arrival)
- TerraVision — terraform-plan → AWS/Azure/GCP architecture diagrams (4.8k dl/mo)
- Syncro MCP (Aug 11) — RMM/PSA; writes obey existing permissions + approval rules
- Haystack MCP (Aug 6) — first intranet-space MCP server (enterprise signal)
- Volume: 1,203 new servers this week — 3rd-busiest on record; registry now 22,122

**📦 Platform releases**

- OpenAI: ChatGPT Workspace Agents GA (Aug 7) — templates, custom MCP servers, Slack, scheduled runs; ChatGPT Work product live (Aug 4)
- OpenAI: ChatGPT Voice now accepts file uploads + Projects (Aug 7); GPT-5.6 Fast mode handles >272K-token prompts (Aug 5)
- Anthropic: Claude Code v2.1.228–233 (Aug 11–14) — synced skills can no longer run `!` commands or expand `@` files locally; plugin-marketplace `command` sources; enterprise skill/plugin security scanning beta (Aug 6)
- Meta: Muse Glimmer (Aug 10) — local, agentic, multimodal, open; day-0 Intel vLLM support
- HF: Strands Agents + LeRobot + Storage Buckets (Aug 13) — record/train/deploy in one place; Baseten joins HF Inference Providers (Aug 6)
- Hermes: Skills Hub unified index now ingests browse.sh + ClawHub package catalog — install path for the items above

**💎 Misc user-facing finds**

- OpenThinkerAgent-32B (open-thoughts) — open-data 32B agent model; MedAgentBench included in its 7-benchmark suite
- HF security read: "Anatomy of a Frontier Lab Agent Intrusion" (Jul 27) — useful forensics protocol for the infra mandate
- ZeroGPU + MongoDB + Azure DevOps = the week's pattern: vendors shipping hosted MCP over OAuth instead of DIY connectors

**⏭️ Watchlist**

- Liquid AI edge push — LFM2.5-2.6B (explicit Hermes/OpenClaw harness support) + LFM2.5-VL-3B (Aug 12)
- MCP registry velocity — 22k+ servers; finance #1 arrival category 7 weeks straight (noise/quality signal)
- Agent Skills security posture — Anthropic scanning beta + Claude Code skill sandboxing set the bar other harnesses will copy

---

## 🤖 Agent Platforms Daily — Mon Aug 17, 2026

**🔥 Top 3 adopt-this-week**

1. **Muse Glimmer** (Meta, 30B, Apache-2.0) · local agentic multimodal model; day-0 llama.cpp/vLLM/transformers support + quantized GGUFs; HF blog ships AGENTS.md recipes for Claw/Hermes wiring · PHI-safe on-prem agent backbone for document analysis and coding — no API keys · huggingface.co/blog/muse-glimmer
2. **Anthropic-Cybersecurity-Skills** · 817 structured security skills mapped to MITRE ATT&CK, NIST CSF/AI RMF, D3DEFEND; runs in Claude Code, Copilot, Codex, Cursor, Gemini CLI + 20 platforms; trending on GitHub today (156★/day) · operationalizes the CTO security mandate as loadable agent playbooks · github.com/mukul975/Anthropic-Cybersecurity-Skills
3. **Ouroboros** (MCP coding agent) · pins an acceptance spec — verify command and expected output never enter the success contract; 5,480★, 58k dl/mo · spec-gated automated testing, fits the CI/CD mandate · mcphq.ai/news/2026-08-10-new-mcp-servers

**🆕 New MCP servers/plugins**

- Week of Aug 10–16: **1,315 new MCP servers** — 2nd-busiest week on record; registry total 22,234; finance top category 7 straight weeks
- agent-device — inspect/control/debug real iOS/Android/desktop/TV apps; #3 browser-automation server, 559k dl/mo
- Kin — semantic code retrieval over entity/relationship/provenance graph; 10+ releases/90d
- Upstash mcp-server — manage Upstash databases/resources from agents (4.5k dl/mo)
- Docmancer — local-only, source-attributed Markdown memory + docs retrieval
- REA — reverse-engineer anything via one CLI + MCP server (3.8k dl/mo)

**📦 Platform releases**

- Hermes Agent v0.20.2 (Aug 16) — desktop multi-gateway Connections registry, MCP health checks, cron hardening, LiteLLM prompt caching
- OpenAI — ChatGPT desktop imports setup/skills/plugins from Claude Code, Cowork, Cursor (Aug 11); Plugin Directory replaces App Directory; Atlas browser agent retired Aug 9
- Claude Code v2.1.233 (Aug 14) — bundled-skill alias fixes; claude.ai-synced skills can no longer run `!` commands or expand `@` files locally
- OpenClaw 2026.8.1-beta.2 (Aug 15) — fail-closed secret egress host binding, SQLite snapshot backups, plugin-install provenance `--force` warnings
- Codex CLI 0.147.0 — portable Agent Plugins, search across local/workspace/remote plugin catalogs

**💎 Misc user-facing finds**

- **strix** — open-source AI penetration testing; #2 on GitHub trending today (856★/day) — self-scan NURA web apps pre-production
- MCP spec went **stateless** (2026-07-28): sessions/initialize removed, official conformance tests added; GitHub MCP Server already compliant — verify our client SDKs follow
- cc-switch ⚠️ — desktop switcher across Claude Code/Codex/OpenCode/OpenClaw/Gemini CLI/Hermes (adoption numbers from GitTrend, unverified)

**⏭️ Watchlist**

- MCP stateless-core migration across Hermes + our own servers (conformance tests as the gate)
- OpenEnv → Harbor: TRL "loop-owning" harness training (Aug 5 post) — train coding agents on their real loops; MCP first-class
- Muse Glimmer local integrations (Ollama/LM Studio/Unsloth) landing this week — test as Hermes local model

---

## 🤖 Agent Platforms Daily — Thu Aug 27, 2026

**🔥 Top 3 adopt-this-week**

1. **fhirHydrant** (FHIR MCP server) · R4+ FHIR over SMART Backend Services; config-driven resource tools + LOINC/SNOMED terminology + IPS/patient-match operations; compact PHI-light audit responses · Direct fit for NURA's FHIR/SMART clinical plane — turns FHIR resources into MCP tools for Hermes · mcp.so/servers/fhirhydrant (verify against OpenEMR stack first)
2. **Hermes Agent v0.20.6 (v2026.8.27)** · Today's release: remote MCP catalog (50+ vendor-hosted servers), OS-keychain secret encryption (fits SEAL→PROBE→REGISTER cred-SOP), TTL result caching for web_search/extract · We run Hermes — upgrade touches our own agent core · github.com/NousResearch/hermes-agent/releases
3. **claude-obsidian** · Self-organizing Obsidian second-brain (15 Agent Skills, ingest→linked pages, vault lint, Karpathy LLM-wiki pattern, plain Markdown you own) · Matches NURA's Obsidian-vault-as-memory-authority doctrine · v1.9.2, trending on GitHub today · github.com/AgriciDaniel/claude-obsidian

**🆕 New MCP servers/plugins**

- HF **tiny-agents / `huggingface_hub` MCP client** — `Agent` class, ~70-line MCP agent, AGENTS.md support (JS `@huggingface/tiny-agents`) — unlocks cheap provider-routed agent lanes
- **Katto · Speccy x402 · Hologrow · Legion · QuanticData** (mcp.so new arrivals, names/function ⚠️ unverified)
- **anthropics/claude-plugins-official** + **ComposioHQ/awesome-claude-skills** (GitHub today) — official plugin + skills indexes
- **K-Dense-AI/scientific-agent-skills** (GitHub today) — domain agent skills, screen for clinical-relevant ones
- Hermes plugin-index provenance ⚠️: default `index.json` URL 404'd; fixed by pointing at in-tree seed — audit community plugins before install

**📦 Platform releases**

- **Hermes v0.20.6** (today) — catalog/self-heal/secrets
- **Claude Code v2.1.246** (Aug 25) — SendFeedback tool, plugin-skill fixes; Agent Skills + Skills API now **GA**, new `ant` CLI
- **OpenAI** — ChatGPT Work (long-task agent) + scheduled-task webhooks; Workspace agents GA (Biz/Ent/Edu); Codex MCP command deprecated → Codex plugin
- **Google ADK v2.8.0** (Aug 25) — non-blocking skill loading, MCP toolset reuse, Jinja2
- **OpenClaw 2026.8.1-beta.3** — GPT-5.6 Sol/Terra/Luna/Ultra, SQLite backup/restore, CDP relay
- **LangGraph 1.2.11** — v3 content-block streaming, per-node timeouts/error handlers

**💎 Misc user-facing finds**

- **Agent Memory Leaderboard** (HF, results expected Aug) — eval for our mem0/Obsidian memory
- MCP registry surge: **2,402 new servers** week Aug 17 (record), **25,072 cumulative**
- ChatGPT Work + webhook scheduled tasks — recurring report automation for solo founder

**⏭️ Watchlist**

- 4,988 MCP servers publish **no source repo** (unauditable) — keep clinical/FHIR MCPs to config-driven vetted repos
- Hermes plugin-index supply-chain (default URL was 404; in-tree seed now canonical)
- Claude Code **Workflows** research preview + OpenAI Workspace agents — watch for NURA multi-step clinical workflows

---

## 🤖 Agent Platforms Daily — Fri Aug 28, 2026

**🔥 Top 3 adopt-this-week**

1. **Consistorium** (local-first repo-intelligence MCP) · live git state, docs, durable tasks & agent handoffs exposed to ChatGPT/Claude/Codex/Hermes, every claim labeled `live_observation` vs `agent_record` · Gives Hermes/Atlas a grounded "strategist" layer over the NURA monorepo without pasting context — directly reinforces verify-before-declare · github.com/Renaissance-AI-Solutions/consistorium
2. **AgentSeed** (hybrid skill + MCP guardrail) · gates every coding task as contract→implement→verify→evidence; 5 zero-dep tools: `verify_code`, `scan_hallucination`, `check_plugin`, `sandbox_run`, `schema_validate` · Enforces the founder rule "never declare complete untested" as a loadable CI gate for Claude Code/Cursor/VS Code · github.com/weed33834/AgentSeed
3. **HF Spaces `agents.md`** · every Gradio Space now exposes a plain-text `agents.md`; agent reads schema/auth and calls it end-to-end (chained prompt→image→3D, zero integration code) · Turns HF's open-weights catalog into callable primitives for NURA's on-prem/open-weight lanes · huggingface.co/blog/mishig/spaces-agents-md

**🆕 New MCP servers/plugins**

- Consistorium (repo-intel MCP, Aug 23) — the top pick above
- AgentSeed (anti-hallucination skill+MCP, 1.0.0, Aug 19)
- oss-trends-mcp — task-driven trending-OSS recommender (GitHub momentum + npm/PyPI + HN buzz)
- MegaAgent-MCP — one async server: web search, article extract, GitHub, Docker sandbox, OCR, Reddit/4PDA
- mcp-server-github-trend — GitHub trending discovery + repo health scoring
- Codex portable Agent Plugins — search across local/workspace/remote plugin catalogs (0.150)

**📦 Platform releases**

- **Hermes** — "Herald" (A2A v1.0, streaming voice, grounded-citations skill, desktop plugin SDK) + "Quicksilver" (~80% faster first token); v0.20.6 (Aug 27) adds remote MCP catalog + OS-keychain secret encryption
- **Claude** — Agent Skills + `/v1/skills` GA (no beta header); Claude Platform on AWS; `ant` CLI
- **Claude Code v2.1.248** — `--restricted` flag strips command/code tools + WebFetch; per-agent cacheTtl; Workflow tool footprint 5.7k→~1k tokens
- **Google ADK v2.8.0** — BigQuery SQL-injection guards ⚠️ (we hold clinical data), Model Armor plugin, data-agent tools, per-workflow token telemetry
- **OpenClaw 2026.8.1-beta.3** — atomic `/model` switching for GPT-5.6 Sol/Terra/Luna/Ultra; plugin-install provenance warnings
- **LangChain (Aug)** — Managed Deep Agents + LLM Gateway public beta; Deep Agents v0.7 (~65% fewer base tokens)

**💎 Misc user-facing finds**

- ClawHub `clawhub` CLI + skills.sh + browse.sh — one-command search/install/publish of agent skills & plugins (vector search, semver)
- MCP registries matured: Glama 79k servers, mcp-marketplace 21.5k security-scanned tools
- Workato MCP Registry GA — governed server inventory + runtime registry access for agents

**⏭️ Watchlist**

- **Stateless MCP (2026-07-28)** migration — Hermes already compliant; Codex opt-in; gate our own servers on conformance tests
- Anthropic enterprise skill/plugin security scanning + Claude Code sandboxing — the bar other harnesses copy; re-audit our clinical skills
- ADK BigQuery SQL-injection guards — signal to harden MCP/tool data-layer against SQL injection in OpenEMR/Postgres connectors

---

## 🤖 Agent Platforms Daily — Sat Aug 29, 2026

**🔥 Top 3 adopt-this-week**

1. **MCP-Agent-1.7B** · First open small SLM fine-tuned to natively speak MCP (Qwen3-1.7B LoRA): calls MCP tools over JSON-RPC, plans DAG tool chains, asks clarifying Qs, refuses dangerous requests · Direct fit for NURA's LOM lane (local tool-caller brain) · huggingface.co/muhammadtlha944/MCP-Agent-1.7B
2. **Hermes Agent v0.20.6 (Aug 27)** · consent-gated real-profile browsing; remote MCP catalog +50 live-verified servers (Cloudflare, Grafana Cloud, Better Stack, Railway); TTL result-caching for web_search/web_extract; opt-in OS-keychain secret encryption; lean-tail compression default; new models (GLM-5.3-Flash, MiniMax M3 free, MiniMax H3 Max video) · Upgrades our own core · github.com/NousResearch/hermes-agent/releases/tag/v2026.8.27
3. **ARD (Agentic Resource Discovery) + HF Discover tool** · Open discovery layer (Linux Foundation; Google/MS/GoDaddy/HF) — agents search federated skill/MCP/A2A catalogs by intent; HF shipped `hf discover` + REST/MCP endpoint · Publish NURA's ai-catalog.json to be discovered · huggingface.co/blog/agentic-resource-discovery-launch

**🆕 New MCP servers/plugins**

- oss-trends-mcp · ranks trending OSS by GitHub momentum + npm/PyPI + HN buzz · fuels this exact sweep
- github-repo-mcp-server · own-repo issues/PRs/CI + trend discovery (allowlist-gated, read-only)
- lastmile-ai/mcp-agent (8.5k★) · composable MCP agent framework, FastMCP API, Temporal durability
- mcp-server-github-trend · GitHub trend search + repo health score + sandboxed deploy

**📦 Platform releases**

- Claude Code v2.1.251 (Aug 28): PreModelSwitch/PostModelSwitch hooks; CLAUDE_CODE_SUBAGENT_MODEL now default-only
- openai-agents-python v0.22.0: guardrail output redaction, ModelBehaviorError, provider-contract tightening
- Google ADK v2.8.0 (Aug 25): native A2A task mode, Model Armor guardrail plugin, BigQuery SQL-injection guards, token telemetry
- ChatGPT Workspace Agents (Aug 24): org shared-context agents, schedules, Slack deploy
- LangGraph 1.2.x: content-block streaming v3 + delta channels; per-node trace_policy
- OpenClaw 2026.8.1-beta.2: plugin install provenance `--force` gate; ClawHub semver ranges; muse-spark-1.1 provider

**💎 Misc user-facing finds**

- HF **State of Open Models Summer 2026**: agents are "the new user" — Claude Code 44.4% of agent traffic in July, Codex climbing 10.4→20.8%; MCP moving into Linux Foundation Agentic AI Foundation ⚠️
- Agent Memory Leaderboard Space (featured) — unified agent-memory eval

**⏭️ Watchlist**

- Small MCP-native models (MCP-Agent-1.7B, AgentMercury-Qwen3.5-4B-SAO) as LOM tool-callers
- Publish NURA ai-catalog.json; track ARD federation modes
- Claude Code subagent-model precedence change — reconcile our fleet's CLAUDE_CODE_SUBAGENT_MODEL
