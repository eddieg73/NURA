# NURA

> AI-enabled healthcare software, clinical workflow orchestration, mobile applications, and edge operations.

**Status:** Active engineering / pre-production. See **[Repository Status](docs/REPOSITORY_STATUS.md)** for the evidence-based readiness matrix.

NURA is a multi-component platform under active development. This repository contains a Flutter application, backend services, display-state/edge software, engineering automation, and supporting product/research material.

## Quick navigation

| Destination | Use it for |
| --- | --- |
| [Repository Status](docs/REPOSITORY_STATUS.md) | What is implemented, tested, deployed, and still gated |
| [Documentation Hub](docs/README.md) | Technical documentation entry point |
| [Architecture](docs/ARCHITECTURE.md) | Repository and service boundaries |
| [Deployment](docs/DEPLOYMENT.md) | Promotion and smoke-test gates |
| [Operations](docs/OPERATIONS.md) | Runtime, recovery, monitoring and rollback standards |
| [Security](SECURITY.md) | Vulnerability, secret and PHI handling |
| [Contributing](CONTRIBUTING.md) | Engineering workflow |
| [Changelog](CHANGELOG.md) | Notable repository changes |
| [Support](SUPPORT.md) | Escalation and incident routing |

## Architecture at a glance

```text
NURA
├── Flutter application
│   ├── lib/
│   ├── ios/
│   ├── android/
│   ├── macos/
│   └── linux/
├── Backend services
│   ├── services/app_backend/
│   └── services/display_state/
├── Documentation
│   └── docs/
├── Engineering automation
│   └── .github/
└── Product / research proposals
    └── ARTIFICIAL_MEDIC_PROPOSAL.md
```

## Core components

| Component | Location | Purpose | Readme/status |
| --- | --- | --- | --- |
| Flutter client | `lib/` | Cross-platform application UI and client logic | Repository status |
| App backend | `services/app_backend/` | Application backend service | [Service README](services/app_backend/README.md) |
| Display-state service | `services/display_state/` | State delivery for edge/display clients | [Service README](services/display_state/README.md) |
| Edge display | `docs/edge-display/` | Hardware/display integration | [Documentation](docs/edge-display/) |
| CI and automation | `.github/` | Automated validation and repository governance | [Contributing](CONTRIBUTING.md) |
| Artificial Medic proposal | `ARTIFICIAL_MEDIC_PROPOSAL.md` | Product/research proposal | Not a production clinical specification |

## Engineering principles

- Human authorization remains required for patient-impacting clinical decisions and writes.
- PHI stays within explicitly approved systems and infrastructure.
- Secrets belong in environment variables or an approved secret manager, never source control.
- Automated jobs must be observable, idempotent where practical, and auditable.
- Every production service requires health/readiness checks, logs, restart verification, backup/recovery planning, and rollback.
- Clinical AI components require evaluation and governance before promotion from development or shadow operation.
- **Implemented**, **CI verified**, **deployed**, and **production verified** are separate states.

## Getting started

### Flutter application

Prerequisites: Flutter 3.x, Dart 3.x, and platform tooling for the target environment.

```bash
flutter pub get
flutter analyze
flutter test
flutter run
```

### Backend services

Each deployable service lives under `services/` and owns its runtime documentation. Read the service README before running or deploying it; do not assume services share configuration or data boundaries.

## Definition of production completion

A change is not production-ready merely because it compiles, passes a unit test, or has been merged. Where applicable, completion requires:

1. automated validation passing;
2. security and secret review;
3. deployment configuration review;
4. immutable/versioned deployment artifact;
5. synthetic smoke test;
6. health/readiness and log verification;
7. persistence/restart verification;
8. monitoring and alerting;
9. backup/recovery verification; and
10. documented rollback.

## Clinical and regulatory notice

NURA includes healthcare-oriented concepts and software. Repository content, prototypes, AI output, demonstrations, and research materials are **not substitutes for licensed clinical judgment** and are not automatically cleared, approved, or validated for patient care. Production clinical use requires applicable medical, privacy, security, quality, regulatory, and organizational approvals.

## Ownership

NURA is maintained by the repository owner and authorized collaborators. `CODEOWNERS` defines the current repository review owner.
