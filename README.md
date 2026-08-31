# NURA

> AI-enabled healthcare software, clinical workflow orchestration, mobile applications, and edge operations.

NURA is a multi-component platform under active development. This repository currently contains the Flutter application, backend services, display-state service, edge-display documentation, CI configuration, and supporting technical proposals.

## Repository status

**Development stage:** Active engineering / pre-production

This repository should not be interpreted as a production clinical system merely because a component is present. Clinical, security, infrastructure, and deployment gates must be completed and verified independently before production use.

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
│   └── docs/edge-display/
├── Engineering automation
│   └── .github/workflows/
└── Product / research proposals
    └── ARTIFICIAL_MEDIC_PROPOSAL.md
```

## Core components

| Component | Location | Purpose |
| --- | --- | --- |
| Flutter client | `lib/` | Cross-platform application UI and client logic |
| App backend | `services/app_backend/` | Application backend service |
| Display-state service | `services/display_state/` | State delivery for edge / display clients |
| Edge display | `docs/edge-display/` | Hardware/display integration documentation |
| CI | `.github/workflows/` | Automated validation for repository changes |
| Artificial Medic proposal | `ARTIFICIAL_MEDIC_PROPOSAL.md` | Product/research proposal; not a production clinical specification |

## Engineering principles

NURA engineering follows several non-negotiable operating principles:

- Human authorization remains required for patient-impacting clinical decisions and writes.
- PHI must stay within explicitly approved systems and infrastructure.
- Secrets belong in environment variables or an approved secret manager, never source control.
- Automated jobs must be observable, idempotent where practical, and auditable.
- Every production service requires health checks, logs, restart verification, backup/recovery planning, and a rollback path.
- Clinical AI components must be evaluated before promotion from development or shadow operation.

## Getting started

### Flutter application

Prerequisites:

- Flutter 3.x
- Dart 3.x
- Platform tooling for the target environment

```bash
flutter pub get
flutter analyze
flutter test
flutter run
```

### Backend services

Each service is maintained within its own directory under `services/`. Check the service-specific files before running or deploying it; do not assume a common runtime or environment configuration across services.

## Documentation

Start with [`docs/README.md`](docs/README.md) for the documentation map.

Important repository documents:

- [`SECURITY.md`](SECURITY.md) — security and vulnerability reporting policy
- [`CONTRIBUTING.md`](CONTRIBUTING.md) — engineering workflow and contribution standards
- [`ARTIFICIAL_MEDIC_PROPOSAL.md`](ARTIFICIAL_MEDIC_PROPOSAL.md) — research/product proposal
- [`docs/edge-display/`](docs/edge-display/) — edge-display documentation

## Branch and pull-request discipline

Production-bound changes should be made through focused branches and pull requests. A change is not considered production-ready solely because it compiles or has been merged. Where applicable, completion requires:

1. automated tests passing;
2. security and secret review;
3. deployment configuration review;
4. synthetic smoke testing;
5. health/log verification;
6. restart and persistence verification; and
7. documented rollback.

## Clinical and regulatory notice

NURA includes healthcare-oriented concepts and software. Repository content, prototypes, AI output, demonstrations, and research materials are **not substitutes for licensed clinical judgment** and are not automatically cleared, approved, or validated for patient care. Production clinical use requires the applicable medical, privacy, security, quality, regulatory, and organizational approvals.

## Ownership

NURA is maintained by the repository owner and authorized project collaborators. See `CODEOWNERS` for the current repository review owner.
