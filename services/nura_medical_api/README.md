# NURA Medical API

Production-oriented backend for `apps/nura_medical`.

## Intended use

This service supports authenticated clinician workflow, source-text capture, documentation drafts, clinical synthesis, differential-support drafts, review, tasks, export, and account deletion. It does **not** authorize autonomous diagnosis or treatment. Every clinical output is created as `draft`; only reviewer or administrator roles may approve or reject it.

## Implemented controls

- Organization-scoped identities, encounters, drafts, tasks, and audit records
- Clinician draft visibility limited to the creating clinician
- Organization review queue limited to reviewer and administrator roles
- Argon2 password hashing
- Short-lived JWT access tokens with organization and role revalidation
- Opaque, hashed, rotating, revocable refresh sessions
- Account-scoped export and in-app deletion API
- Consent/authority attestation before clinical text is accepted
- Structured output contract: source facts, interpretation, ordered possibilities, dangerous alternatives, red flags, missing data, next step, urgency, confidence, evidence date, provenance, and limitations
- Disabled safe mode when no approved inference provider is configured
- PostgreSQL production configuration and SQLite test/development support
- Request correlation IDs and append-only audit events without request-body logging
- Explicit external-AI PHI approval gates

## Local development

```bash
cd services/nura_medical_api
cp .env.production.example .env
# Change APP_ENV to development and DATABASE_URL to sqlite:///./nura_medical.db
python -m venv .venv
. .venv/bin/activate
pip install -r requirements.txt
uvicorn app.main:app --reload --port 8080
```

OpenAPI documentation:

```text
http://127.0.0.1:8080/docs
```

Tests:

```bash
PYTHONPATH=. python -m pytest -q
```

## Production deployment

1. Inventory the VPS, Docker networks, reverse proxy, ports, volumes, databases, backups, certificates, and secrets before deployment.
2. Copy `.env.production.example` to `.env.production` and replace every placeholder.
3. Keep `AI_PROVIDER=disabled` until the approved clinical inference route is validated.
4. Start the private stack:

```bash
docker compose --env-file .env.production up --build -d
curl http://127.0.0.1:8080/readyz
```

5. Publish the API only through an approved HTTPS reverse-proxy route.
6. Configure encrypted backups, restoration tests, monitoring, alerting, incident response, and rollback.

## Bootstrap access

Demo seeding is prohibited in production. Create the first administrator interactively inside the API container so the password is not passed on the command line:

```bash
docker compose exec api python scripts/bootstrap_user.py \
  --organization "NURATECH AI" \
  --email admin@nuratech.ai \
  --full-name "NURA Administrator" \
  --role admin
```

Use the same command with role `clinician` or `reviewer` to provision App Store review and clinical-review accounts.

## Inference providers

### Disabled safe mode

`AI_PROVIDER=disabled` preserves the end-to-end workflow while returning a structured abstention rather than generating diagnostic conclusions. This is the default.

### Hermes clinical engine

```dotenv
AI_PROVIDER=hermes
CLINICAL_ENGINE_URL=https://approved-internal-engine.example
CLINICAL_ENGINE_TOKEN=secret-reference
```

The upstream contract is `POST /v1/clinical/draft` and must satisfy the NURA clinical output contract.

### OpenAI adapter

The optional OpenAI adapter refuses startup unless all required configuration is present, including deployment approval flags. Those flags are not substitutes for a signed agreement, security review, minimum-necessary assessment, retention review, or clinical validation.

## Production gates requiring organizational action

- Approved production domain and TLS route
- Signed vendor/BAA review for every PHI processor
- Public privacy, terms, and support pages
- Clinical validation and accepted performance thresholds
- Role provisioning and identity lifecycle
- Managed database migrations before schema changes
- Central audit retention and security monitoring
- Incident, downtime, backup, restoration, and rollback procedures
- Final accountable clinical, privacy, security, legal, and executive approvers
