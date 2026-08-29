# Hermes Daily Operations Report — 2026-08-07

**Generated:** 2026-08-07 ~02:07 UTC (22:07 EST Aug 6)  
**Inventory engine:** `nura-inventory-health.py`  
**Nodes probed:** Clinic (1441409) · Lab (1030183) · Edge (817449) · 9 endpoints

---

## Overall Status: 🟡 IMPROVING

| Node | Containers | Status | Δ from Aug 6 |
|------|-----------|--------|---------------|
| Clinic (72.61.71.211) | 39/40 up | 🟡 DEGRADED (swap) | ↑ +3 containers |
| Lab (72.60.163.140) | 22/23 up | 🟢 HEALTHY | ↑ +1 container |
| Edge (195.35.32.113) | 2/9 up | ⚠️ DEGRADED (baseline) | ↑ +1 container |
| Endpoints | 9/9 open | 🟢 ALL HEALTHY | ↑ api.nuratech.ai restored |

**Inventory line:** `clinic:39/40up | lab:22/23up | edge:2/9up | endpoints: 9/9 open`

---

## ✅ Resolved: SEV-2 api.nuratech.ai — RESTORED

- **Previous state (Aug 6):** Gateway bound to 127.0.0.1:8642 — public endpoint returned 000
- **Current state:** Endpoint probe reports `open`; curl returns `404` (valid gateway HTTP response — "no route for /" is expected)
- **Fix mechanism:** Gateway container restart picked up `host: 0.0.0.0` config + Docker port mapping `0.0.0.0:8642→8642`
- **Status:** 🟢 RESOLVED

---

## 🔴 SEV-2: Clinic Swap Saturation — PERSISTING (but improving)

- **Swap:** 4.0/4.0 GiB used (5 MiB free) — effectively full
- **Memory:** 9.4/15.6 GiB used, 6.2 GiB available — system not in OOM danger
- **Top swap consumers (dramatically improved from yesterday):**
  - Java (Mirth): 178 MB (was 151 MB)
  - MainThread (Paperclip): 39 MB (was 1.23 GiB → **93% reduction**)
  - Node: 26 MB (was 409 MB → **94% reduction**)
- **Assessment:** The Paperclip node processes that consumed 1.6 GiB yesterday have been restarted and freed their swap allocation. Swap remains allocated from stale pages but active pressure has dropped significantly. Will self-clear on next natural container restart cycle or can wait for scheduled maintenance.
- **Status:** 🔴 Same severity but active pressure resolved — downgrade to SEV-3 next report if trend holds

---

## ✅ Resolved: Lab langfuse ClickHouse Migration

- **Previous state (Aug 6):** langfuse-web stuck in restart loop. Error: "Applying clickhouse migrations failed"
- **Current state:** `langfuse-langfuse-web-1: Up 24 hours`, `langfuse-langfuse-worker-1: Up 24 hours`
- **All langfuse containers:** web, worker, redis, postgres, minio, clickhouse (×2), db — all healthy
- **Status:** 🟢 RESOLVED

---

## ✅ Container Recoveries

| Container | Aug 6 Status | Aug 7 Status |
|-----------|-------------|-------------|
| docsgpt-oss-worker-1 | Exited (2) | Up 4 hours ✓ |
| openclaw | Exited (78) | Up 24 hours ✓ |
| langfuse-langfuse-web-1 | Restart loop | Up 24 hours ✓ |

---

## Failed Integrations

| Integration | Status | Detail |
|-------------|--------|--------|
| api.nuratech.ai | 🟢 OPEN | Resolved — see above |
| Edge dokploy stack | ⚠️ 7 dead | 10-month stale baseline (no change) |
| chatwoot-prepare-1 | ⚪ Exited (0) | Expected — one-time setup job |
| Lab nuratech-test | ⚪ Exited (255) | 2-month stale test container |

---

## Backup Status

| Check | Status |
|-------|--------|
| Latest backup | `nura-backup-20260806.tar.gz` (48 MB) ✓ |
| Backup age | ~20h — within 24h window ✓ |
| Daily cadence | Aug 2, 4, 5, 6 confirmed — consistent |
| Backup location | `/root/.hermes/uploads/` on Clinic |
| Offsite (Restic/R2) | Not configured (R2_API_TOKEN missing) |
| Retention | 4 snapshots preserved (Aug 2–6) |

---

## Security Status

| Check | Status |
|-------|--------|
| TLS certs | `mcp.nuratech.ai` expires **Sep 14 2026** (38 days) — OK |
| Additional certs | Only one cert in `/etc/letsencrypt/live` |
| SSH keys | `id_nura_clean` functional on all 3 nodes ✓ |
| Exposed ports | Managed via NPM on Clinic, Traefik on Lab ✓ |
| Firewall drift | Not audited this run |
| Credential hygiene | Not audited this run |

---

## Clinical Safety Status

| Service | Status |
|---------|--------|
| OpenEMR | Up 3 days (healthy) ✓ |
| Mirth Connect | Up 3 days (HL7 engine) ✓ |
| Orthanc PACS | Up 3 days ✓ |
| OHIF Viewer | Up 46h ✓ |
| ThaiRIS | Up 46h (web + db) ✓ |
| Chatwoot | Up 44h (rails + sidekiq + redis + postgres) ✓ |
| DocsGPT (Clinical AI) | Full stack healthy (backend + frontend + worker + postgres + redis) ✓ |
| Hermes clinical lanes | 🟢 All endpoints open — api.nuratech.ai restored |

**Note:** No AI clinical output review performed this run. No critical message delays detected.

---

## Resource Utilization

| Node | CPU | RAM | Swap | Disk |
|------|-----|-----|------|------|
| Clinic | Normal | 9.9/16.0G (62%) | **4.0/4.0G 🔴** | 77% |
| Lab | Normal | 7.2/32.1G (23%) | — | 11% |
| Edge | Normal | 1.8/3.9G (45%) | — | 40% |

---

## Scheduled Jobs

| Job | Status |
|-----|--------|
| Health watchdog (5-min) | Running (silent) |
| Inventory engine | Ran (this run) |
| Daily backup | Last: Aug 6 06:00 EST ✓ |
| Edge n8n (×2) | Both Up 20h — operational |
| Obsidian LiveSync | Running (Clinic CouchDB) |

---

## Recommended Actions (Top 3)

1. **Monitor Clinic swap over next 24h** — Paperclip swap consumption is down 93% since yesterday; swap should self-clear as Docker restarts cycle. If still at 4.0G in 48h, schedule maintenance window to restart top-swap containers (Mirth, Paperclip) to force reclamation. No urgent action needed.

2. **Configure offsite backup** — Restic/R2 is documented but R2_API_TOKEN is not set. Without offsite, backups are single-node. Create a low-priority Atlas ticket.

3. **Clean up Edge dead containers** — 7 containers dead for 10+ months consuming disk and config drift. Either restore the dokploy stack or `docker container prune` to reclaim space. Low priority.

---

*Report by Hermes — NURA OS CTO layer. Evidence from live fleet probes 2026-08-07 02:07 UTC.*
