# Security & Clinical Safety Policy

## Do not commit

- PHI or patient-identifiable data
- API keys, passwords, tokens, private keys, certificates, connection strings, or `.env` files
- production database dumps
- payer/member rosters
- signed legal documents containing sensitive data

Use the approved secret manager and environment-specific deployment configuration.

## Reportable issues

Treat the following as security/safety defects:

- authentication or authorization bypass
- cross-tenant data exposure
- PHI leakage
- secret exposure
- unsafe autonomous EHR write-back
- uncontrolled clinical ordering/prescribing
- unsupported coding/billing submission
- audit-log tampering or missing provenance
- prompt/tool injection that can cross an approval boundary

## Clinical safety

Clinical AI output is decision support unless a specifically approved protocol defines otherwise. Systems must preserve source provenance, uncertainty, human review/override, and an auditable path from input to recommendation to action.

## Production controls

Production deployments should use least privilege, RBAC, tenant isolation, encryption in transit/at rest, append-only or tamper-evident audit trails where appropriate, environment separation, monitored integration failures, and tested rollback procedures.
