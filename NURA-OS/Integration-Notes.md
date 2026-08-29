# NURA Integration Notes (2026-08-02) — full connection state

Every connection, its status, and its purpose. Credentials NEVER live here (secrets stay .env 0600).

## Communication & Channels
- **Telegram** ✅ live (this chat) · **Email** ✅ (nura@nuratech.ai Workspace) · **Signal** ✅ · **SMS/WhatsApp** 🔶 Twilio creds dead (401 — console refresh needed; numbers staged: +1 727-477-3636 / WhatsApp +1 305-206-8697) · **Webhook** ✅ · **API server** ✅ :8642 (execution lane for Paperclip agents)

## AI & Inference (doctrine: fast/accurate/free-first)
- **DeepSeek** ✅ primary (cheap+accurate) · **Gemini** ✅ direct + vision cascade (flash→pro) · **OpenRouter** ✅ free lanes quality-gated · **OpenAI** 🔶 key on box (0 credits history) · **Anthropic** 🔶 pending · **HF Inference** ✅ Bio_ClinicalBERT $0 (proven) · Embeddings local fastembed 384d · RunPod ✗ invalid

## MCP Lanes (35+)
- **LIVE**: openFDA (18) · PubMed · BioPortal (7) · legal case-law (10) · Moltbook (8) · Redis 8.8.1+vectorset · Qdrant (RAG 540 chunks) · CDC (Socrata public) · Perfex (183, token pending) · OpenEMR (20, mock — OAuth pending)
- **BUILT, KEY PENDING**: OpenEvidence (2) · Granola (4) · Mirth (HL7, creds pending) · Firebase FCM (4) · Documo fax (4) · Chatwoot · GHL
- **Vision**: vision-proxy.py cascade free-vl→gemini (vision_analyze tool route broken — direct proxy is the lane)

## Orchestration & Org
- **Paperclip** ✅ :3101 canonical — 57+ agents (Atlas CEO · Orion CTO · Iris CMO · 27 named + SaaS division + NURA Capital Markets pending) · execution path LIVE (all patched with gateway key) · board NUR-1..90
- **Hermes gateway** ✅ gateway-nura (s6) — gateway-default = harmless zombie (never kill s6 children)
- **Crons** ~42: audits · watchdogs · digests · X check-in 08:00 · Disclosure & Space 17:00 · competitive watch Fri · scrum Mon 09:00 · CME/license · self-model Sun 06:00

## Browser & Content
- **Playwright** ✅ chromium headless (PubMed/ClinicalTrials/CDC/FDA verified; desktop-UA required) — free medical browsing lane
- **Studio stack** (video-studio-stack): ElevenLabs ✅ (voice_id fix NUR-73) · HeyGen/Higgsfield/CapCut 🔶 keys pending · FLUX3 ✅ B-roll · bundle.social ✅
- **X** 🔶 xurl installed, auth pending (daily check-in armed) · **Moltbook** ✅ claimed + posting

## Data & Storage
- **Obsidian vault** ✅ everything mirrors here (RAG source) · **Notion** 🔶 token LIVE, 0 pages shared — one-click share gates sync · **Mem0** ✅ · **RAG** ✅ 540 chunks · **R2 backup** 🔶 staged
- **Fleet**: Clinic 1441409 (PHI/EHR/PACS) · Lab 1030183 (compute) · Storefront 817449 (pay/CRM) · Docker access ruling NUR-68 pending (Hermes box = client-only)

## Trading (NURA Capital Markets — NUR-85)
- SAF scanner ✅ (Yahoo live) · data registry ✅ (market-data.json) · congressional tracker 🔶 (Senate live; House 500; Quiver key pending) · broker API 🔶 pending · $1,000 account protocol (1% cap)

## Claude Code (NUR-87)
- CLI ✅ 2.1.220 · DeepSeek lane ✅ VERIFIED · Gemini lane 🔶 slug-gating · Docker container pending NUR-68
