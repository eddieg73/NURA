# Deployment & Release Gates

## Before deployment

- [ ] Change has an identified owner.
- [ ] Scope and affected services are documented.
- [ ] CI passes.
- [ ] No credentials or PHI are committed.
- [ ] Required environment-variable names are documented.
- [ ] Database/schema migrations have a rollback or recovery plan.
- [ ] Public routes and trust boundaries are understood.
- [ ] Backup/snapshot is available before destructive or stateful changes.

## Deploy

Use the service-specific deployment procedure. Never infer production success from a successful Git push or image build.

## Smoke test

At minimum:

1. verify process/container health;
2. verify expected network route;
3. verify TLS where applicable;
4. execute a synthetic happy-path transaction;
5. test failure behavior for the highest-risk dependency;
6. verify logs/audit record;
7. restart the service and repeat the critical health check; and
8. verify persistent state survived restart where required.

## Webhook / event services

Additionally test:

- valid signed event;
- invalid signature rejection;
- expired/replayed event rejection;
- duplicate event idempotency;
- unknown source rejection;
- downstream outage behavior;
- retry behavior; and
- correlation between sender, receiver, and operational task record.

## Release evidence

Record:

- commit SHA;
- deployed version/image;
- deployment timestamp;
- operator;
- smoke-test result;
- relevant logs or monitoring link;
- known limitations; and
- rollback target.

Only then mark the release operationally verified.
