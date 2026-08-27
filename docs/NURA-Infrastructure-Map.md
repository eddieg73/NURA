# NURA Infrastructure & Multi-Machine Fleet Map

**Company:** NURATECH.ai · **Funding:** founder-funded ~$600k to current state · **Class:** infrastructure documentation (server + Docker + agent + multi-machine). Source of truth (vault).

---

## 1. The Fleet (Hostinger VPS — 3 nodes)
| Node | Host | Spec | Role | Rule |
|---|---|---|---|---|
| **Clinic** | 1441409 · 72.61.71.211 | KVM8 · 8c/32GB | Patient data / EHR / PACS / gateway | 🔴 CRITICAL — never restart gateway/s6 children |
| **Lab** | 1030183 · 72.60.163.140 | KVM8 · 8c/32GB | Sovereign inference (Ollama/mesh LLM), Dify, Medplum, n8n-adjacent | 🟡 compute |
| **Edge** | 817449 · 195.35.32.113 | KVM1 · 1c/4GB | Perfex CRM fleet, n8n Edge | 🟢 edge |

**Deploy control plane:** **Dokploy** (PaaS) on the **Lab** at `dokploy.nuratech.ai` (→ 72.60.163.140) — the Docker-apps deploy UI. ⚠️ Probed **502** (app behind the proxy not serving yet — migration incomplete / container or proxy needs attention). Once up, it's the cleanest place to deploy **LiteLLM gateway · Open WebUI · OpenCode**.

## 2. Docker work (the containers)
- **Clinic (~43 containers Up):** hermes-gateway + hermes-dashboard (hands-off) · mirth-oie46 (MLLP 6663 / web 8086 / admin 8445) · OpenEMR · radris-stack (owns 80/443) · nura-ris · nura-coding (:8001) · mcp-medical · Orthanc · OHIF · Qdrant · Redis · Chatwoot · Mattermost · Postiz · Nginx PM · openclaw · agentmemory · meshcentral · obd-bridge · obsidian-livesync · home-assistant · tandoor · nura-radai.
- **Lab:** Dify stack · Medplum (FHIR) · Akaunting (accounting) · OHIF · rustfs · native Ollama (:11434) · Dockerized rescue + Colibrì (:8000).
- **Edge (817449):** multiple Perfex CRM installs (`/var/www/crm` = pay.nuratech.ai + erp.medisunmedical.com etc.) · FlexMCP · nginx proxy · Dokploy.

## 3. Agent / lane wiring (the "brain")
- **Hermes Agent** = ONE interchangeable runtime inside the NURA Agent OS (no vendor lock-in). Runs on the gateway (Clinic) + deployable across the fleet + **multi-machine**.
- **MCP lanes:** Perfex MCP (183 tools) · OpenEMR MCP · hostinger-* · medical · qdrant/redis · mirth · github · notion · obsidian · firecrawl · n8n.
- **Orchestration:** n8n (estate of 56+ workflows — Medisun voice/booking/memory, GHL sync, OpenEMR pack) + cron (Hermes) + Temporal-deferred.
- **LLM lanes (fallback chain):** DeepSeek (primary) → Lab-Ollama `deepseek-r1:8b` (reasoning) → `qwen3:8b` (tool) → `qwen2.5:3b` (simple) → Anthropic → Gemini. **Sovereign offline** (Colibrì/GLM-5.2) + Dockerized rescue lane.
- **Comms/voice:** ElevenLabs voice agent · Twilio SMS/voice · Chatwoot · Mattermost (org chat).

## 4. Multi-machine Hermes fleet (Windows PC + 2 iMacs, collaborative, Mattermost)
**Goal:** run Hermes on a **Windows PC** and **2 iMacs**, each an independent Hermes profile/node, all **logging into Mattermost** to communicate/collaborate (the org chat = the shared command/coordination surface).
- **Architecture:** one Hermes install per machine (`hermes` CLI/desktop), each its **own profile** (isolated config/skills/memory), each wired to the shared **Mattermost** as its messaging gateway (bot token → Mattermost channel). The machines coordinate by posting/reading in a shared Mattermost team (e.g., #ops / #dev), and the **gateway** on the Clinic is the master node; the 3 satellite nodes (Win + 2× iMac) are profile-isolated workers that join the shared Mattermost channels.
- **Windows PC:** Windows-specific Hermes (per hermes-agent windows-quirks skill) — install via the installer, configure Mattermost gateway, join the shared team.
- **iMacs:** macOS Hermes (native desktop app) — same pattern.
- **Collaboration model:** shared **skills + memory via the vault** (the Obsidian vault is the source of truth, synced via obsidian-livesync/CouchDB); **Mattermost** = the human/agent comms bus; each node's agent posts status/reports to the shared channels; Hermes orchestrates with `delegate_task` / shared cron.
- **Security:** each machine = its own profile + Mattermost bot creds sealed (never in chat); PHI stays on the BAA host (Clinic); the Windows/Mac nodes are dev/ops-workers (no production PHI).

## 5. "Copy Grok Bot + Cursor" (in progress)
We are building OUR OWN equivalents (no lock-in): a **Grok-like assistant bot** (self-hosted sovereign LLM + chat UI + **Mattermost bot**) and a **Cursor-like AI coding agent** (agent + local LLM + editor integration). Research compiling → then deploy.

## 6. Documented doctrine (this session)
- LLM resilience: multi-provider fallback chain + sovereign rescue lane (verified).
- Harness best practices (`harness-best-practices` skill): verify-before-declare, sandbox side-effects, tiered patterns, failure→rule loop.
- Reg A (v3.1): proprietary integrated process, white-labeled suite, only Eddie + Alex.
- Patient-appointment-followup (Medisun first client) + Medisun Health Group enterprise OS.

---
**Sources / where the live state lives:** fleet via Hostinger MCP · docker via `mcp__hostinger_vps__` · lane docs in `/opt/data/profiles/nura/skills/` (nura-fleet-command, n8n-lane-ops, perfex-mcp, hermes-agent, local-llm-and-vision-ops, sovereign-inference-fleet).
