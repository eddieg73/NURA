# 08 — OPERATIONS & ENGINEERING STANDARDS (how it's run)

Architect view: a system is only production-grade if it is observable, recoverable, and safe to
change. These are the non-negotiable rails.

## Observability
Structured JSON logs. Every request carries `trace_id` / `job_id` / `tenant_id`. Minimum metrics:
jobs/hour, success/failure rate, GPU utilization, queue depth, render/generation duration, API
latency, cost/job + cost/provider + cost/model, storage usage. Instrument the gateway (telemetry.py,
audit.py), langfuse (already on Lab), sentry.

## Queue & failure handling
- Media queue: **Celery + Redis** dispatch, durable record in Postgres (`media_job`). Durable clinical
  events: **NATS JetStream** (Redis = transient only — never the record).
- Retry budget: local model 3, commercial API 1. After failure: retry → change params → change model
  → change provider → degrade gracefully → **human exception queue**. Never infinite retry, never
  silently discard. Every error visible.

## Deployment
- **Docker** everywhere; infrastructure reproducible from code (IaC). Pin versions / images (no
  `latest`). Non-root threads. Compose overrides for dev vs prod.
- **Git strategy:** `main` / `development` / `feature/*` / `hotfix/*`. Production changes = PR +
  automated tests + security checks + code review + deployment validation. **Hermes never bypasses
  protected production branches.** Land on feature branches (as done: `nura-platform-builds-2026-08-23`).

## Definition of Done
A feature is done only when: code builds · tests pass · service starts · health check passes ·
integration works · failure case tested · logs exist · metrics exist · security reviewed ·
documentation updated · rollback tested.

## Autonomy boundary (Hermes)
Decide autonomously: minor implementation details, routine versions, file locations, routine provider
fallback, basic retries, normal model selection.
Escalate when: architecture materially changes, security boundary changes, data-loss risk exists,
legal/license uncertainty, cost threshold exceeded, clinical approval required, production credentials
unavailable, destructive migration.

## Ops watchdogs (already live)
Incident commander (hourly audit), cron-status-board, docker-health-check, swap/disk watchdogs,
hermes-gateway-repair. [S]master-systems-audit · incident-commander · nura-daily-operations-report.
