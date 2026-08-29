# Hermes Daily Operations Report — 2026-08-09

**Generated:** 2026-08-09 02:03 UTC (22:03 EST Aug 8)  
**Inventory engine:** `nura-inventory-health.py`  
**Nodes probed:** Clinic (local) · Lab (SSH 72.60.163.140) · Edge (SSH 195.35.32.113) · 9 endpoints

---

## Overall Status: ⚠️ DEGRADED (improved)

| Node | Containers | Status | Δ from Aug 8 |
|------|-----------|--------|---------------|
| Clinic (72.61.71.211) | 40/40 up | ⚠️ DEGRADED (swap only) | Disk resolved ✓, +1 container, load ↓ |
| Lab (72.60.163.140) | 22/23 up | 🟢 HEALTHY | No change |
| Edge (195.35.32.113) | 2/9 up | ⚠️ DEGRADED (baseline) | No change |
| Endpoints | 9/9 open | 🟢 ALL HEALTHY | No change |

**Inventory line:** `clinic:40/40up | lab:22/23up | edge:2/9up | endpoints: 9/9 open`

---

## 🔴 SEV-2: Clinic Swap Saturation — PERSISTING (Day 4)

- **Swap:** 4.0/4.0 GiB used (4.6 MiB free) — unchanged since Aug 6
- **Memory:** 10.2/15.6 GiB used, 3.2 GiB free, 5.4 GiB available — slightly improved from yesterday (11.5→10.2 GiB used)
- **Load average:** 2.58 / 3.16 / 2.21 — dramatically improved from yesterday's 7.81/7.06/5.54. The disk-space recovery eliminated the I/O contention that was driving high load.
- **Top swap consumers (current):**
  - mcp-server-qdra (PID 1086448): 92.5 MB
  - node-MainThread (PID 818): 56.5 MB
  - npm exec paperclip (PID 581): 34.4 MB
  - behive × 2 (PID 18798–18799): 55.9 MB combined
  - hermes (PID 1086335): 26.2 MB
  - MCP servers (redis, hostinger, openemr, firecrawl, runpod): 8–24 MB each
- **Swap composition shifted:** Yesterday s6-svscan dominated at 28% of swap; today the top visible process is mcp-server-qdra at ~92 MB. The bulk of swap (~3.4 GiB) remains distributed across Docker containers and kernel caches not visible in per-process VmSwap.
- **Status:** 🔴 PERSISTING — requires scheduled maintenance window. Not worsening.

---

## 🟢 RESOLVED: Clinic Disk Normalized (77% from 86%)

- **Aug 8:** 86% (165G/193G used) — anomalous +9% spike in 24h
- **Aug 9:** 77% (148G/193G used) — returned to Aug 7 baseline
- **Resolution:** Disk space reclaimed (~17 GB). Probable cause was Docker layer/image accumulation or log buildup, cleared by automated or manual cleanup. The load drop from 7.81→2.58 confirms I/O pressure was the primary contributor to yesterday's elevated load.
- **Status:** 🟢 RESOLVED — monitoring for recurrence

---

## Failed Integrations

| Integration | Status | Detail |
|-------------|--------|--------|
| chatwoot-prepare-1 | ⚪ Exited (0) | Expected — one-time init container |
| Edge dokploy stack | ⚠️ 7 dead | 10-month stale baseline (unchanged) |
| Lab nuratech-test | ⚪ Exited (255) | 2-month stale test container |
| Edge dokploy.1 (tawk8…) | ⚠️ Dead | Part of stale edge dokploy stack |

No new failures. All 9/9 core endpoints verified open. Clinic containers at full 40/40 — the nura-nuratech-mapping-gw-relay-1 container returned (Up 3 days).

---

## Backup Status

| Check | Status |
|-------|--------|
| Latest backup | `nura-backup-20260808.tar.gz` (48 MB) ✓ |
| Backup chain | Aug 2–8 all confirmed on disk ✓ |
| Backup freshness | <24h — within SLA |
| Offsite (Restic/R2) | Not configured (R2_API_TOKEN missing) |
| Storage path | `/opt/data/uploads/` — 6 backups totaling ~288 MB |

