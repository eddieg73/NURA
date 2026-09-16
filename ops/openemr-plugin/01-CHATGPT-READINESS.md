# Using the NURA OpenEMR MCP Plugin with ChatGPT — Readiness Assessment

**Date:** 2026-09-13
**Founder directive:** *"Need to use this plug to chat with chat gpt."*
**Verdict:** the **plugin is ready**; the **path to ChatGPT is blocked in three places**, two of which
need founder authorization and one of which only the founder can clear externally.

---

## 1. What is verified WORKING

| Layer | State | Evidence |
|---|---|---|
| The plugin itself | **READY** | `tsc` exit 0 (strict); **23/23 tests pass**; server starts, `/healthz` 200, auth enforced, 405s correct, fail-closed proven |
| OpenEMR FHIR metadata | **LIVE** | `/apis/default/fhir/metadata` → HTTP 200, 35,811 B, `CapabilityStatement`, `fhirVersion 4.0.1`, software `OpenEMR` |
| OpenEMR SMART discovery | **LIVE** | `/apis/default/fhir/.well-known/smart-configuration` → HTTP 200, 7,976 B |
| Required FHIR resources | **ALL PRESENT** | Patient · Condition · AllergyIntolerance · MedicationRequest · MedicationDispense · Observation · Encounter · DiagnosticReport · Procedure · DocumentReference (34 resource types advertised) |
| PKCE support | **YES** | `code_challenge_methods_supported: S256` |
| OpenEMR's own OAuth AS | **ADVERTISED** | `authorization_endpoint`, `token_endpoint`, `introspection_endpoint`, `jwks_uri` all published |
| Clinic host / fleet | **REACHABLE** | all three nodes SSH-accessible; clinic = `srv1441409` |

OpenEMR publishing its own SMART authorization server matters: the plugin package explicitly states
it **does not ship an authorization server**, so OpenEMR filling that role removes a major build.

## 2. BLOCKER A — ChatGPT-side eligibility (only the founder can clear)

Per the plugin's own README, as of 2026-09-13:

- OpenAI's official guidance places the **Epic/EHR integration beyond individual *ChatGPT for
  Clinicians* accounts**. Deploy only in an **eligible organisational ChatGPT for Healthcare or a
  regulated Enterprise workspace**.
- **NPI and licence verification** are required.
- **PHI must not be used until the BAA and all required third-party agreements are in place.**

**This is an authority gate, not an engineering one. Nothing I deploy changes it.** No PHI may flow
through this connector until the BAA exists.

## 3. BLOCKER B — OpenEMR's OAuth2 authorization server is DISABLED

Read from OpenEMR's own `globals` table (single site, one row each):

```
rest_api                = 0     <-- DISABLED
rest_fhir_api           = 0     <-- DISABLED
rest_portal_api         = 0
rest_system_scopes_api  = 0
oauth_clients (table)   = EMPTY <-- no client registered
```

Live probes confirm the effect:

```
/apis/default/fhir/metadata   -> HTTP 200   (FHIR metadata is public)
/apis/default/fhir/Patient    -> HTTP 401   (auth middleware runs first)
/apis/default/api/patient     -> HTTP 401   (same)
/oauth2/default/token         -> HTTP 404   {"message":"OpenEMR Error: API is disabled"}
/oauth2/default/authorize     -> HTTP 404   "API is disabled"
/oauth2/default/jwk           -> HTTP 404   "API is disabled"
```

**Interpretation:** the resource routes exist and reject unauthenticated calls, but the
**authorization server cannot issue a token**. The plugin's `AUTH_MODE=jwt` validates tokens via
`jose.jwtVerify` against a JWKS — with `/oauth2/default/jwk` disabled there is nothing to validate
against. **The auth chain is broken at the source, not in the plugin.**

To fix, an administrator must enable the REST/FHIR API and OAuth2 in **Administration → Config →
Connectors**, then **register an OAuth client** (client id/secret, redirect URIs, read/search scopes).

