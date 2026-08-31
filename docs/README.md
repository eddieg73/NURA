# NURA Documentation

This directory is the technical documentation entry point for the NURA repository.

## Documentation map

| Area | Location | Status |
| --- | --- | --- |
| Edge display | [`edge-display/`](edge-display/) | Active development |
| Repository architecture | [`ARCHITECTURE.md`](ARCHITECTURE.md) | Repository-level overview |
| Operations | [`OPERATIONS.md`](OPERATIONS.md) | Production readiness and runbook requirements |
| Deployment | [`DEPLOYMENT.md`](DEPLOYMENT.md) | Deployment gates and verification checklist |

## Source-of-truth rules

- Code behavior is defined by version-controlled implementation and tests.
- Production configuration must be maintained outside source control when it contains secrets.
- Architecture documentation describes intended boundaries; deployed reality must be verified from the runtime environment.
- Clinical or patient-impacting workflows require separate clinical governance and validation.

## Documentation standard

Every production-bound service should eventually document:

1. purpose and owner;
2. dependencies;
3. local development procedure;
4. required environment variables without secret values;
5. health endpoints;
6. data stores and persistence;
7. network ingress/egress;
8. logging and monitoring;
9. backup and recovery;
10. deployment and rollback;
11. smoke tests; and
12. security/PHI classification.