**Note:** Backups are healthy. Aug 7 backup confirmed (was unconfirmed yesterday). Aug 8 backup generated today at 48MB — consistent with prior backups. Offsite DR remains the gap.

---

## Security Status

| Check | Status |
|-------|--------|
| TLS certs | `mcp.nuratech.ai` — cert endpoint unreachable this probe (openssl s_client failed) |
| SSH keys | `id_nura_clean` presumed functional (fleet SSH used in inventory) |
| Exposed ports | Managed via NPM (Clinic) + Traefik (Lab) ✓ |
| Firewall drift | Not audited this run |
| Credential hygiene | Not audited this run |
| DEA license renewal | Sep 30 deadline (52 days) — no action needed yet |

**⚠️ Note:** TLS cert check for mcp.nuratech.ai failed with `openssl s_client` — may be a probe issue or cert rotation. Prior report had expiry Sep 14 2026. Follow up manually.

---

## Clinical Safety Status

| Service | Status |
|---------|--------|
| OpenEMR | Up 5 days (healthy) ✓ |
| Mirth Connect | Up 5 days ✓ |
| Orthanc PACS | Up 5 days ✓ |
| OHIF Viewer | Up 3 days ✓ |
| ThaiRIS | Up 3 days (web + db) ✓ |
| Chatwoot | Up 3 days (rails + sidekiq + redis + postgres) ✓ |
| DocsGPT (Clinical AI) | Up 2 days — full stack healthy ✓ |
| Hermes gateway | Up 3 days (healthy), 0.0.0.0:8642 ✓ |
| api.nuratech.ai | Open ✓ |

**Note:** No AI clinical output review performed this run. No critical message delays detected. All clinical services operational.

---

## Resource Utilization

| Node | CPU | RAM | Swap | Disk |
|------|-----|-----|------|------|
| Clinic | Load 2.58 | 10.2/15.6G (65%) | **4.0/4.0G 🔴** | 77% 🟡 |
| Lab | Normal | 7.3/32.1G (23%) | — | 11% |
| Edge | Normal | 1.8/3.9G (46%) | — | 40% |

**Δ from yesterday:** Clinic load ↓64% (7.81→2.58), RAM ↓1.3G, Disk ↓9pp. All improvements attributable to disk-space recovery.

---

## Scheduled Jobs

| Job | Status |
|-----|--------|
| Health watchdog (5-min) | Running (silent) |
| Inventory engine | Ran (this run) |
| Daily backup (06:00 EST) | Aug 2–8 chain confirmed ✓ |
| Edge n8n × 2 | code-n8n-1: Up 2 days; n8n-n8n-6tp2rd-n8n-1: Up ~18 min (recent restart) |
| Obsidian LiveSync | Running (Clinic CouchDB) |
| Postiz scheduler | Up 5 days (temporal + postgres healthy) |
| DocsGPT | Up 2 days — 18/18 documents trained |

---

## Recommended Actions (Top 3)

1. **🔴 Schedule swap-clearing maintenance window (Day 4)** — Swap has been saturated for 4 days. Although load has improved with disk recovery, swap exhaustion still creates operational brittleness: any memory pressure spike will immediately cause OOM or severe slowdown. A controlled restart of top consumers (mcp-server-qdra at 92MB, behive, hermes, MCP fleet) during a low-usage window (~10 min downtime) would reclaim ~2-3 GiB. Without intervention, the first memory-intensive operation will trigger cascading failures.

2. **🟡 Investigate Edge n8n restart** — `n8n-n8n-6tp2rd-n8n-1` restarted ~18 minutes before this probe. Verify whether this was an automated restart (watchdog/cron) or a crash. Check Edge logs: `docker logs n8n-n8n-6tp2rd-n8n-1 --tail 100`.

3. **🟡 Verify TLS cert for mcp.nuratech.ai** — The `openssl s_client` probe failed this run (prior: Sep 14 2026 expiry). Confirm whether the cert is still valid or if there was a rotation. If the endpoint is down, classify as SEV-3.

---

*Report by Hermes — NURA OS CTO layer. Evidence from live fleet probes 2026-08-09 02:03 UTC.*  
*Inventory: /opt/data/profiles/nura/home/nura-ops/inventory.json*  
*Previous report: 2026-08-08 — disk SEV-2 resolved, load normalized, swap persistent.*
