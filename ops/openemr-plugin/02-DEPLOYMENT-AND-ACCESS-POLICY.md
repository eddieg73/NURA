# NURA OpenEMR MCP — Deployment Record & Access Policy

**Date:** 2026-09-13
**Founder approval:** *"Yes — deploy the plugin + fix the public HTTPS route, synthetic data only (no PHI)."*
**Access policy (founder, 2026-09-13):** *"We provide the plug in for verified healthcare professional
accounts only initially. We can then do it for paramedics and nurses with license number."*

---

## 1. ACCESS POLICY (governance — binding on the connector)

**Phase 1 — verified healthcare professional accounts only.**
**Phase 2 — extend to paramedics and nurses by license number.**

This is not marketing copy; it constrains the auth model:

- Enrollment is **gated on credential verification**, so the authorization layer must assert a
  **verified clinician identity** — not merely "a logged-in user". The plugin already carries the
  right primitives: `openid`, `fhirUser`, and `user/*.read` scopes, with `fhirUser` identifying the
  acting clinician.
- **Identity binding must be to a real, verified professional record.** A token that says
  "authenticated" is insufficient; the issuing server must attest the licence/NPI and the
  permitted role.
- **Phase 2 needs a licence-number verification step** before a paramedic or nurse account is
  provisioned. The scope granted must match the role — do not issue a nurse the same scope set as an
  attending physician without a clinical decision.
- **Least-privilege per phase.** All phases are **read/search only**. No write, order, prescribe,
  message, or signing scope. The connector ships no such tool and none should be added for these
  cohorts.
- **Verified identity is also the audit unit.** `audit.ts` logs `correlationId`/tool/outcome/count
  with no PHI; the *identity* of the verified professional is what makes a retrieval attributable.

**Registration/verification is the gate — not the URL.** Until verification exists, the connector
must not serve PHI to any account, regardless of workspace eligibility.

## 2. WHAT IS DEPLOYED AND VERIFIED

**Plugin** — `nura-openemr-mcp:0.2.1` on clinic (`srv1441409`), image built from the reviewed +
patched source (265 MB).

```
container   nura-openemr-mcp   restart=unless-stopped   network=host
bind        172.17.0.1:8787 (docker bridge gateway only — NOT the public interface)
public      http://72.61.71.211:8787 -> refused
```

**Public route — was 100% dead, now working:**

```
TLS         CN=mcp.nuratech.ai · issuer=Let's Encrypt · ssl_verify=0 (VALID)
GET  /healthz  -> 200  {"status":"ok","service":"nura-openemr","version":"0.2.0"}
GET  /mcp      -> 405  method_not_allowed            (POST-only, correct)
POST /mcp      -> 401  Missing Authorization header  (fail-closed)
GET  /.well-known/oauth-protected-resource -> 200
discovery   resource=https://mcp.nuratech.ai  scopes=[ehr.read]  bearer=header
PACS        pacs 401 / ris 200 (with -k)  -> UNCHANGED, no regression
```

### Why the route was dead

Host nginx is **`inactive`**, so the `mcp.nuratech.ai` vhost in `/etc/nginx/sites-enabled/` was
**inert config**. `:443` is owned by **`radris-stack-nginx-1`**, whose only `server_name`s were
`_` (catch-all), `pacs`, `ris`, `viewer` — **no `mcp`**. Requests fell through to the PACS default
and received its **self-signed** certificate, so TLS verification failed → HTTP 000.

**Fix applied** (not to host nginx — to the container that actually owns :443):

- `/docker/radris-stack/nginx/certs/mcp.nuratech.ai.{crt,key}` — the existing LE cert for the
  correct hostname
- `/docker/radris-stack/nginx/conf.d/mcp.conf` — new vhost → `http://host.docker.internal:8787`
- `nginx -t` → **successful**; `nginx -s reload` → **exit 0**
- Documented lesson: **add vhosts to `radris-stack-nginx-1`, never to host nginx.** Skill:
  `tls-ownership-drift-prevention`.

### Why the bind is 172.17.0.1 and not 0.0.0.0

