# ⚕ NURA OS — System Architecture

> **Updated:** 2026-08-01 | **Owner:** Hermes Agent

## Core Stack

```
┌─────────────────────────────────────────────────────┐
│                  NURA OS Dashboard                    │
│              (:9119 — nura-clinical skin)             │
├─────────────────────────────────────────────────────┤
│  Hermes Agent (deepseek-v4-pro)                       │
│  ├─ Exec Persona: NURA/Hermes                         │
│  ├─ Gateway: Telegram + API + Webhook                  │
│  └─ MCP Fleet: 19 connectors                          │
├─────────────────────────────────────────────────────┤
│  Data Layer                                           │
│  ├─ PostgreSQL (BeHive) :5434                         │
│  ├─ Redis :6379                                       │
│  ├─ Qdrant :6333/:6334                                │
│  └─ Obsidian Vault: /opt/data/Obsidian Vault          │
├─────────────────────────────────────────────────────┤
│  Execution & Integration                              │
│  ├─ n8n (n8n.nuratech.ai)                             │
│  ├─ Paperclip (:3100)                                 │
│  ├─ OpenEMR MCP (mock → live)                         │
│  └─ Cron Scheduler (12 jobs)                          │
├─────────────────────────────────────────────────────┤
│  External                                             │
│  ├─ Telegram Gateway                                  │
│  ├─ n8n Webhooks                                      │
│  ├─ Hermes Webhooks (:8644)                           │
│  └─ Zapier Bridge                                     │
└─────────────────────────────────────────────────────┘
```

## Active Ports

| Port | Service | Status |
|------|---------|--------|
| 3100 | Paperclip | 🟢 |
| 5434 | PostgreSQL | 🟢 |
| 6333 | Qdrant HTTP | 🟢 |
| 6334 | Qdrant gRPC | 🟢 |
| 6379 | Redis | 🟢 |
| 8642 | Hermes API | 🟢 |
| 8644 | Hermes Webhook Gateway | 🔴 Stopped |
| 9119 | Hermes Dashboard | 🟢 |

## Model Routing

- **Primary:** deepseek-v4-pro (deepseek provider)
- **MoE Reference:** 9 models across 7 providers
- **Fallback:** openrouter (configured, disabled)
- **OSS Aliases:** oss-free-fast, oss-free-reasoning, oss-free-large

## Key Paths

| Path | Purpose |
|------|---------|
| `/opt/data/profiles/nura/` | Active Hermes profile |
| `/opt/data/profiles/nura/config.yaml` | Hermes configuration |
| `/opt/data/profiles/nura/skills/` | Skill library |
| `/opt/data/profiles/nura/scripts/` | Watchdog/automation scripts |
| `/opt/data/paperclip-runtime/` | Paperclip data |
| `/opt/data/Obsidian Vault/` | Obsidian knowledge base |
| `/opt/data/mcp-installs/` | MCP server installations |
| `/opt/hermes/` | Hermes installation |

## Related

- [[Integration-Status]] — Live health dashboard
- [[Zapier-Integration]] — Zapier bridge setup
- [[../Executive/Dashboard]] — Executive KPIs
- [[../SOPs/]] — Standard operating procedures
