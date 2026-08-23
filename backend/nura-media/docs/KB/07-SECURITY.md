# 07 — SECURITY & COMPLIANCE (the guardrails that make the boundary safe)

Chief-architect view: security is enforced at **boundaries**, not as a feature bolted on.

## Trust boundaries (where the controls live)
1. **Internet edge** — Cloudflare/WAF → NURA API/Gateway. Only 443; never expose PG/Redis/Orthanc-
   internal/Mirth-admin/Docker/Prometheus/Grafana. Admin via private network/VPN/Tailscale.
2. **Service-to-service** — API-key / mTLS; least-privilege per-service app keys. No master key.
3. **Model boundary** — the **Model Gateway** is the ONLY path to an LLM. `phi_policy` strips
   MRN/DOB/phone before any external call; tool denylist blocks destructive/authority tools.
4. **EHR boundary** — only the provider-approved final reaches OpenEMR (Mirth). Never auto-post.
5. **Human boundary** — item-level provider approval; voice/face/avatar cloning only for identities
   in `authorized_identity_registry`.

## Credential doctrine (SOP)
SEAL → PROBE → REGISTER → WIRE → DOC → REPORT. Secrets in env/secret-manager, **never** in git,
compose, code, README, Docker images. Single-purpose keys, least privilege, rotate. Example B2 keys:
orthanc-prod, documents-prod, ai-readonly, audit-writer(no-delete), dataset-ingest.

## Data policy
- **HIPAA:** Hostinger ≠ HIPAA → dev/synthetic only; BAA host + B2 BAA before production PHI.
- **No PHI in media prompts** by default; medical-edu uses synthetic/de-identified. External medical
  publish requires human clinical approval.
- Multi-tenant: every object has tenant_id; authorize user→tenant→patient→object (never by ID).
- Private buckets only; CORS never `*`; signed URLs, short TTL.

## Supply chain / hardening
Zero secrets in git · env-based secrets · pin versions (no `latest`/`-dev` tags) · non-root
containers where possible · dependency + container scanning · audit logging · rate limiting ·
incident response/access monitoring.

## Reference
`backend/nura-radiology-ai/EMR-RISK-GATES.md` · [S]agent-security-scanning · credential-bootstrap ·
openemr-security-hardening · military-grade-hardening.
