# Hermes Daily Operations Report
**Date:** 2026-08-05 02:04 UTC  
**Inventory:** `/opt/data/profiles/nura/home/nura-ops/inventory.json`  
**Watchdog:** Active (5-min cadence)

---

## Overall Status: 🟡 DEGRADED

| Node | Containers | Up | Down/Degraded | Status |
|------|-----------|----|---------------|--------|
| **Clinic** (72.61.71.211) | 39 | 37 | 2 | Healthy |
| **Lab** (72.60.163.140) | 26 | 22 | 4 | Degraded |
| **Edge** (195.35.32.113) | 8 | 1 | 7 | Failed |
| **Endpoints** | 9 | 8 | 1 | Degraded |

**Summary:** 60 healthy · 6 degraded (restart loop/created) · 9 failed (exited/dead) · 1 endpoint closed

---

## 🔴 Critical Incidents

### SEV-2: `api.nuratech.ai` endpoint closed
- **Status:** HTTP 000, cert unreachable (connection refused in 2ms)
- **First detected:** 2026-08-04 (remote gateway saga)
- **Current state:** `hermes-gateway` container is UP on clinic (0.0.0.0:8642), but the public endpoint does not route traffic. NPM proxy (nginx-proxy-manager-app-1) restarted ~50 min ago; may need forward rule verification.
- **Impact:** Remote Hermes gateway inaccessible from external clients
- **Evidence:** `curl -s -m 5 -o /dev/null -w '%{http_code}' https://api.nuratech.ai` → `000` in 2ms

### SEV-3: `openclaw` container exited (78) — 19h downtime
- **Status:** Exited (78) as of Aug 4 ~07:00 UTC
- **Impact:** Browser automation agent offline; no desktop-driven tasks
- **Note:** Exit code 78 suggests configuration error or signal-related exit

### SEV-3: `hermes-agent` container exited (0) — 32h downtime
- **Status:** Exited (0) as of Aug 3 ~18:00 UTC  
- **Impact:** Core agent container not running; Hermes sessions run via gateway
- **Note:** Clean exit (0) — may be intentional shutdown without restart policy

### SEV-3: Lab — `langfuse` restart loop
- **Status:** Restarting (1) every ~41s
- **Impact:** Langfuse observability unavailable; `langfuse-langfuse-web-1` stuck in "Created" state (never started)
- **Dependencies:** langfuse-db, langfuse-redis, langfuse-clickhouse all healthy

### SEV-3: Lab — `farmer_nginx` restart loop
- **Status:** Restarting (1) every ~28s
- **Impact:** Farmer app frontend unavailable (Oussama's Laravel project)

### SEV-4: Edge node — Dokploy stack dead (10 months)
- **Status:** 7/8 containers exited or dead; only `n8n` running
- **Impact:** Edge node has no functional deployment platform
- **Note:** This is a known, long-standing issue; edge node has been in this state since ~Oct 2025

---

## Failed Integrations

| Integration | Failure | First Detected | Status |
|-------------|---------|---------------|--------|
| `api.nuratech.ai` | Public endpoint unreachable | 08-04 | 🔴 Open |
| `openclaw` | Container exited (78) | 08-04 07:00 UTC | 🔴 Open |
| `hermes-agent` | Container exited (0) | 08-03 18:00 UTC | 🔴 Open |
| `langfuse` (lab) | Restart loop | 08-04 ~20:00 UTC | 🔴 Open |
| `farmer_nginx` (lab) | Restart loop | Unknown | 🔴 Open |
| Edge dokploy stack | Dead (10 months) | ~Oct 2025 | 🟡 Known |

---

## Backup Status: 🔴 UNKNOWN

- `/opt/data/backups/` is **empty** — no backup artifacts found
- `nura-backup.sh` script exists (`/opt/data/scripts/nura-backup.sh`, last modified Aug 1) but no evidence of recent execution
- No crontab accessible from this environment to verify schedule
- **Risk:** Backup status cannot be confirmed — this is a SEV-2 gap

---

## Security Status: 🟡 REVIEW NEEDED

- **Certs:** Unable to verify NPM Let's Encrypt certs directly (Docker not available in this environment). `api.nuratech.ai` SSL handshake fails entirely (connection refused, not cert error).
- **Swap exhaustion:** 4.0 GiB / 4.0 GiB swap used (99.97%) — sustained full swap is a stability risk
- **Docker socket:** Not accessible from this session — limits direct inspection
- **No unauthorized access detected** (from available telemetry)
- **No exposed ports beyond documented services**

---

## Clinical Safety Status: 🟢 NOMINAL

- **OpenEMR:** Up and healthy (openemr-zklo-openemr-1, 44h uptime, healthy)
- **Mirth Connect:** Up and healthy (44h uptime)
- **Orthanc PACS:** Up and healthy (44h uptime)
- **Qdrant:** Up (44h)
- **Redis:** Up (44h)
- **No delayed critical messages detected** (from available inventory)
- **No failed clinical interfaces** — AI output pathways nominal
- **⚠️ Note:** Cannot verify clinical message/event integrity without Docker access; surface-level health checks are green

---

## Resource Utilization

| Resource | Clinic | Lab | Edge | Host (this node) |
|----------|--------|-----|------|-------------------|
| **Memory** | 5,280 / 15,992 MB (33%) | 6,230 / 32,094 MB (19%) | 1,507 / 3,916 MB (38%) | 5.1 / 15 GiB used |
| **Disk** | 57% | 10% | 39% | 57% (109G / 193G) |
| **Swap** | — | — | — | 🔴 **4.0/4.0 GiB (100%)** |
| **Load** | — | — | — | 0.95 (1-min), 1.66 (5-min) |
| **Uptime** | — | — | — | 1 day 20:29 |

### Swap Alert 🔴
Host swap is fully saturated (4,192,608 / 4,194,300 kB). This is the recurring condition flagged by the founder on 08-04. Swap refill prevention requires identifying the consumer and restarting the offending container, not just clearing swap.

---

## Scheduled Jobs

| Job | Cadence | Status |
|-----|---------|--------|
| Health watchdog (`nura-health-watchdog.sh`) | 5-min | ✅ Running (last updated 01:00) |
| Inventory refresh (`nura-inventory-health.py`) | Daily 02:00 | ✅ Just executed (02:03) |
| Backup (`nura-backup.sh`) | Unknown | 🔴 No evidence of recent execution |
| Security scan | Daily 02:00 | ⚠️ Not verifiable from this session |
| Docker health sweep | 15-min | ⚠️ Not verifiable |

---

## Recommended Actions (Top 3)

1. **🔴 Restore `api.nuratech.ai` routing** — Verify NPM proxy forward rule targets `hermes-gateway:8642` (container name, not 127.0.0.1). The container is up and bound to 0.0.0.0:8642; the break is at the NPM proxy layer. Check the forward rule and SSL cert assignment.

2. **🔴 Investigate swap saturation** — 100% swap is a stability risk. Identify the swap consumer (likely a container with memory leak — check `langfuse` restart loop as candidate since it's crashing and respawning). Once identified, restart the offending container; do NOT just `swapoff/swapon` to clear it — find the root cause per the founder's 08-04 directive.

3. **🟡 Restore exited containers** — `openclaw` (19h down) and `hermes-agent` (32h down) need restart. Check restart policies and logs for root cause. The `langfuse` and `farmer_nginx` restart loops on lab also need log inspection to break the loop.

---

*Generated by Hermes CTO — NURA OS System Reliability Automation*  
*Next report: 2026-08-06 02:00 UTC*
