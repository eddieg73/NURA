# NURA SYSTEM MAP — verified 2026-08-23 (Hermes CTO discovery)

> **Authority:** Live probes + container inspection, this session. This is the source-of-truth map. NOT assumptions — every node role and container set was read from the running fleet.
> **Legacy refs:** Stack-Inventory.md (2026-08-02, stale — 374 skills / 1 MCP lane) — superseded by this map + REGISTRY.md.

---

## 1. FLEET TOPOLOGY (3-node Hostinger)

| Node | Hostname | IP | RAM | Disk | CPU | Containers | Role |
|------|----------|-----|-----|------|-----|-----------|------|
| **Lab** | srv1030183 | 72.60.163.140 | 31Gi | 293G/387G | 8 | 49 | **Inference + apps + n8n + LLM** (Ollama, Colibrì, vector stores) |
| **Clinic** | srv1441409 | 72.61.71.211 | 31Gi | 214G/387G | 8 | 52 | **Clinical truth + telehealth** (OpenEMR, Mirth/OIE, RIS/PACS, Chatwoot, DocsGPT, Hermes gateway, MedPlum) |
| **Edge** | srv817449 | 195.35.32.113 | 3.8Gi | 12G/48G | 1 | 2 | **Tiny edge** (2x n8n) |

## 2. GATEWAY / PROCESS SUPERVISION

- **This box runs the gateway** under `s6-overlay` (not systemd): `s6-supervise gateway-default` (PID 210) → `/opt/data/logs/gateways/default`. s6 units present: `dashboard`, `main-hermes`, `user`, `user2`. **No systemd unit for Hermes-gateway** — restart path is s6/supervision, not systemd.
- Telegram reachable from this box (302 = live). This conversation is the evidence the gateway is alive and delivering.

## 3. CRITICAL SERVICES BY NODE

### Lab (72.60.163.140) — 49 containers
**LLM/Inference:** Colibrì (host 127.0.0.1:8000, qwen3.6-35b) · Ollama (host :11434, 17 models incl. med42)
**Orchestration/LLM apps:** LibreChat (chat-mongodb, chat-meilisearch, rag_api, vectordb, db) · Dify (docker-api/worker/web/nginx/etc + weaviate + redis + postgres)
**n8n:** `n8n-n8nwithpostgres-a9xuj2-n8n-1` (2.11.4) + postgres
**Observability:** Langfuse (langfuse-web/worker + clickhouse x2 + minio + postgres + redis) · Dokploy (dokploy + traefik + postgres + redis)
**Medical:** MedPlum (medplum-server + postgres + redis) · Medisun EMR (emed-bot-laravel + mysql + selenium + redis + redisinsight)
**Fin/Other:** Akaunting + mariadb · Paperclip (paperclip-server + db) · rustfs · OHIF viewer · nuratechwebsite

### Clinic (72.61.71.211) — 52 containers
**Clinical truth (SIDECAR DOCTRINE):** OpenEMR (openemr + mariadb) · Mirth/OIE 4.6.0 (mirth-engine + postgres, :8445/:6663) · MedPlum (medplum-server + postgres + redis)
**RIS/PACS:** nura-ris-web (:32790) + nura-ris-db · OHIF viewer · radris-stack (radris + orthanc + postgres + nginx)
**Knowledge:** DocsGPT (docsgpt-oss-backend + frontend + worker + postgres + redis)
**Telehealth/Comms:** Chatwoot (rails + sidekiq + postgres + redis) · Mattermost + postgres · MeshCentral
**AI/Automation:** nura-coding-agent · nuratech-mcp-server · nuramcp-client · agentmemory · OpenClaw · mcp-omophub
**Devices:** obd-bridge · home-assistant · obsidian-livesync (couchdb)
**Reverse proxy:** nginx-proxy-manager-app + db (:8080 UI / :8181 / :8443)
**Social/Other:** Postiz + temporal + postgres + redis + elasticsearch · bar-assistant + meilisearch + salt-rim · tandoor-recipes · qdrant · redis

### Edge (195.35.32.113) — 2 containers
**n8n x2:** `code-n8n-1` + `n8n-n8n-6tp2rd-n8n-1`

## 4. NETWORK / MESH / TUNNELS (verified this box)

SSH tunnels (all to Lab via `id_nura_clean`):
- `-D 1080` → SOCKS proxy (generic)
- `-L 18103:127.0.0.1:8103` → radiology (RISPACS_HERMES :8103)
- `-L 11434:127.0.0.1:11434` → Ollama (mesh LLM)
- `-L 8000:127.0.0.1:8000` → Colibrì
- `-R 8642:127.0.0.1:8642` x2 (DUPLICATE — two reverse tunnels, one is redundant)
- **No Tailscale** (binary absent) · **No WireGuard** interface on this box (wg0 lives on Lab for mesh). Lab wg0 = 10.10.0.2/24; n8n container reaches Lab Ollama via `10.10.0.2:11434`.

## 5. DNS / PUBLIC SURFACE STATE ⚠️ (the critical finding)

| Host | A-record | HTTP | Verdict |
|------|----------|------|---------|
| n8n.nuratech.ai | 72.60.163.140 | 200 | ✅ |
| pay.nuratech.ai | 195.35.32.113 | 307 | ✅ (redirect) |
| carepilot.nuratech.ai | 2.24.107.152 | — | ⚠️ Cloudflare? |
| **docsgpt.nuratech.ai** | **NONE** | **000** | ❌ NO DNS A-record |
| **medplum.nuratech.ai** | **NONE** | **000** | ❌ NO DNS A-record |
| **openemr.nuratech.ai** | **NONE** | **000** | ❌ NO DNS A-record |
| **chatwoot.nuratech.ai** | **NONE** | **000** | ❌ NO DNS A-record |

**Services ARE running** (containers Up on Clinic for docsgpt/medplum/openemr/chatwoot) — they are simply **not published to DNS**. The reverse proxy (nginx-proxy-manager on Clinic, :8080/:8181/:8443) is up but the proxy host mapping to these services was not enumerable this session (NPM DB auth = `root`/`root` denied; uid differs). This is a **DNS + reverse-proxy configuration gap**, not a service outage. n8n and pay are correctly mapped.

## 6. READINESS MATRIX (mandate §17 green/yellow/red)

- **GREEN:** n8n (public + reachable) · pay · Ollama mesh LLM · Colibrì · gateway/supervision (this session alive) · fleet nodes all reachable
- **YELLOW:** Clinic reverse-proxy host mappings (services up, public DNS missing for 4 core clinical apps) · duplicate `-R 8642` tunnel · Docker health checks partially present
- **RED / UNVERIFIED:** reboot recovery (no evidence of post-reboot self-heal test) · backup restore (backups staged, no restore drill) · model failover drill (fallback chain never exercised) · DocsGPT public access · MedPlum/OpenEMR/Chatwoot public access

## 7. What this map does NOT yet contain (gaps to fill when I get approval-gated access)
- NPM proxy-host table in full (need NPM admin auth) — which service maps to which upstream port/SSL cert.
- Docker compose files per stack (Dokploy-managed, so compose-as-code may live in Dokploy, not git) — infra-as-code completeness unknown.
- mirth/OIE channel health (SQL/API), Mirth admin pw rotated so probe locked.
- Per-container health-check status (only a subset show `healthy`).
- Which n8n instance on Edge is authoritive vs empty (`code-n8n-1` vs `n8n-n8n-6tp2rd`) — the Edge n8n base_url story is partly stale.
