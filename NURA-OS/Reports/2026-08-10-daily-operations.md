# Hermes Daily Operations Report — 2026-08-10

**Generated:** 2026-08-10 02:13 UTC (22:13 EST Aug 9)  
**Inventory engine:** `nura-inventory-health.py`  
**Nodes probed:** Clinic (72.61.71.211) · Lab (72.60.163.140) · Edge (195.35.32.113) · 9 endpoints

---

## Overall Status: ⚠️ DEGRADED

| Node | Containers | Status | Δ from Aug 9 |
|------|-----------|--------|---------------|
| Clinic (72.61.71.211) | 40/40 up | ⚠️ DEGRADED (swap only) | Disk improved, load normalized, openclaw restarted |
| Lab (72.60.163.140) | 27/29 up | ⚠️ DEGRADED | LibreChat restarted (4h uptime), +5 containers visible in scan |
| Edge (195.35.32.113) | 2/9 up | ⚠️ DEGRADED (baseline) | n8n stabilized (24h uptime), 7 stale dead |
| Endpoints | 9/9 open | 🟢 ALL HEALTHY | No change |

**Inventory line:** `clinic:40/40up | lab:27/29up | edge:2/9up | endpoints: 9/9 open`

---

## 🔴 SEV-2: Clinic Swap Saturation — PERSISTING (Day 5)

- **Swap:** 4,095/4,095 MB used (0 MB free) — unchanged since Aug 6
- **Memory:** 10,773/15,992 MB used (67%), 5,218 MB available — slight increase from 10,489 MB yesterday
- **Load average:** 1.62 / 1.90 / 1.84 — **normalized** (↓37% from 2.58 yesterday, ↓79% from 7.81 on Aug 8)
- **Disk:** 76% (145G/193G) — continued improvement (77% → 76% → 86% peak Aug 8)
- **Status:** 🔴 PERSISTING Day 5. Load and disk have fully recovered from the Aug 8 spike, but swap remains 100% consumed. The system is stable under current load but has zero swap headroom for any memory pressure event.
- **Root cause candidate:** Docker overlay + MCP server proliferation (~15 MCP servers + 40 containers) on 16 GB RAM. The mcp-server-qdra process (92 MB swap) remains the largest single consumer.

---

## 🟡 OBSERVATION: Clinic openclaw Daily Restart Pattern

- **Aug 8 02:03 UTC:** Up 17 hours → started ~Aug 7 09:00 UTC
- **Aug 9 02:03 UTC:** Up 17 hours → started ~Aug 8 09:00 UTC  
- **Aug 10 02:07 UTC:** Up 18 hours → started ~Aug 9 08:00 UTC

Pattern: openclaw is restarting approximately every 24 hours (daily restart ~08:00–09:00 UTC). This may be an intentional cron, a watchdog cycle, or a memory-leak crash. Verify intent and adjust monitoring threshold if expected behavior.

---

## 🟡 OBSERVATION: Lab LibreChat Stack Restarted

- **LibreChat:** Up 4 hours (was multi-day stable previously)
- **rag_api:** Up 4 hours (restarted with LibreChat)
- **vectordb:** Up 4 hours (restarted with LibreChat)

The entire LibreChat stack (chat + rag + vector + meilisearch + mongodb) restarted ~4 hours ago (~22:00 UTC Aug 9). This is a coordinated restart — likely an update, config change, or Docker Compose restart rather than a crash. No SEV — investigate if expected.

---

## 🟡 OBSERVATION: Gateway Internal Bind Regression

- **Probe:** `docker exec hermes-gateway sh -c "grep -i ':21C2' /proc/net/tcp"`
- **Result:** `0100007F:21C2` = **127.0.0.1:8642** (NOT 0.0.0.0:8642)
- **08-04 fix:** Required `00000000:21C2` (0.0.0.0:8642) for the API server
- **External access:** Working via Docker port mapping (endpoint probe: open ✓)
- **Impact:** Internal Docker network access to the API server may be degraded. External access unaffected.

The gateway has been Up 4 days — the bind regression likely dates to the Aug 6 restart. Since external probes still succeed, classify as SEV-3. Repair at next scheduled maintenance.

---

## Failed Integrations

| Integration | Node | Status | Detail |
|-------------|------|--------|--------|
| admin-panel | Lab | ⚪ Created | Container created but never started — intentional? |
| nuratech-test | Lab | ⚪ Exited (255) | 2-month stale test container (unchanged) |
| Edge dokploy stack | Edge | ⚠️ 7 dead/exited | 11-month stale baseline (unchanged) |

No new failures. All 9/9 core endpoints verified open. The Lab container count increase (23→29) is from broader inventory scan catching previously uncounted containers (paperclip, medisun, n8n) — all healthy.

---

## Backup Status

| Check | Status |
|-------|--------|
| Latest backup | `nura-backup-20260809.tar.gz` (76 MB) ✓ |
| Backup chain | Aug 2–9 all confirmed on disk ✓ |
| Backup freshness | <24h — within SLA |
| Offsite (Restic/R2) | Not configured |
| Storage path | `/opt/data/uploads/` — 7 backups totaling ~411 MB |

