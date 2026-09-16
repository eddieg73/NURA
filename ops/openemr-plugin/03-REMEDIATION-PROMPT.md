# NURA CTO REMEDIATION PROMPT — OpenEMR ⇄ ChatGPT MCP Lane + Fleet Defects

**Issued:** 2026-09-13 · **Authority:** CTO (Hermes) · **Audience:** executing engineer or agent
**Scope:** every open defect found in the 2026-09-13 OpenEMR/ChatGPT lane review, plus the adjacent
fleet faults that block it. Ordered by **dependency**, not by severity — later phases cannot be
verified before earlier ones.

---

## 0. OPERATING RULES — READ BEFORE TOUCHING ANYTHING

1. **Verify before declaring.** A 2xx is not a state change. Re-read the object after every write.
   Paste real command output as evidence. Untested work is labelled **untested**.
2. **Neither invent authority nor assume it.** Phases marked **[AUTH]** change a **live clinical
   system** or a public boundary. Do not execute them without explicit founder authorization.
3. **Never expose the `passthrough` verifier publicly.** It accepts **any** bearer token. Any public
   route must terminate at `AUTH_MODE=jwt`.
4. **No PHI until the BAA exists.** Until then every test uses synthetic or local data.
5. **Every phase ends with a ROLLBACK line that has been tested**, not merely written.
6. **Do not print credentials, tokens, client secrets, or PHI into any log, chat, or commit.**
   Report fingerprints/MATCH-MISMATCH, never values.
7. **Add vhosts to `radris-stack-nginx-1`, never to host nginx.** Host nginx is `inactive`; its
   `sites-enabled/*` are inert. (See skill `tls-ownership-drift-prevention`.)

**Authoritative references** (verify against the deployed version, do not trust this doc alone):
- OpenEMR API enablement + OAuth2 + client registration:
  `github.com/openemr/openemr/blob/master/Documentation/api/AUTHENTICATION.md`
- OpenEMR SMART app registration + launch flows:
  `github.com/openemr/openemr/blob/master/Documentation/api/SMART_ON_FHIR.md`
