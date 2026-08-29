# PERFORMANCE_PLAN.md — NURA/HERMES OPTIMIZATION EXECUTION PLAN (2026-08-05)

**Standing by for approval. No changes made. The order: highest-ROI first, each change measured before the next.**

## PHASE 1 — HIGH IMPACT / LOW RISK (the immediate wins)
| # | Change | Expected gain | Risk |
|---|---|---|---|
| P1 | The compose memory-limits (the caps: hermes-gateway 3G · postiz 512M · temporal 512M · the rest 256-512M) | the swap-pressure down · the OOM-kills eliminated · the predictable fleet | LOW (config-only, the founder-approval for the gateway-recreate) |
| P2 | The Redis maxmemory + the allkeys-lru eviction (the Clinic's redis-gc8b) | the unbounded-growth risk gone | LOW |
| P3 | The langfuse restart-backoff (the compose restart-policy → on-failure + the max-retries) | the crash-loop CPU burn stops | LOW |
| P4 | The daemon.json default-address-pools (10.99.0.0/16 → 256 subnets) | the subnet-exhaustion gone (the DocsGPT-class failures end!) | MED (the docker-daemon restart = the founder-gated, the ~60s blip) |
| P5 | The swap consumer-hunt (the 4G-full: the gateway's 2.5GB + the postiz/temporal = the suspects) → the caps apply | the kaqe-class container-restarts stop | LOW |

## PHASE 2 — HIGH IMPACT / MEDIUM RISK (the code-level)
| # | Change | Expected gain | Risk |
|---|---|---|---|
| P6 | The god-file extraction #1: gateway/run.py (25.7K LOC) → the focused modules (the platform-registry, the channel-adapters, the session-manager) — the repo's OWN AGENTS.md blesses this class of work | the import-time ↓ · the maintenance tax ↓ · the regression-surface ↓ | MED (the big-mechanical diffs — the tests must pass) |
| P7 | The god-file extraction #2: cli.py (18K) → the command-groups | the CLI startup-latency ↓ | MED |
| P8 | The tool-schema gating (the service-gated check_fn for the heavy lanes — the 40+ MCP tools off the default payload) | the per-call tokens ↓ (the cost!) · the latency ↓ | MED (the prompt-caching invariant preserved — the gating at the schema-build, not the mid-conversation) |
| P9 | The gateway memory-profile: the cache-size caps + the session-pruning (the old-session eviction) | the 2.5GB → ~1.5GB target | MED |
| P10 | The load-rebalance: the analytics + the queues (postiz/temporal/langfuse) → the LAB (32GB, 19% used!) | the Clinic's pressure ↓ · the Lab earns its keep | MED (the DNS/routing updates) |

## PHASE 3 — EVERYTHING ELSE (the backlog)
- The db passes: the slow-query logs + the composite indexes (OpenEMR/MariaDB · the Chatwoot/Postgres!) · the Qdrant collection-sizing · the statement-timeouts
- The Temporal-consolidation (the 4-container stack → the leaner profile)
- The frontend: the dashboard/desktop bundle-splitting + the lazy-loads
- The skill-index warm-start · the dependency-surface trim
- The HTTP-caching headers on the static lanes

## THE MEASUREMENT RITUAL (every phase)
- Before/after: the docker-stats (the mem/cpu!) · the swap-levels · the gateway-latency (the /health p95!) · the Redis-memory · the API-response-times
- The gates: the tests-pass (the repo's pytest!) · the functionality-preserved · the re-measure → the next item
- The evidence = the probe-output in every report (the no-claims-without-measurement!)

## THE APPROVAL GATES
- P1/P4/P10 = the founder's explicit go (the gateway-recreate + the daemon-restart + the load-moves)
- P6-P9 = the founder's go + the staged-deploy (the staging-verify → the production)
- The clinical-data = untouched (the OpenEMR API-only doctrine holds throughout)
