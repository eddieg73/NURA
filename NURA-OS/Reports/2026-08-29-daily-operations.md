# Hermes Daily Operations Report

**Date:** 2026-08-29 02:02 UTC · **Engine:** `nura-inventory-health.py` · **Source:** `~/nura-ops/inventory.json`

## Overall Status — HEALTHY
| Node | Host | Containers up | Mem (MB) | Disk |
|------|------|---------------|----------|------|
| clinic | 72.61.71.211 | 40/40 | 11,062/32,094 (34%) | 65% |
| lab | 72.60.163.140 | **40/40** | 11,147/32,094 (35%) | 65% |
| edge | 195.35.32.113 | 8/8 | 2,224/3,916 (57%) | 29% |

**Fleet containers: 88/88 up.** **Endpoints probed: 9/9 open** (`api.nuratech.ai, hermes-gateway, orthanc, mirth, npm, mattermost, redis, qdrant, openemr`).

**Positive delta vs 08-28:** the **lab node fully recovered** — 35/40 → **40/40**. The Dokploy deploy-manager crash-loop (08-27→present) that took the lab to degraded is resolved; all lab containers Up.

All 9 critical endpoint ports re-validated against each container's *actual published* host port (no stale-port false positives): hermes-gateway 8642, mirth 8445, orthanc 8042, npm 8181, mattermost 32772, redis 32770, qdrant 32776, openemr 32777 — all match published ports ✓. (Port probes confirmed live via socket here.)

## Critical Incidents
- **None.** No SEV-1/SEV-2. No patient-facing service down. OpenEMR, Mirth, Orthanc/DICOM, Hermes-gateway, RadIntel orchestrator, RIS-web, Medplum, LibreChat, Langfuse, Akaunting, rustfs all Up.

## Failed Integrations
1. **api.nuratech.ai — self-signed TLS cert (TRAEFIK DEFAULT CERT).** *Not an outage* — TCP 80/443 are open and the TLS handshake completes — but the cert is `CN=TRAEFIK DEFAULT CERT` with a SAN pointing at an internal container ID (`192da9...traefik.default`), **not** `api.nuratech.ai`. Any external HTTPS client rejects it (`curl` exit 60, "self-signed certificate"). **Caveat:** the engine logs it `open` because it only probes TCP:80, masking the HTTPS trust break (the pitfall: probe port ≠ what a real client sees). Verdict valid 2026-08-03 → 2027-08-03.
2. **emr.hrthouse.com — 000 (KNOWN, pre-existing).** OpenEMR's public DNS mispointed; the live OpenEMR is the clinic node `openemr-zklo` (port 32777, open). Not new.
3. **Lab-intake pipeline (KNOWN DROP since 08-26)** — `provider_labs → Med42 → OpenEMR` cron is SILENT: email lane down (gws / Google OAuth unset), fax lane down (DOCUMO_KEY unset). Credentials not yet healed; documented per the anti-flood mandate, not re-alerting.

## Backup Status
- Latest completed: `nura-backup-20260828.tar.gz` — **91,704,592 bytes (87.5 MiB)**, timestamped 08-28 06:00 ✓.
- Daily 06:00 encrypted backup **enabled**, `last_status: ok`. Today's (08-29 06:00) not yet run at 02:02 UTC — verify after 06:00. Continuous daily artifacts present 08-22 → 08-28 (~91.5–91.7 MiB each).

## Security Status
- No expired/expiring creds or certs surfaced by this probe; no unauthorized-access signal; all 9 critical ports return expected services.
- **Apparent:** `api.nuratech.ai` presents an untrusted self-signed cert (see Failed Integrations) — an external trust/identity gap on a public front door. The engine's TCP:80-only probe conceals it.

## Clinical Safety Status
- OpenEMR (`openemr-zklo`) **Up (healthy)**; Mirth OIE (admin 8445) Up; Orthanc/DICOM Up; Hermes-gateway Up (healthy); RadIntel orchestrator (8090) Up; RIS-web (32790) Up.
- No delayed critical messages, no unreviewed AI output, no failed clinical interfaces beyond the known lab-intake drop above. No clinical writes made during this probe.

## Resource Utilization
- Memory: clinic 34%, lab 35%, edge 57% — all < 60%; local box 33%. No pressure.
- Disk: clinic 65%, lab 65%, edge 29%, local 65% — within bounds but trending; re-check if any cross 80%.
- No queue/GPU depth data captured by this engine.

## Scheduled Jobs
- 89 cron jobs present, all enabled. Inventory engine refresh completed 02:02 ✓ (this run); report generated on schedule.
- Daily 06:00 encrypted backup `last_status: ok`. No failures surfaced from the jobs registry. Weather/swap/lab watchdogs benign.

## Recommended Actions (top 3)
1. **Replace the api.nuratech.ai TLS cert.** Provision a valid cert for `api.nuratech.ai` (Let's Encrypt / real CA) on the lab Traefik/Swarm front-end and bind the domain SAN. External clients currently reject HTTPS (curl 60). Bounded, tooling-only, no clinical impact. Verify with `curl -v https://api.nuratech.ai` returning a trusted cert (HTTP 200/valid CA, not the TRAEFIK default).
2. **Re-wire the lab-intake lane.** Set gws/Google OAuth + DOCUMO_KEY to restore `provider_labs → Med42 → OpenEMR`; re-enable and verify a fresh lab ORU end-to-end. (Known drop since 08-26.)
3. **Disk hygiene + backup verification.** Run space-optimization on clinic 65% / lab 65% before they cross 80%; confirm today's 06:00 `nura-backup-20260829.tar.gz` completes with a checksum.

---
*Generated autonomously from live probe data. All counts cited from `~/nura-ops/inventory.json` (generated 2026-08-29T02:02:03Z) + live socket/curl probes. api.nuratech.ai TLS discrepancy confirmed via `openssl s_client` (TRAEFIK DEFAULT CERT).*
