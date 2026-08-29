# PERFORMANCE_AUDIT.md — NURA/HERMES STACK (2026-08-05, Principal Architect review)

**Scope: the hermes-agent codebase (the core!) + the deployed fleet (Clinic/Lab/Edge) + the databases/caches/queues/deployment configs. Measurements taken live 2026-08-05. No changes made — audit only.**

## 1. THE CODEBASE (hermes-agent, measured)
| Finding | Evidence | Impact |
|---|---|---|
| **F1 — The god-files**: gateway/run.py = 25,766 LOC · cli.py = 17,976 · web_server.py = 17,333 · run_agent.py = 7,410 · api_server.py = 6,955 (58K LOC in 5 files!) | wc -l (measured) | HIGH — import-time, cache-miss amplification, the maintenance tax, the interpreter's per-module compile + the memory footprint of the module objects; every edit risks the regression |
| **F2 — The tool-schema payload**: every model tool ships on EVERY API call (the repo's own AGENTS.md: "the bar for a new core tool is high") | the core design invariant | HIGH — the token/cost per call grows linearly with the tool count; the 40+ MCP lanes = the fat payloads to every provider |
| **F3 — The skill-loading**: the 455+ skills = indexed at the session start | the skills index | MEDIUM — the cold-session start latency + the memory |
| **F4 — The dependency surface**: pyproject = 421 lines (the deps + the dev-deps) | measured | LOW — the install size + the attack surface |

## 2. THE FLEET (live metrics, 08-05)
| Finding | Evidence | Impact |
|---|---|---|
| **F5 — The gateway memory**: hermes-gateway = 2.49 GiB resident (the API server + the sessions + the caches in one container) | docker stats (measured) | HIGH — the 16GB Clinic's single largest consumer; the swap-pressure contributor |
| **F6 — The un-bounded siblings**: postiz = 312 MiB + temporal = 198 MiB + the agentmemory/bar-assistant/etc. — NO memory limits in the composes | docker stats + the compose inspection | MEDIUM — the "noisy neighbor" risk; the swap-full incidents (the 08-04 saga!) |
| **F7 — Redis**: dbsize + memory = the auth-gated (the auth ✓) — the maxmemory/eviction policy = UNVERIFIED | redis-cli info (auth-gated) | MEDIUM — an unbounded Redis = the OOM risk |
| **F8 — The network-saga residue**: the api/ris/pacs public doors = 000 (the cloud-firewall), the internal 502 (the bind) — the diagnostic loops burned hours | the 08-04/05 logs | LOW (the resolved) — the lesson: the layered-debugging cost |
| **F9 — The langfuse crash-loop** (the Lab): the "Restarting (1)" — the retry-loop burns CPU | the audit (earlier) | MEDIUM — the failed-worker retry without the backoff |
| **F10 — The swap**: the Clinic's swap = the full at the audit (4G/4G) | the CTO audit | HIGH — the memory-pressure = the container-restart risk (the kaqe event!) |

## 3. THE DATABASES
| Finding | Evidence | Impact |
|---|---|---|
| **F11 — The MariaDB/OpenEMR**: no slow-query log, no index review performed | the config audit | MEDIUM — the unknown query profile |
| **F12 — The Qdrant**: the nura-os collection = the live retrieval — no collection sizing/replication check | the API audit | LOW-MEDIUM |
| **F13 — The Postgres (Chatwoot/Postiz/Mattermost)**: no connection-pool tuning, no statement-timeouts | the compose audit | MEDIUM — the idle-connection bloat + the runaway-query risk |

## 4. THE QUEUES & THE JOBS
| Finding | Evidence | Impact |
|---|---|---|
| **F14 — Temporal (Postiz)**: 4 containers (the ES + the UI + the admin + the server!) for a social scheduler | the container list | MEDIUM — the over-provisioned queue stack |
| **F15 — The crons**: the 5-min health watchdog + the daily ops + the SENTINEL — no timeouts documented on the long jobs | the cron registry | LOW-MEDIUM |

## 5. THE FRONTEND & THE ASSETS
| Finding | Evidence | Impact |
|---|---|---|
| **F16 — The Hermes dashboard/desktop**: the Electron bundle + the web dashboard — no bundle-splitting/lazy-load audit | the repo surface | LOW-MED (the desktop is the founder's surface!) |
| **F17 — The DocsGPT frontend**: the Vite-bundle at :5173 (the dev-mode — the un-optimized) | the deploy | LOW (the dev-mode only) |

## 6. THE DEPLOYMENT CONFIG
| Finding | Evidence | Impact |
|---|---|---|
| **F18 — NO memory/cpu limits** in the fleet composes (the 40+ projects!) | the compose inspection | HIGH — the noisy-neighbor + the swap + the OOM-kill exposure |
| **F19 — The subnet-pool exhaustion**: the 172.17-28/16 all consumed (the "fully subnetted" errors!) | the docker network audit | MEDIUM — the new-project network failures (the DocsGPT-saga!) |
| **F20 — The single-node concentration**: the Clinic carries the gateway + the EMR + the PACS + the CRM + the queues (16GB) | the fleet map | MEDIUM — the blast-radius; the Lab (32GB) under-utilized (10% disk, 19% mem) |

## THE PRIORITY MATRIX (ROI)
- **HIGH IMPACT / LOW RISK**: F18 (the compose memory limits — the caps on postiz/temporal/gateway!) · F10 (the swap consumer-hunt + the limits) · F9 (the langfuse backoff-fix) · F7 (the Redis maxmemory + the eviction policy) · F19 (the daemon.json pool expansion — the founder-gated restart)
- **HIGH IMPACT / MEDIUM RISK**: F1 (the god-file extractions — the run.py/cli.py modularization — the repo's own AGENTS.md blesses this!) · F2 (the tool-schema gating — the check_fn/service-gated tools!) · F5 (the gateway memory-profile — the cache-size caps + the session-pruning) · F20 (the load-rebalance: the analytics/queues → the Lab!)
- **EVERYTHING ELSE**: F11-13 (the db-index/slow-query passes) · F14 (the temporal-consolidation) · F16-17 (the frontend-bundles) · F3-F4 (the skill-index + the deps)