**Δ from yesterday:** Aug 9 backup generated (76 MB). Chain complete Aug 2–9. Offsite DR remains the gap.

---

## Security Status

| Check | Status |
|-------|--------|
| TLS certs | Not audited this run (yesterday: mcp.nuratech.ai probe failed) |
| SSH keys | `id_nura_clean` functional (fleet inventory succeeded) |
| Exposed ports | Managed via NPM (Clinic) + Traefik (Lab) ✓ |
| Firewall drift | Not audited this run |
| Credential hygiene | Not audited this run |
| DEA license renewal | Sep 30 deadline (51 days) — no action needed yet |

---

## Clinical Safety Status

| Service | Location | Status |
|---------|----------|--------|
| OpenEMR | Clinic | Up 6 days (healthy) ✓ |
| Mirth Connect | Clinic | Up 6 days ✓ |
| Orthanc PACS | Clinic | Up 6 days ✓ |
| OHIF Viewer | Clinic | Up 4 days ✓ |
| ThaiRIS | Clinic | Up 4 days (web + db) ✓ |
| Chatwoot | Clinic | Up 4 days (rails + sidekiq + redis + postgres) ✓ |
| DocsGPT (Clinical AI) | Clinic | Up 3 days — 18/18 trained ✓ |
| Hermes gateway | Clinic | Up 4 days (healthy), external:8642 open ✓ |
| api.nuratech.ai | Clinic | Open ✓ |
| Mattermost | Clinic | Up 6 days (healthy) ✓ |

All clinical services operational. No AI clinical output review performed this run. No critical message delays detected. **Note:** Gateway internal bind regression (127.0.0.1 vs 0.0.0.0) does not affect external clinical access.

---

## Resource Utilization

| Node | Load | RAM | Swap | Disk | Trend |
|------|------|-----|------|------|--------|
| Clinic | 1.62 | 10.8/15.6G (67%) | **4.0/4.0G 🔴** | 76% | Load ↓37%, Disk ↓1pp |
| Lab | Normal | 8.2/32.1G (25%) | — | 13% | RAM +0.9G, Disk stable |
| Edge | Normal | 1.8/3.9G (45%) | — | 40% | Stable |

**Δ from yesterday:** Clinic load fully normalized (1.62 vs 2.58). RAM slightly up (+0.6G). Disk continues incremental improvement. Lab RAM up due to additional containers scanned.

---

## Scheduled Jobs

| Job | Status |
|-----|--------|
| Health watchdog (5-min) | Running (silent) ✓ |
| Inventory engine | Ran (this run) ✓ |
| Daily backup (06:00 EST) | Aug 2–9 chain confirmed ✓ |
| Edge n8n × 2 | code-n8n-1: Up 3 days; n8n-n8n-6tp2rd: **Up 24 hours** (stabilized after yesterday's restart) |
| Obsidian LiveSync | Running (Clinic CouchDB, Up 6 days) ✓ |
| Postiz scheduler | Up 3 days (temporal + postgres healthy) ✓ |
| DocsGPT | Up 3 days — 18/18 trained ✓ |
| LibrewChat (Lab) | **Up 4 hours** — stack restart detected |

---

## Recommended Actions (Top 3)

1. **🔴 Schedule swap-clearing maintenance window (Day 5)** — Swap has been 100% saturated for 5 consecutive days. The system is stable under current load (1.62 load average, 5.2 GB available RAM) but has absolutely zero buffer for any memory pressure event. A controlled restart of the top swap consumer (mcp-server-qdra at ~92 MB) plus a targeted Docker daemon restart during low-usage window would reclaim ~1-2 GiB and restore operational headroom. Without intervention, the next memory-intensive operation (large model load, concurrent MCP calls, or backup run) risks OOM kill cascades. **Window:** 15 min, impact: brief MCP + Hermes interruption.

2. **🟡 Investigate LibreChat stack restart** — The entire Lab LibreChat deployment (chat, rag_api, vectordb, meilisearch, mongodb) restarted ~4 hours ago. Verify whether this was intentional (update/config change) or a crash. Check: `docker logs LibreChat --tail 50` on Lab.

3. **🟡 Verify gateway internal bind (08-04 regression)** — The hermes-gateway is listening on 127.0.0.1:8642 internally instead of 0.0.0.0:8642 per the Aug 4 fix. While external access works via Docker port forwarding, other containers on the Docker network may be unable to reach the API server directly. Verify `api_server.host` in the gateway config and correct to `0.0.0.0` at next opportunity. Impact: SEV-3 (degraded internal routing, no external outage).

---

*Report by Hermes — NURA OS CTO layer. Evidence from live fleet probes 2026-08-10 02:07 UTC.*  
*Inventory: /opt/data/profiles/nura/home/nura-ops/inventory.json*  
*Previous report: 2026-08-09 — load normalized, disk resolved, swap persistent Day 4.*
