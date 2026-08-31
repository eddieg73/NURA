# Security Policy

NURA includes healthcare-oriented software and should be treated as security-sensitive.

## Reporting a vulnerability

Do **not** publish credentials, PHI, exploit details, private infrastructure information, or patient data in a public GitHub issue.

Repository collaborators should report security findings privately to the repository owner or designated security lead and include:

- affected component;
- severity and impact;
- reproduction steps that do not expose PHI;
- affected version/commit;
- recommended containment; and
- remediation proposal when known.

## Secrets

Never commit:

- passwords;
- API keys;
- private keys;
- OAuth client secrets;
- database credentials;
- signing secrets;
- production `.env` files; or
- live PHI-bearing payloads.

Use placeholders in examples and an approved runtime secret-management mechanism for real values.

## PHI and sensitive data

Synthetic/de-identified test data should be the default in development and CI. PHI must not be copied into issues, pull requests, CI logs, fixtures, screenshots, or source files unless an explicitly approved compliant workflow requires it.

## Production security gate

Security-sensitive changes require review of authentication, authorization, least privilege, auditability, encryption in transit, secret handling, data retention, failure behavior, and rollback before production promotion.
