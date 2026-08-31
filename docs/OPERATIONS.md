# NURA Operations Standard

## Objective

Production operations should make system state obvious: what is running, what is unhealthy, what changed, who/what changed it, and how to recover.

## Minimum service contract

Every production service should expose or document:

- service name and owner;
- version / commit SHA;
- health endpoint or deterministic health command;
- startup and restart procedure;
- dependencies;
- persistent volumes and databases;
- log location and retention;
- alert conditions;
- environment-variable names without values;
- backup policy where stateful;
- restore procedure;
- rollback procedure; and
- smoke-test procedure.

## Deployment verification

A production deployment is accepted only after:

- container/process is healthy;
- expected ports/routes respond;
- TLS is valid for public HTTPS endpoints;
- downstream dependencies respond;
- synthetic workflow succeeds;
- duplicate/idempotent behavior is tested when relevant;
- restart does not lose required state;
- logs contain no unexpected secrets or PHI;
- monitoring/alerting sees the service; and
- rollback path is known.

## Incident severity

- **SEV-0:** Patient safety, confirmed PHI exposure, destructive security compromise, or unrecoverable production data loss.
- **SEV-1:** Critical production service unavailable or major clinical/operational workflow blocked.
- **SEV-2:** Material degradation with workaround.
- **SEV-3:** Non-critical defect or operational improvement.

SEV-0 and SEV-1 events require immediate containment before optimization or feature work.

## Agent-operated jobs

Automated jobs should report at minimum:

`external_id`, `correlation_id`, `source`, `owner`, `status`, `progress`, `last_event`, `last_event_at`, `blocked_reason`, `completion_evidence`, and a durable link to the underlying work when available.

A job marked Done without completion evidence should be treated as administratively complete, not technically verified.
