# NURA Documentation

This directory is the technical documentation entry point for the NURA repository.

## Start here

| Need | Document |
| --- | --- |
| Understand the repository | [`ARCHITECTURE.md`](ARCHITECTURE.md) |
| See what is actually complete | [`REPOSITORY_STATUS.md`](REPOSITORY_STATUS.md) |
| Deploy or promote a service | [`DEPLOYMENT.md`](DEPLOYMENT.md) |
| Operate or recover a service | [`OPERATIONS.md`](OPERATIONS.md) |
| Work on edge displays | [`edge-display/`](edge-display/) |
| Report a security issue | [`../SECURITY.md`](../SECURITY.md) |
| Contribute code | [`../CONTRIBUTING.md`](../CONTRIBUTING.md) |
| Review notable changes | [`../CHANGELOG.md`](../CHANGELOG.md) |

## Service documentation

- [`../services/app_backend/README.md`](../services/app_backend/README.md) — Flutter application backend.
- [`../services/display_state/README.md`](../services/display_state/README.md) — edge/browser display-state service.

## Source-of-truth rules

- Code behavior is defined by version-controlled implementation and tests.
- Production configuration containing secrets stays outside source control.
- Architecture documentation describes intended boundaries; deployed reality must be verified from the runtime environment.
- A merged change is not automatically a deployed change.
- An implemented clinical feature is not automatically clinically validated.
- Clinical or patient-impacting workflows require separate clinical governance and validation.

## Documentation standard

Every production-bound service should document:

1. purpose and owner;
2. dependencies;
3. local development procedure;
4. required environment variables without secret values;
5. health/readiness endpoints;
6. data stores and persistence;
7. network ingress/egress;
8. logging and monitoring;
9. backup and recovery;
10. deployment and rollback;
11. smoke tests; and
12. security/PHI classification.
