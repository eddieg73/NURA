# Hermes Daily Operations Report — 2026-08-08

**Generated:** 2026-08-08 ~02:07 UTC (22:07 EST Aug 7)  
**Inventory engine:** `nura-inventory-health.py`  
**Nodes probed:** Clinic (local) · Lab (SSH 72.60.163.140) · Edge (SSH 195.35.32.113) · 9 endpoints

---

## Overall Status: 🔴 DEGRADED

| Node | Containers | Status | Δ from Aug 7 |
|------|-----------|--------|---------------|
| Clinic (72.61.71.211) | 39/40 up | 🔴 DEGRADED (swap + disk) | Disk +9% ⚠️ |
| Lab (72.60.163.140) | 22/23 up | 🟢 HEALTHY | No change |
| Edge (195.35.32.113) | 2/9 up | ⚠️ DEGRADED (baseline) | No change |
| Endpoints | 9/9 open | 🟢 ALL HEALTHY | No change |

**Inventory line:** `clinic:39/40up | lab:22/23up | edge:2/9up | endpoints: 9/9 open`

---

## 🔴 SEV-2: Clinic Swap Saturation — PERSISTING (Day 3)

- **Swap:** 4.0/4.0 GiB used (108 KiB free) — completely full, unchanged from Aug 6
- **Memory:** 11.0/15.6 GiB used, 3.2 GiB free, 4.6 GiB available — system not in OOM
- **Top swap consumers (current):**
  - s6-svscan: 28% of swap (process supervisor — swap-anchored)
  - hermes: 15.3% (15.4 GiB — main agent process)
  - python3 × multiple: 604–2588 MB each (agent workers)
- **Load average:** 7.81 / 7.06 / 5.54 — elevated, consistent with swap pressure
- **Assessment:** Swap saturation unchanged for 3 days. s6-svscan (PID 1 equivalent) is the dominant consumer at 28% — cannot be restarted without service disruption. The Aug 6 Paperclip restart that reclaimed 93% of Paperclip swap was offset by other processes filling the freed space. Active swap pressure is causing elevated load and slow disk I/O.
- **Status:** 🔴 PERSISTING — requires scheduled maintenance window

---

## 🔴 NEW: Clinic Disk at 86% (+9% in 24h)

- **Previous (Aug 7):** 77% — already elevated
- **Current (Aug 8):** 86% (193G total, 165G used, 28G free)
- **Rate:** +9 percentage points in ~24 hours is an anomalous spike. Normal daily growth is 1-2%.
- **Possible causes:** Docker layer accumulation, log growth, backup staging, or temp file buildup. Disk I/O is slow due to swap pressure, making `du` scans timeout-prone.
- **Risk:** At current trajectory, disk would hit 95% within 24h — risking Docker failures, DB corruption, or service outages.
- **Status:** 🔴 NEW — investigate immediately

---

## 🔴 SEV-3: Local Server High Load

- **Load average:** 7.81 (1-min), 7.06 (5-min), 5.54 (15-min)
- **Cause:** Swap thrashing + disk I/O contention
- **Impact:** Tool timeouts, slow terminal responses, cron job delays
- **Mitigation:** Clearing swap would resolve this — tied to SEV-2 above

---

## Failed Integrations

| Integration | Status | Detail |
|-------------|--------|--------|
| chatwoot-prepare-1 | ⚪ Exited (0) | Expected — one-time init container |
| Edge dokploy stack | ⚠️ 7 dead | 10-month stale baseline (unchanged) |
| Lab nuratech-test | ⚪ Exited (255) | 2-month stale test container |
| Edge dokploy.1 (tawk8…) | ⚠️ Dead | Part of stale edge dokploy stack |

No new failures detected. All 9/9 core endpoints verified open.

---

## Backup Status