> ⚠️ **This is a security-relevant production change to a LIVE clinical system** (`openemr-zklo-openemr-1`,
> healthy, up 2 weeks). Enabling the REST API widens its attack surface. Per standing doctrine this is
> **authorization-gated — I have not touched it.**

Also unresolved: OpenEMR advertises `client-confidential-symmetric`, which often means **opaque**
tokens with introspection. If it issues opaque rather than JWT tokens, the plugin's `jwt` mode cannot
validate them and **no introspection verifier is shipped** — that would need either OpenEMR JWT
configuration or a plugin change. **Verify token format once OAuth is enabled.**

## 4. BLOCKER C — `mcp.nuratech.ai` has been publicly DEAD

The domain exists and resolves correctly, but it has never served:

- DNS `mcp.nuratech.ai` → **72.61.71.211** (clinic) ✓
- Host nginx HAS an `mcp.nuratech.ai` vhost proxying to `127.0.0.1:8088` — but **host nginx is
  `inactive`**, so that config is **dead**.
- **`:443` on clinic is owned by `radris-stack-nginx-1`** (nginx container, `0.0.0.0:443->443`).
- Its only `server_name`s are **`_` (catch-all), `pacs.nuratech.ai`, `ris.nuratech.ai`,
  `viewer.nuratech.ai`** — **there is no `mcp.nuratech.ai` block.**
- Therefore mcp requests fall through to the PACS default and receive its **self-signed** cert →
  TLS validation fails → **HTTP 000**.

Compounding details:
- The `mcp.nuratech.ai` Let's Encrypt cert expires **2026-09-14 09:49 UTC — tomorrow** (moot while the
  vhost is dead, but it must be renewed before any use).
- `radris-stack-nginx-1` holds only one cert pair in `/etc/nginx/certs/` (`fullchain.pem`,
  `privkey.pem`) and mounts `/docker/radris-stack/nginx/{certs,conf.d}`.
- **`:8088` is a DIFFERENT, older server** — image `nuratech-mcp-server` (Node 20.20.2, built
  2026-06-16). `POST /mcp` returns `{"tool":"handle_patient_request","reply":"…book an appointment or
  ask a question?","escalate":false}` — a **conversational receptionist bot, not this FHIR bridge.**
  The reviewed plugin is **not deployed anywhere.**

This is the **TLS-ownership-drift** class: a valid-looking vhost that owns nothing.

## 5. What remains to deploy (in order)

1. **Decide the public hostname** for the FHIR bridge. `mcp.nuratech.ai` currently implies the
   conversational bot on `:8088`; the new plugin needs its own host or port to avoid a collision.
2. **Obtain a valid cert** for that hostname and mount it into `radris-stack-nginx-1`.
3. **Add the vhost to `radris-stack-nginx-1`** — the container that actually owns `:443` — proxying to
   the plugin's port. Do **not** add it to host nginx; that config is inert.
4. **Run the plugin** (Node ≥22) with a **non-PHI synthetic config** first, and verify the full chain.
5. **Enable OpenEMR OAuth2 + register a read-only client** — *authorization required* (Blocker B).
6. **Connect ChatGPT** — *requires the eligible workspace + BAA* (Blocker A). Only then may PHI flow.

## 6. Recommendation

**Do not connect PHI yet.** Sequence it safely:

- **Now, no approval needed:** leave everything as-is; the assessment is complete and evidence-backed.
- **With your go-ahead (reversible infra):** deploy the plugin + fix the public HTTPS route, verified
  against **synthetic/local data only**. This proves the plumbing with zero PHI exposure.
- **With your explicit authorization (security-relevant, live EHR):** enable OpenEMR's REST/FHIR +
  OAuth2 and register a read/search-only client.
- **Only you can do:** confirm the ChatGPT workspace is eligible (org/Enterprise + NPI verification)
  and that a **BAA is executed**. Until then the connector must stay off PHI.

**Bottom line:** the plugin is not the problem — it is built, tested, and running. The path to
ChatGPT is blocked by a disabled authorization server, a publicly broken hostname, and an external
BAA/eligibility gate. Two are engineering tasks I can execute on your word; the third is yours.