`host.docker.internal` resolves to **172.17.0.1** (docker bridge gateway) inside containers, so a
loopback-only bind was unreachable and produced **502**. Binding to the **bridge gateway** satisfies
both constraints: nginx can reach it, the **public interface cannot** (verified refused), and the
plugin keeps `--network host` so it can still reach OpenEMR at `127.0.0.1:32777` — which
`config.ts` **requires**, since it rejects non-HTTPS unless the host is `localhost`.

**Explicitly NOT done:** exposing the `passthrough` verifier publicly. That verifier accepts *any*
bearer token and would have recreated the exact "wide bind + any token" defect this plugin's own
review identified. The connector runs `AUTH_MODE=jwt` even though authentication cannot yet succeed.

## 3. CURRENT STATE — fail-closed by design

`AUTH_MODE=jwt` points at OpenEMR's advertised OAuth endpoints. OpenEMR's authorization server is
**disabled** (`rest_api=0`, `rest_fhir_api=0`, `/oauth2/default/jwk` → *"API is disabled"*), so the
JWKS fetch fails and **every MCP call is rejected**. That is deliberate: the route and the auth
plumbing are live, and nothing is reachable until real authentication exists.

```
POST /mcp with any bearer -> HTTP 500 {"error":"server_error"}
```

> ⚠️ **Defect worth reporting upstream:** an unreachable JWKS yields **500**, not 401/503. The
> request is correctly *denied*, but the status misrepresents it as a server fault. A `401` (or `503`)
> would be correct and would keep monitoring honest — a 500 storm looks like an outage rather than
> "auth not configured". Not patched here; flagged for the next revision.

## 4. REMAINING GATES

| # | Gate | Owner | Status |
|---|---|---|---|
| 1 | Enable OpenEMR REST/FHIR + OAuth2; register a read/search-only client | **Founder authorization** | NOT DONE — security-relevant change to a live EHR |
| 2 | Expose an OAuth authorization server publicly (currently `127.0.0.1:32777`) | Engineering, after #1 | Blocked by #1 |
| 3 | Verify token format — JWT+JWKS vs opaque+introspection | Engineering, after #1 | UNSOLVED. `client-confidential-symmetric` may imply **opaque** tokens; if so the plugin's `jwt` mode **cannot** validate them and **no introspection verifier ships** |
| 4 | Clinician credential verification (licence/NPI) per the access policy | **Founder / ops** | Policy set; implementation pending |
| 5 | Eligible ChatGPT workspace + **BAA** | **Founder** | Founder confirms org/Enterprise access can be obtained |
| 6 | Cert renewal — `mcp.nuratech.ai` expires **2026-09-14 09:49 UTC** | Engineering | ⚠️ URGENT. `certbot` renewal uses `authenticator=nginx` but **host nginx is inactive**, so renewal will FAIL. Needs a route that works through the radris container (webroot) or another validation method |

## 5. SECURITY FINDINGS OBSERVED IN PASSING

1. **Credential embedded in an nginx config.** `viewer.conf` in `radris-stack-nginx-1` contains a
   `proxy_set_header Authorization "Basic <base64>"` for Orthanc — a **plaintext credential in a
   config file** (value not reproduced here). Recommend moving to an env/file secret and rotating.
2. **`pacs`/`ris`/`viewer` all serve the SAME self-signed certificate** (`CN=pacs.nuratech.ai`,
   issued Aug 15). Those hostnames are therefore **untrusted by every browser** — `curl` without
   `-k` returns 000. Pre-existing, unrelated to this change, but it means the clinical RIS/PACS
   endpoints are effectively TLS-broken for users.
3. **Certbot will silently fail to renew** any host cert while `authenticator=nginx` is configured
   against an inactive nginx (see gate #6).

## 6. ROLLBACK

Fully reversible in minutes:

```bash
# remove the public route
rm /docker/radris-stack/nginx/conf.d/mcp.conf
docker exec radris-stack-nginx-1 nginx -s reload
# stop the service
docker rm -f nura-openemr-mcp
# source + image
rm -rf /docker/nura-openemr-mcp
docker rmi nura-openemr-mcp:0.2.1
```

No OpenEMR setting was changed. No PHI was ever requested, returned, or stored: the upstream is a
non-existent synthetic endpoint and the connector refused every authenticated call.
