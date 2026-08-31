# NURA Medical API

Production-oriented backend for `apps/nura_medical`.

## Intended use

This service supports clinician workflow, source-text capture, draft documentation, clinical synthesis, task management, review, and audit. It does **not** authorize autonomous diagnosis or treatment. Every clinical output remains `draft` until a user with reviewer or administrator authority approves or rejects it.

## Implemented controls

- Organization-scoped users, encounters, drafts, tasks, and audit queries
- Argon2 password hashing
- Short-lived JWT access tokens
- Opaque, hashed, rotating, revocable refresh sessions
- Account export and in-app account deletion API
- Consent attestation before clinical text is accepted
- Structured clinical output contract with facts, interpretation, differential, dangerous alternatives, red flags, missing data, urgency, confidence, provenance, limitations, and evidence date
- Reviewer-only approval/rejection workflow
- No request-body logging
- Request correlation IDs and append-only audit events
- PostgreSQL production configuration and SQLite test/development support
- Explicit external-AI PHI approval gates
- Disabled safe mode when no approved inference provider is configured

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

API documentation:

```text
http://127.0.0.1:8080/docs
```

Run tests:

```bash
PYTHONPATH=. python -m pytest -q
```

## Production deployment

1. Inventory the existing VPS, Docker networks, reverse proxy, ports, volumes, backups, and secrets before deployment.
2. Copy `.env.production.example` to `.env.production` and replace every placeholder.
3. Keep `AI_PROVIDER=disabled` until the approved clinical inference route is validated.
4. Start the private stack:

```bash
docker compose -f docker-compose.production.yml --env-file .env.production up --build -d
curl http://127.0.0.1:8080/readyz
```

5. Publish only through an approved HTTPS reverse-proxy route such as `https://api.nuratech.ai`.
6. Configure encrypted backups, retention, restoration testing, monitoring, alerting, and rollback.

## Inference providers

### Disabled safe mode

`AI_PROVIDER=disabled` stores source facts and returns a structured message that inference is unavailable. This is the default.

### Hermes clinical engine

```dotenv
AI_PROVIDER=hermes
CLINICAL_ENGINE_URL=https://approved-internal-engine.example
CLINICAL_ENGINE_TOKEN=secret-reference
```

The upstream contract is `POST /v1/clinical/draft` and must return the NURA clinical output object.

### OpenAI Responses API

OpenAI routing is refused at startup unless all of the following are configured:

```dotenv
AI_PROVIDER=openai
OPENAI_API_KEY=secret-reference
OPENAI_BAA_CONFIRMED=true
OPENAI_PHI_APPROVED=true
```

Those flags are deployment approvals, not substitutes for a signed agreement, security review, minimum-necessary assessment, retention review, or clinical validation. The request sets `store: false`, but the accountable organization must still confirm its contractual and regulatory configuration.

## Production gates still requiring organizational action

- Approved production domain and TLS route
- Signed vendor/BAA review for every PHI processor
- Apple App Store privacy policy and support URLs published at the configured addresses
- Clinical safety case and validation dataset
- Role provisioning and identity lifecycle
- Database migration process before the first schema change
- Centralized audit retention and security monitoring
- Incident response, downtime, backup, and restoration procedures
- Final accountable clinical and security approvers
