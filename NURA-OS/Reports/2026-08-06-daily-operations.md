# Hermes Daily Operations Report — 2026-08-06

**Generated:** 2026-08-06 ~08:30 EST  
**Inventory engine:** `nura-inventory-health.py`

---

## Overall Status: 🔴 DEGRADED

| Node | Containers | Status |
|------|-----------|--------|
| Clinic (1441409 · 72.61.71.211) | 36/40 up | ⚠️ DEGRADED |
| Lab (1030183 · 72.60.163.140) | 21/24 up | ⚠️ DEGRADED |
| Edge (817449 · 195.35.32.113) | 1/8 up | ⚠️ DEGRADED (baseline) |
| Endpoints | 8/9 open | 🔴 api.nuratech.ai UNHEALTHY |

---

## 🔴 Critical Incidents

### SEV-2: api.nuratech.ai — DOWN (remote gateway unreachable)
- **First detected:** 2026-08-06 inventory run
- **Root cause:** Hermes gateway container binding to 127.0.0.1:8642 despite config showing `host: 0.0.0.0`
  - TCP bind proof: `0100007F:21C2` = 127.0.0.1:8642 ✗ (needs `00000000:21C2`)
  - Config on disk: `api_server.extra.host: 0.0.0.0` ✓
  - Env: `API_SERVER_HOST=0.0.0.0` ✓
  - **Fix applied but gateway not restarted** — the config change requires a container restart to take effect
- **Impact:** api.nuratech.ai returns 000; external clients cannot reach the gateway
- **Status:** Needs gateway restart to pick up 0.0.0.0 bind

### SEV-2: Clinic swap CRITICAL — 100% full (4.0/4.0 GiB)
- **80 KiB free** — effectively exhausted
- **Top swap consumers:**
  - Paperclip orchestrator (PID 15615): 1.23 GiB swap
  - Paperclip backend (PID 15614): 409 MiB swap
  - Mirth Connect Java (PID 2206): 151 MiB swap
- **Hermes-gateway CPU:** 239.93% (3.36 GiB RAM / 21.5%)
- **Memory available:** 7.5 GiB — system not crashing but swap pressure is extreme
- **Status:** Swap was 3.3G on 08-03 (YELLOW), now full. Self-clear expected at natural container restart but root consumer (Paperclip node processes) persists

### SEV-3: Lab langfuse — restart loop (ClickHouse migration failure)
- **First detected:** 2026-08-06
- **Error:** `Applying clickhouse migrations failed` — database unreachable or CLICKHOUSE_PASSWORD encoding issue
- **langfuse-web:** Stuck in `Created` state (never started)
- **Status:** langfuse main container restarting every ~60s

---

## ⚠️ Failed Integrations

| Integration | Status | Detail |
|-------------|--------|--------|
| api.nuratech.ai | 🔴 DOWN | Gateway binds 127.0.0.1 — need restart |
| docsgpt-oss-worker | 🔴 Exited (2) | Clinic — worker crash, not restarted |
| openclaw | ⚠️ Exited (78) | Clinic — exit code 78, 43h ago |
| hermes-agent | ⚪ Exited (0) | Clinic — clean exit 2d ago (expected) |
| chatwoot-prepare | ⚪ Exited (0) | Clinic — setup job, expected |
| Edge dokploy stack | ⚠️ Dead | 7 containers dead 10mo (known baseline) |

---

## Backup Status

| Check | Status |
|-------|--------|
| Latest backup | `nura-backup-20260805.tar.gz` (Aug 5, ~47MB) |
| Backup age | ~27h — within 48h window ✓ |
| Backup location | `/root/.hermes/uploads/` on Clinic |
| Restic/R2 offsite | SKIPPED — R2_API_TOKEN not configured in .env |
| Automated cron | None found (manual or script-triggered) |
| Retention | 3 snapshots preserved (Aug 2, 4, 5) |

---

## Security Status

| Check | Status |
|-------|--------|
| TLS certs | `mcp.nuratech.ai` expires **Sep 14 2026** (39 days) — OK |
| Other certs | Only one cert in `/etc/letsencrypt/live` — single-domain |
| SSH keys | `id_nura_clean` functional on all 3 nodes ✓ |
| Exposed ports | NPM handling 80/443 on Clinic ✓ |
| Firewall | Not audited this run |
| Credential hygiene | Not audited this run |
| Docker exposed ports | Gateway on 8642 (internal only currently — broken) |

---

## Clinical Safety Status

| Check | Status |
|-------|--------|
| OpenEMR | Not directly probed — assumed operational (no alerts) |
| Mirth Connect | Running ✓ (Java PID 2206, 164 MiB) |
| Orthanc PACS | Running ✓ |
| OHIF Viewer | Running ✓ |
| ThaiRIS | Running ✓ (web + db) |
| Chatwoot | Running ✓ (rails + sidekiq + redis + postgres) |
| Clinical AI (DocsGPT) | Running ✓ (backend + frontend, worker crashed) |
| Hermes clinical lanes | Degraded — api.nuratech.ai down impacts external clinical access |

---

## Resource Utilization

| Node | CPU | RAM | Swap | Disk |
|------|-----|-----|------|------|
| Clinic | High (gateway 240%) | 8.1/15 GiB (7.5 avail) | **4.0/4.0G 🔴** | 145/193G (75%) |
| Lab | Normal | — | 0/4.0G ✓ | 39/387G (10%) |
| Edge | Normal | — | 0/2.0G ✓ | 19/48G (40%) |

**Docker disk (Clinic):** 67.66 GiB images · 22.96 GiB build cache (100% reclaimable) · 7.77 GiB volumes reclaimable

---

## Scheduled Jobs

| Job | Status |
|-----|--------|
| Health watchdog (5-min) | Running (silent) |
| Swap watchdog (30-min) | Should have alerted on clinic swap — verify |
| Daily backup | Manual only — last 08-05 |
| Inventory engine | Ran (this run) |
| Cron backup jobs | None configured in crontab |

---

## Recommended Actions (Top 3)

1. **Restart hermes-gateway container** to apply `host: 0.0.0.0` config — restores api.nuratech.ai. Command: `docker compose -f /opt/hermes/docker-compose.yml up -d --force-recreate hermes-gateway` (⚠️ requires authorization per gateway-restart policy; this is the remote-gateway exception case)

2. **Investigate & resolve Clinic swap saturation** — identify why Paperclip node processes (orchestrator + backend) are consuming 1.6 GiB swap. Options: restart paperclip containers to clear swap, or increase swapfile to 8 GiB as interim buffer. Root cause is likely memory pressure from hermes-gateway (3.36 GiB) + Paperclip node processes.

3. **Fix Lab langfuse ClickHouse migration** — check CLICKHOUSE_PASSWORD encoding in langfuse env, verify langfuse-clickhouse container is healthy and reachable. Restart langfuse stack after fix.

---

*Report by Hermes — NURA OS CTO layer. Evidence from live fleet probes 2026-08-06.*
