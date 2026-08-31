# Contributing to NURA

## Workflow

1. Start from the current default branch.
2. Create a focused branch: `feat/`, `fix/`, `docs/`, `chore/`, `security/`, or `hotfix/`.
3. Keep changes bounded to one coherent objective.
4. Add or update tests and documentation with the implementation.
5. Run applicable local validation.
6. Open a pull request with risk, validation, and rollback information.
7. Merge only after required checks and review are complete.

## Commit style

Prefer concise conventional prefixes:

- `feat:` new capability
- `fix:` defect correction
- `docs:` documentation
- `test:` test-only changes
- `refactor:` behavior-preserving restructuring
- `security:` security hardening
- `ci:` automation/CI
- `chore:` maintenance

## Definition of done

A code change is Done when its intended behavior is implemented, tested, documented where necessary, reviewed, and merged. A production change is not operationally Done until deployment and smoke-test evidence exist.

## Healthcare-specific rules

- Do not use real patient data in development fixtures or PRs.
- Do not bypass clinical approval gates merely to automate a workflow.
- Document PHI boundaries when introducing a new integration.
- Patient-impacting logic requires explicit clinical validation criteria.

## Pull request expectations

Every substantive PR should answer:

- What changed?
- Why?
- What is the risk?
- How was it tested?
- Does it touch PHI, authentication, authorization, clinical logic, billing, or persistent data?
- How is it rolled back?