- OpenEMR standard API: `Documentation/api/STANDARD_API.md`
- OpenEMR CLI API-enablement flags (**PR #11830**, `./cli install` — replaces manual SQL toggling)
- MCP authorization spec: `modelcontextprotocol.io/specification/2025-06-18/basic/authorization`
- OpenAI remote MCP server guide: `developers.openai.com/api/docs/mcp`
- OpenAI developer mode / MCP apps: `help.openai.com/en/articles/12584461`
- Our plugin source + review: `/opt/data/NURA/ops/openemr-plugin/`

---

## PHASE 1 — TLS / CERTIFICATE RENEWAL  ✅ RESOLVED 2026-09-14 (prediction was WRONG)

**⚠️ CORRECTION — READ THIS BEFORE ACTING.** This phase originally predicted, from static config
inspection, that renewal **could not succeed** (`authenticator = nginx` while host nginx is
`inactive`). **That prediction was falsified by evidence.** Verified 2026-09-14 16:08 UTC:

```
mcp.nuratech.ai   notBefore = Sep 14 06:12:10 2026   notAfter = Dec 13 06:12:09 2026
ssl_verify_result = 0 (VALID)   https://mcp.nuratech.ai/healthz -> HTTP 200
openssl x509 -checkend 0 -> "Certificate will not expire"
```

**It renewed cleanly at 06:12 UTC on 2026-09-14**, ~3.5 h before the old cert expired. So
`certbot` **is** working here — whatever mechanism it uses (timer run, a deploy hook syncing into
the container, or a temporarily-started nginx) **succeeds**. The lesson is recorded rather than
deleted: **a config-inspection forecast is not evidence; probe the artefact.** Static reasoning
about a containerised ingress produced a confident, wrong conclusion.

**What remains genuinely open (still true, still worth fixing):**

- `pacs.nuratech.ai`, `ris.nuratech.ai`, `viewer.nuratech.ai` **all serve ONE shared self-signed
  certificate** (`CN=pacs.nuratech.ai`, issued 2026-08-15, self-issued, valid to 2027-08-15). None
  of the three hostnames is trusted by a browser — `curl` without `-k` returns **000**. This is
  pre-existing and unrelated to the MCP work, but it means the clinical RIS/PACS endpoints are
  effectively TLS-broken for users.
- **Determine WHY mcp renewed but the others did not.** Before changing any renewal method, find
  out what mechanism actually renewed `mcp.nuratech.ai` on 09-14 (check `certbot` logs,
  `/etc/letsencrypt/renewal/*.conf`, any deploy hook, and the systemd timer). **Do not "fix" a
  working renewal path** — the original instruction to switch to DNS-01/webroot was based on the
  now-falsified premise.

**Revised tasks.**
1. Establish the real renewal mechanism for `mcp.nuratech.ai` (logs + hooks + timer) and document it.
2. Confirm the **same** mechanism covers `pacs`/`ris`/`viewer`; if it does not, that is the actual
   defect — fix only those.
3. Issue **per-host** certificates so one hostname's cert is never served for another.
4. Re-probe served certs after any change.

**Verify.** For each host: served `subject` matches the hostname, `issuer` is a real CA, and `curl`
**without `-k`** returns non-000.
**Rollback.** Keep prior cert files; restore and `nginx -s reload`.
**Exit criteria.** Every clinical hostname serves a valid, hostname-matching cert; **the working
renewal path is NOT disturbed.**

---

## PHASE 2 — OPENEMR API + OAUTH2 ENABLEMENT  **[AUTH]**

**Defect.** `globals` shows `rest_api=0`, `rest_fhir_api=0`, `rest_portal_api=0`,
`rest_system_scopes_api=0`; `oauth_clients` is **empty**. Live behaviour:
`/apis/default/fhir/metadata` → 200 (public), `/apis/...` → 401, but
`/oauth2/default/{token,authorize,jwk}` → **404 "OpenEMR Error: API is disabled"**.
**No token can be issued, so the plugin's `AUTH_MODE=jwt` has no JWKS to validate against.**

**Tasks.** *(Founder authorization required — this widens a live EHR's attack surface.)*
1. **Administration → Config → Connectors**: enable **Standard REST API** and **Standard FHIR REST
   API**. Per OpenEMR docs both are required (`/api/` and `/fhir/`). Consider the CLI route from
   **PR #11830** to avoid hand-inserting SQL into `globals`.
2. **Administration → Config → Connectors → Site Address** — **required for OAuth2 and FHIR**.
   Must be the public HTTPS URL, not `127.0.0.1:32777`.
3. **SSL/TLS is mandatory** for OAuth2 — do not attempt the flow over plain HTTP.
4. **OAuth2 → App Manual Approval**: set deliberately. Note the trade-off: automatic approval
   auto-approves `patient/*`-only apps (ONC Cures 48-hour rule); **apps requesting `user/*` or
   `system/*` require manual approval**. Our connector is clinician-facing and will request `user/*`
   → **manual approval is the correct setting**.
5. **Register the client** — either web (`/interface/smart/register-app.php`) or API:
   `POST /oauth2/default/registration` with `application_type: private`,
   `token_endpoint_auth_method: private_key_jwt` + `jwks_uri` (preferred; RS384, RSA ≥2048) or
   `client_secret_basic`. Request **read/search only**:
   `openid fhirUser offline_access api:fhir` + `user/{Patient,Condition,AllergyIntolerance,
   MedicationRequest,MedicationDispense,Observation,Encounter,DiagnosticReport,Procedure,
   DocumentReference}.rs`  (`.rs` = read+search; **no `.c`/`.u`/`.d`**).
6. **Enable the app**: *Administration → System → API Clients* → **Enable**. An unapproved app
   authenticates but is denied — this is the usual cause of a silent failure.
7. Store the `client_secret` in the sealed secrets store (0600). It **cannot be retrieved later**.

**Verify.** `/oauth2/default/.well-known/...` resolves; a real `authorization_code` + PKCE `S256`
flow returns a token; `introspect` reports it active; a token scoped `user/Patient.rs` retrieves one
synthetic patient from `/apis/default/fhir/Patient/<id>` and is **rejected** for a resource it was
not granted.
**Rollback.** Re-set the four `globals` to `0`, disable/delete the client, `docker restart` OpenEMR.
**Exit criteria.** A live token can read a synthetic patient and cannot exceed its scopes.

**Open question to resolve in this phase.** OpenEMR's own docs show the token response as a JWT
(`"access_token": "eyJ0eX...RkRp..."`), and it publishes an introspection endpoint. **Determine
empirically which is authoritative** (JWT with JWKS, or opaque with introspection). If tokens are
**opaque**, the plugin's `jwt` mode cannot validate them and **no introspection verifier ships** —
that becomes a Phase 4 code change, not a config change.

---

## PHASE 3 — MCP SPECIFICATION COMPLIANCE

**MCP spec requirements** (`2025-06-18`, authorization) and our status:

| Requirement | Spec | Ours | Action |
|---|---|---|---|
| Protected Resource Metadata (RFC 9728) | **MUST** | ✅ `/.well-known/oauth-protected-resource` | none |
| `authorization_servers` in that document | **MUST** | ⚠️ present but **`http://127.0.0.1:32777/...`** | **fix — must be the public AS** |
| `WWW-Authenticate` on 401 (RFC 9728 §5.1) | **MUST** | ✅ verified compliant | none |
| AS Metadata (RFC 8414) at `/.well-known/oauth-authorization-server` | **MUST** | ❌ **404** | **see below** |
| `resource` parameter (RFC 8707) in auth + token requests | **MUST** | ❓ unverified | **verify — likely gap** |
| Dynamic Client Registration (RFC 7591) | SHOULD | ✅ `/oauth2/default/registration` | none |

**The two real gaps:**

1. **RFC 8414 AS metadata is 404 on OpenEMR.** MCP clients *must* use OAuth 2.0 Authorization Server
   Metadata. OpenEMR serves the **SMART** document (`.well-known/smart-configuration`), which is a
   different artefact at a different path.
   **First verify whether the 404 is simply because `rest_api=0`** — re-probe
   `/.well-known/oauth-authorization-server` and `/oauth2/default/.well-known/oauth-authorization-server`
   **after Phase 2**. If it is still 404, add a **thin reverse-proxy shim** that serves RFC 8414
   metadata derived from OpenEMR's `smart-configuration` (`issuer`, `authorization_endpoint`,
   `token_endpoint`, `jwks_uri`, `introspection_endpoint`, `registration_endpoint`,
   `code_challenge_methods_supported: [S256]`, `scopes_supported`). **Do not fabricate endpoints** —
   every value must come from the live discovery document.

2. **RFC 8707 `resource` parameter.** MCP requires `resource` on both the authorization and token
   requests. OpenEMR's documented FHIR flow uses **`aud`** (SMART-style), not `resource`.
   **Test empirically.** If OpenEMR ignores `resource`, the token's audience will not be bound to
   `https://mcp.nuratech.ai` — a real security control is lost. Preferred resolution: make the shim
   the AS-facing surface and translate `resource` ⇄ `aud` explicitly, and **document the translation**
   so it is auditable. If translation is unsafe, escalate — do not silently drop the parameter.

**Verify.** A tool-assisted MCP client completes discovery → registration → authorization → token →
authenticated `tools/list` **using only public URLs**, and the issued token's audience is bound to
the MCP resource.
**Exit criteria.** No internal address (`127.0.0.1`, `172.17.0.1`, `host.docker.internal`) appears in
any discovery document.

---

## PHASE 4 — PLUGIN DEFECTS (code changes to `@nura/openemr-mcp`)

1. **Unreachable JWKS returns `500`, should be `401`/`503`.** Currently a dead JWKS yields
   `{"error":"server_error"}`. The request is correctly *denied*, but a **500 storm reads as an
   outage**, not as "auth not configured" — it corrupts monitoring. Return `401` (invalid token) or
   `503` (authorization server unavailable) and keep the failure distinguishable.
2. **`authorization_servers` must be the public AS URL** (Phase 3.1).
3. **`.env` is not loaded.** The README says *"Copy `.env.example` to `.env`"* but there is no dotenv
   import, `loadConfig()` reads `process.env`, and the Dockerfile passes no `--env-file`. Following
   the README literally produces `OPENEMR_FHIR_BASE_URL is required`. **Fix the docs** (state that
   config comes from the process environment) **or** add explicit `--env-file` support. Do not leave
   the two contradicting each other.
4. **`/healthz` discloses the service version unauthenticated and is stale** — it reports `0.2.0`
   while `package.json` says `0.2.1`. Read the version from `package.json`; consider trimming it from
   the public response.
5. **No rate limiting** at the MCP boundary. Add before public production traffic.
6. **Re-run the full gate** after any change: `tsc` (strict) + `node --test` (**currently 23/23**) +
   the live probes. Add regression tests for each fix.

**Exit criteria.** Build clean, all tests pass, `500`-on-JWKS-failure eliminated, discovery
documents carry only public URLs.

---

## PHASE 5 — CHATGPT CONNECTOR REGISTRATION  **[AUTH]**

Per OpenAI's remote-MCP guide and the developer-mode article:

1. Confirm the workspace is an **eligible organisational ChatGPT for Healthcare / regulated
   Enterprise** workspace. Per our own review: the Epic/EHR integration path is **not** available to
   individual *ChatGPT for Clinicians* accounts. **Founder confirms org/Enterprise access.**
2. **NPI + licence verification** completed for the accountable clinician(s).
3. **BAA executed** — and every required third-party agreement. **No PHI before this.**
4. Register the connector in developer mode against `https://mcp.nuratech.ai/mcp`; complete the
   OAuth flow end to end.
5. If the connector is to serve **deep research / company knowledge**, the OpenAI guide specifies
   **two read-only tools — `search` and `fetch`** — with `structuredContent` plus a matching
   JSON-encoded `content` entry, and a **non-empty `url`** per result for citation. Our tool surface
   is clinical-resource oriented, so **decide explicitly** whether this connector is a
   *tool* connector or a *knowledge* connector; do not half-implement the `search`/`fetch` shape.
6. Chat with it against **synthetic** data first. Log the full request/response pair.

**Exit criteria.** End-to-end conversation over synthetic data; audit events present with
correlation IDs; **zero PHI**.

---

## PHASE 6 — ACCESS POLICY ENFORCEMENT (founder policy, 2026-09-13)

**Policy.** *"Verified healthcare professional accounts only initially. We can then do it for
paramedics and nurses with license number."*

**Implement as code, not copy.**
1. **Enrollment gated on credential verification.** The authorization server must attest a
   **verified clinician identity** — `fhirUser` bound to a real professional record — not merely
   "authenticated". A token saying only "logged in" must be insufficient.
2. **Phase 2 (paramedics/nurses)** requires an explicit **licence-number verification step** before
   provisioning, with **role-appropriate scopes**. Do not issue a nurse the same scope set as an
   attending physician without a documented clinical decision.
3. **Read/search only in every phase.** No create/update/delete scopes; the connector ships no
   write tool, and none may be added for these cohorts.
4. **Audit attribution.** The verified professional identity is what makes a retrieval attributable.
   `audit.ts` currently logs `correlationId`/tool/outcome/count with no PHI — **keep it that way**,
   and ensure the acting identity is recorded alongside it.
5. **Deny by default** when verification state is unknown.

**Exit criteria.** A synthetic unverified account is **refused**; a verified clinician succeeds; a
token lacking `fhirUser` is refused; each is demonstrated with raw output.

---

## PHASE 7 — PERFEX LANE REVIEW

**Context.** Perfex has **no built-in REST API**; `pay.nuratech.ai` runs a third-party module.
References: `perfexapi.com/docs`, `perfexcrm.themesic.com/apiguide/`,
`github.com/themesic/perfex-rest-api-examples`, and Themesic's write-up on exposing Perfex through
**OpenAPI + MCP for AI agents** (`themesic.com/blog/automating-perfex-crm-with-a-rest-api-webhooks-openapi-and-mcp-for-ai/`).

**Tasks.**
1. Identify which module is deployed and its version (**owned vs vendored** — FlexMCP is ours per
   internal record). Confirm the auth contract: docs show **`authtoken: <token>` header** (or
   `?authtoken=`) on `/api/v1/...`.
2. **Confirm read-only posture.** Per doctrine, **Perfex must never hold clinical data.** Audit the
   connector for any path that could write clinical content into the CRM; deny it. Restrict to
   contacts/leads/invoices/deals.
3. Verify the MCP tool count and surface against the module's OpenAPI spec; reconcile with the
   internal record (**183 tools**) and flag drift.
4. Confirm webhook signature verification is enforced on inbound webhooks.
5. Probe liveness from outside: `https://pay.nuratech.ai/` currently returns **307** — confirm the
   redirect target is intentional and not a broken canonicalisation.

**Exit criteria.** Auth contract documented with a live probe; read-only boundary proven; tool count
reconciled; webhook signatures verified.

---

## PHASE 8 — GATEWAY LANE REMEDIATION

**Defect.** `gateway_state.json` carries `needs_attention: true` on lanes with **no consumer** —
this is how a 6-day A2A outage went unseen. Currently degraded: **email**, **signal**,
**bluebubbles**, **msgraph_webhook**.

**Tasks.**
1. Confirm the new watchdogs are live and firing: `lane state watchdog` (**`a67d954e02c5`**) and
   `estate watchdog` (**`2f30c0ee660a`**). Both must be **monitor-gated** and both must report a
   **fresh heartbeat** (`--check-heartbeat`).
2. Triage each degraded lane: distinguish **config gaps** (lane deliberately unconfigured — e.g.
   discord/slack/whatsapp are broken by design) from **real degradations**. Never alert on an
   expected condition; that trains the reader to ignore the channel.
3. For each **real** degradation: root-cause, fix if reversible, otherwise escalate with the exact
   blocking action.
4. `evolution review` carries a **stale** `last_status=error` from 2026-09-01. The cause (a
   `TERMINAL_CWD` workdir lock collision with `obsidian-morning` at 08:00 on the 1st) is **already
   fixed** — the schedule moved to `45 9 1 * *`. **Do not "fix" it again**; confirm on 2026-10-01
   that it clears.
5. `emos gap audit` remains **disabled with a real failure behind it** (eMedical login). Leave
   disabled until Phase 9 resolves the root cause; enabling it now guarantees a nightly failure.

**Exit criteria.** Every degraded lane is classified as expected-vs-real with evidence; both
watchdogs verified live with fresh heartbeats.

---

## PHASE 9 — eMEDICAL GAP AUDIT (blocked on authority, not engineering)

**Established.** Credentials are **correct** (verified by fingerprint match; sealed 0600). The job
**never worked — 20 of 20 runs failed**. Current blocker: `service.emedpractice.com` returns
**HTTP 200 with title "Access Denied"** to any browser that runs JavaScript (`navigator.webdriver =
true` in headless, headful-under-Xvfb, and persistent contexts) while plain `curl` and
`page.request.get` receive the real form. **The site blocks automated browsers.**

**Do not** mask `navigator.webdriver`. That evades a deliberate control; the site itself says *"contact
the administrator to obtain access"*; and the account backs a live practice whose vendor agreement is
at stake.

**Tasks.** Pursue a **vendor-sanctioned** path: eMedical **FHIR/API** access, or a whitelist of the
automation host — requested by the account holder via enterprise support. Only if the vendor confirms
**in writing** that automated browser access is permitted should `webdriver` masking be considered,
and it must then be recorded as vendor-sanctioned.
**Meanwhile:** leave disabled. Fix the stale `emed-gap-audit.py` selector assumptions only if the
vendor path lands.

---

## PHASE 10 — VERIFICATION, MONITORING, AND RECORD

1. **Re-probe everything after every phase.** No phase is complete on the strength of its own claim.
2. **Add regression coverage** for each fixed defect (the plugin suite is the model: 23 tests that
   assert security properties, not trivia).
3. **Confirm the watchdog heartbeat** after every change — a dead watchdog is indistinguishable from
   a healthy system.
4. **Record in Notion** (board of record) with: defect · evidence · fix · verification output ·
   rollback · residual risk. Commit code changes to `eddieg73/NURA` under `ops/openemr-plugin/`.
5. **Write the trade-ticket** for anything not fixed, with the exact blocking action and owner.

---

## STOP CONDITIONS

Halt and escalate rather than proceed if:
- any step would expose PHI without an executed BAA;
- a change would put the `passthrough` verifier on a public route;
- enabling OpenEMR's API has not been explicitly authorized;
- an RFC 8707/`aud` translation cannot be made auditable;
- a fix requires stopping the container that owns the clinical ingress;
- evidence contradicts this document (the live system wins — **update this document**).