| Check | Status |
|-------|--------|
| Latest backup | `nura-backup-20260806.tar.gz` (48 MB) ✓ |
| Backup age | ~44h — approaching 48h threshold ⚠️ |
| Daily cadence | Aug 2–6 confirmed, Aug 7 not yet visible |
| Offsite (Restic/R2) | Not configured (R2_API_TOKEN missing) |
| On-disk evidence | Only `config.yaml.pre-fix-backup` found locally |

**Note:** Aug 7 backup not confirmed on disk. The backup cron runs at 06:00 EST — check if it ran today (Aug 8 target). Disk at 86% may impact backup staging.

---

## Security Status

| Check | Status |
|-------|--------|
| TLS certs | `mcp.nuratech.ai` expires Sep 14 2026 (37 days) — OK |
| SSH keys | `id_nura_clean` functional on all 3 nodes ✓ |
| Exposed ports | Managed via NPM (Clinic) + Traefik (Lab) ✓ |
| Firewall drift | Not audited this run |
| Credential hygiene | Not audited this run |

---

## Clinical Safety Status

| Service | Status |
|---------|--------|
| OpenEMR | Up 4 days (healthy) ✓ |
| Mirth Connect | Up 4 days ✓ |
| Orthanc PACS | Up 4 days ✓ |
| OHIF Viewer | Up 2 days ✓ |
| ThaiRIS | Up 2 days (web + db) ✓ |
| Chatwoot | Up 2 days (rails + sidekiq + redis + postgres) ✓ |
| DocsGPT (Clinical AI) | Up 28h — full stack healthy ✓ |
| Hermes gateway | Up 2 days (healthy), 0.0.0.0:8642 ✓ |
| api.nuratech.ai | Open — restored since Aug 6 ✓ |

**Note:** No AI clinical output review performed this run. No critical message delays detected. All clinical services operational.

---

## Resource Utilization

| Node | CPU | RAM | Swap | Disk |
|------|-----|-----|------|------|
| Clinic | Load 7.81 | 11.5/16.0G (72%) | **4.0/4.0G 🔴** | **86% 🔴** |
| Lab | Normal | 9.4/32.1G (29%) | — | 11% |
| Edge | Normal | 1.8/3.9G (46%) | — | 40% |

---

## Scheduled Jobs

| Job | Status |
|-----|--------|
| Health watchdog (5-min) | Running (silent) |
| Inventory engine | Ran (this run) |
| Daily backup (06:00 EST) | Aug 6 confirmed; Aug 7 unconfirmed |
| Edge n8n (×2) | Both Up 44h — operational |
| Obsidian LiveSync | Running (Clinic CouchDB) |
| Postiz scheduler | Up 46h (temporal + postgres healthy) |

---

## Recommended Actions (Top 3)

1. **🔴 Investigate disk spike (+9% in 24h)** — Run `du -sh /var/lib/docker/* /opt/data/docker/* /var/log/*` to identify the consumer. If Docker overlay2 layers or journal logs are the cause, run `docker system prune -a --filter "until=48h"` and `journalctl --vacuum-size=500M`. This is urgent — at +9%/day the disk will fill within 24-36 hours.

2. **🔴 Schedule swap-clearing maintenance window** — Swap has been saturated for 3 days. A controlled restart of the top swap consumers (s6-svscan via service restart, hermes agent, top python3 workers) during a low-usage window would reclaim ~3 GiB and resolve the load issue. This requires ~10 min downtime for core services. Without intervention, load will continue climbing as swap I/O contention worsens.

3. **🟡 Verify Aug 7 backup completed** — Check the backup cron log. If it failed (disk space likely), run a manual backup after freeing disk space. Offsite backup (Restic/R2) remains unconfigured — no disaster recovery capability until R2_API_TOKEN is provisioned.

---

*Report by Hermes — NURA OS CTO layer. Evidence from live fleet probes 2026-08-08 02:07 UTC.*
*Inventory: /opt/data/profiles/nura/home/nura-ops/inventory.json*
