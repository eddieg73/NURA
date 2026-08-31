# Repository Status

Last reviewed: 2026-08-31

This page separates code presence from verified operational readiness.

| Area | Implemented in repository | Automated validation | Production deployed | Runtime smoke tested | Notes |
| --- | --- | --- | --- | --- | --- |
| Flutter client | Yes | App CI | Not verified | Not verified | Cross-platform client under active development |
| App backend | Yes | Pytest in App CI | Not verified | Not verified | FastAPI backend; production gates remain |
| Display-state service | Yes | Service test present; CI coverage being normalized | Not verified | Not verified | Edge/browser state API |
| Edge display | Yes | Partial | Not verified | Not verified | Browser + ESP32 integration assets |
| Hermes event bridge | Feature branch / PR | Dedicated CI added on feature branch | No verified deployment | No verified production smoke test | Do not advertise as live until merge + VPS verification |
| Clinical AI / Artificial Medic | Proposal/research material | Not a production clinical validation suite | No verified production clinical deployment | No | Requires clinical, safety, regulatory and quality gates |

## Definition of complete

A component may be called **implemented** when its source, configuration examples and tests exist. It may be called **production ready** only after all applicable CI, security, deployment, persistence, monitoring, backup and rollback gates pass. It may be called **production verified** only after evidence from the actual target runtime is captured.

## Current repository priorities

1. Merge the repository-professionalization changes after CI/review.
2. Resolve the Hermes event bridge branch against the current default branch and pass its dedicated CI.
3. Add/normalize CI for each deployable service.
4. Establish protected-branch/ruleset requirements for required checks and review.
5. Complete Hostinger runtime inventory before deployment changes.
6. Record smoke-test and rollback evidence for each production service.

## Naming note

The current default branch name is legacy-generated and should eventually be replaced with a conventional `main` branch in a separately planned repository-administration change. Do not rename it casually while deployment references or external automation may depend on it.
