# PROVIDER CREDENTIALING & NUMBER ISSUANCE — PROCESS v1.0 (2026-08-02)

**Founder: "Create a process to issue a fax number and a mobile number and credentialing signup with an NPI number; if they don't have an NPI (lab professional, etc.) use another identifier — certificate number or work email or something of the sort."**

## The flow (one pipeline, three tiers)
```
SIGNUP (app) → IDENTITY SUBMISSION → AUTOMATED VERIFICATION → APPROVED
→ NUMBERS ISSUED (mobile + fax DIDs) → ROLE ASSIGNED → ONBOARDED
```

## Tier 1 — NPI HOLDERS (MD/DO · PA/NP · RN · paramedic/EMT · other NPI-eligible)
1. User submits: full legal name + NPI + state(s) of practice + role
2. **Automated verification: NPPES NPI Registry API (public, free — npiregistry.cms.hhs.gov)**
   - Match: NPI exists · name matches · taxonomy/role matches · status active
3. PASS → credential record created (verification snapshot + timestamp, audited)
4. **Numbers issued: provider MOBILE line (Twilio DID, Doximity-style verified caller ID on practice numbers) + provider FAX line (Documo/Twilio Fax DID)**
5. Role assigned per App-Role-Matrix (MD/DO sign-off · PA/NP provider review, etc.)

## Tier 2 — LICENSED NON-NPI (lab professionals · radiology techs · medical assistants · etc.)
1. User submits: name + **certificate/license number + issuing body** (e.g., ASCP cert, FL DOH license, state board) + work email
2. **Verification (priority order):**
   a. Public license lookup where available (FL MQA/state board portals — automation where API/exists, manual-reviewed where portal-only)
   b. **Verified work email** (OTP to org-domain email — e.g., @nuratech.ai, @clinic domain)
   c. Organization admin approval (org sponsor signs)
3. PASS → credential record + **mobile line issued (if role needs it — lab/tech roles get messaging lanes; fax per org need)**
4. Role assigned (lab director review / tech + radiologist review, etc.)

## Tier 3 — STAFF/ORG ROLES (front desk · admin · schedulers)
1. Verified work email (OTP) + org admin approval
2. Role assigned — **no clinical lanes, no provider numbers**

## Rules
1. **Verification is automated-first, human-approval for edge cases** — every approval is auditable (who, what, when, which source)
2. **One provider = one identity** (NPI or cert) — numbers follow the identity, revoked on departure
3. **Twilio/Documo provisioning is gated on the credential record** — no number issued without verified identity
4. **PHI-safe**: verification data sealed, audit-logged, never in app memory
5. **The provider directory (Doximity-style lookup) is built FROM these verified records** — searchable by name/specialty/org
6. Renewal: NPI/cert status re-verified on a cadence (watchdog lane)

## Integrations
App-Role-Matrix · SaaS connectivity directive (eee684d5) · Doximity+Weave directive (1ed5d4a9) · Twilio lanes · Documo lane · provider-verification-ops skill · OpenEMR/Perfex identity ties
