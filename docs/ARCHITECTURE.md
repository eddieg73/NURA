# NURA Architecture

## Purpose

This document describes the repository-level architecture visible in source control. It does not assert that every planned NURA infrastructure component is deployed.

## Repository layers

### Client layer

The Flutter application is rooted in `lib/` with platform targets under `ios/`, `android/`, `macos/`, and `linux/`.

### Service layer

Current default-branch services are under `services/`:

- `app_backend/` — application backend.
- `display_state/` — state service used by display/edge integrations.

Additional services should follow the same rule: one bounded service directory, its own README, explicit dependencies, tests, health contract, and deployment notes.

### Edge layer

Edge-display implementation documentation is maintained under `docs/edge-display/`.

### Automation layer

GitHub Actions workflows are maintained under `.github/workflows/` and act as engineering gates. Passing CI is necessary but not sufficient for production readiness.

## Production architecture principles

1. **Explicit trust boundaries.** Public ingress, internal services, clinical systems, data stores, and administrative interfaces must be separately identifiable.
2. **Least privilege.** Service credentials should grant only the minimum capabilities required.
3. **No secrets in Git.** Store credentials in runtime environment configuration or an approved secret manager.
4. **PHI containment.** PHI may only traverse approved services and storage locations.
5. **Auditable automation.** Agent and workflow actions need stable IDs, timestamps, status, and evidence of completion.
6. **Human clinical authority.** AI may support workflows, but patient-impacting actions require the configured human authorization gate unless separately validated and legally authorized.
7. **Fail safely.** External dependency failure must not silently create unsafe clinical or operational state.
8. **Reversible releases.** Every production deployment needs a rollback mechanism.

## Completion definition

A service is not "complete" because its code exists. Production completion requires implementation, tests, security review, configuration, deployment, health verification, smoke testing, restart/persistence validation, observability, backup/recovery where applicable, and rollback evidence.
