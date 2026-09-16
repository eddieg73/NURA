# NURA OpenEMR MCP Plugin v0.2.0 — Independent Review

**Artifact:** `NURA_OpenEMR_Plugin_v0.2.0-1.zip` · 47,846 B · 39 entries · sha256 `8b05fb99d7d2a2dc…`
**Reviewed:** 2026-09-13 · **Verdict:** **BUILDS · 23/23 TESTS PASS · RUNS END-TO-END** — one real
security defect found and fixed; one documentation inconsistency, plus deployment gates to clear.

---

## 1. What it is

`@nura/openemr-mcp` — a **read-only MCP bridge for OpenEMR FHIR R4**. TypeScript, Node ≥22,
streamable-HTTP MCP at `/mcp`, OAuth 2.1 resource-server validation, RFC 8693 token exchange, and a
Codex-compatible plugin manifest declaring the `Read` capability only. No write, order, prescription,
message, or signing tool exists.

Manifest is coherent: `.mcp.json` → `http://127.0.0.1:8787/mcp`; Dockerfile is multi-stage and runs
`USER node`; `.gitignore` excludes `.env` and `dist/`.

## 2. Independent verification (all results real, not self-reported)

**Dependency install** — `npm ci` → 109 packages, exit 0.
*Note:* npm reports `esbuild` postinstall skipped by the `allow-scripts` guard. **This is benign —
verified, not assumed.** `esbuild --version` → 0.28.2; `tsx --version` → v4.23.13; and `tsx
src/index.ts` runs the TypeScript source directly with no build step, serving `/healthz` 200. npm 11
ships the platform binary as an optional dependency (`@esbuild/linux-x64`, 11 MB), so the legacy
postinstall download/link step is no longer required. An earlier draft of this review claimed the
warning "affects only `tsx`" — **that claim was made without testing and was wrong; it affects
nothing.**

**Build** — `npx tsc -p tsconfig.json` → **exit 0, zero errors** under `strict` **and**
`noUncheckedIndexedAccess`. That is a demanding configuration and it passes clean.

**Tests** — `node --test` → **23 pass / 0 fail**. The suite tests security properties, not trivia:
JWT signature+issuer+audience+expiry+scope enforcement · production refuses passthrough · production
requires token exchange · FHIR base URL rejects embedded credentials and query strings · patient
context bound to the user token · patient context rejects tampering · FHIR client **refuses
redirects** and enforces its result bound · DocumentReference projection strips Binary URLs and
embedded data · FHIR client blocks arbitrary upstream paths · token exchange uses RFC 8693 **without
exposing the subject token in logs**. (20 shipped + 3 added by this review.)

**Live end-to-end** — server started against a synthetic config and probed:

```
startup      {"event":"service_started","service":"nura-openemr","port":18787}
/healthz     HTTP 200  {"status":"ok","service":"nura-openemr","version":"0.2.0"}
headers      cache-control: no-store · pragma: no-cache · x-content-type-options: nosniff
             referrer-policy: no-referrer · content-security-policy: default-src 'none'
             (x-powered-by absent — disabled)
POST /mcp    no Authorization      -> HTTP 401 {"error":"invalid_token"}
POST /mcp    dummy bearer          -> HTTP 200, real tool list returned
GET  /mcp                          -> HTTP 405 {"error":"method_not_allowed"}
DELETE /mcp                        -> HTTP 405 {"error":"method_not_allowed"}
fail-closed  NODE_ENV=production AUTH_MODE=passthrough
             -> refused: "AUTH_MODE=jwt is required in production"
```

## 3. Security architecture — reviewed line by line

The code **enforces what `SECURITY.md` claims**. Verified specifically:

- **`auth.ts`** — `jwtVerify` with an **explicit `algorithms: ["RS256","PS256","ES256"]` allowlist**
  (blocks `alg:none` and HS256 key-confusion), issuer + audience + 5 s clock tolerance, scopes
  enforced, JWKS with cooldown/cache/timeout bounds. Signature is checked *before* any scope logic.
- **`context-token.ts`** — HMAC-SHA256 context token compared with **`timingSafeEqual`** after a
  length check; the payload is **bound to `sha256(accessToken)`**, so a context token cannot be
  replayed against another session or patient; `exp`/`iat` validated; patient id constrained by
  `/^[A-Za-z0-9.\-]{1,128}$/`.
- **`token-exchange.ts`** — correct RFC 8693 grant; `redirect: "error"` (**prevents token
  exfiltration via redirect**); AbortController timeout; response `token_type` must be bearer;
  token length floor.
- **`fhir.ts`** — upstream path regex blocks traversal and arbitrary paths; `redirect: "error"`;
  results bound via `.slice(0, count)`; `projectResource` **strips Binary `url`/`data`** from
  DocumentReference, keeping only content-type/title/creation/size/hash; provenance
  (resourceType/id/versionId/lastUpdated/source) preserved on every projected resource.
- **`audit.ts`** — emits only timestamp, correlationId, tool, outcome, resourceCount. **No chart
  content, no tokens.** Matches the documented PHI-minimization claim.
- **`server.ts`** — every tool carries `readOnlyHint:true, destructiveHint:false, idempotentHint:true,
  openWorldHint:false`. Live tool listing confirms name-only patient search is prohibited.
- **`index.ts`** — 1 MB body limit, 405 on GET/DELETE, `trust proxy` opt-in only, generic 401/502/500
  responses that leak no internals.

## 4. DEFECT FOUND AND FIXED — the server bound `0.0.0.0`

`index.ts` did `app.listen(config.port, "0.0.0.0")` while the package's **own** `.mcp.json` advertises
`http://127.0.0.1:8787/mcp` and the README instructs connecting locally. The code contradicted its own
manifest intent.

Severity is raised by the dev default: `AUTH_MODE=passthrough`, whose verifier **accepts any bearer
token**. Proven live — a dummy bearer returned HTTP 200 with the **full tool list**, and the port
answered on the host's LAN address (`http://192.168.32.2:18787/healthz` → 200). Production is
protected by the fail-closed JWT gate, but anything deployed in dev/passthrough posture exposed the
entire MCP tool surface to every reachable interface. This is the same `0.0.0.0`-plus-weak-auth class
already recorded against the NURA dashboard.

**Fix applied** (4 files):
- `src/config.ts` — new `bindHost`, default **`127.0.0.1`**, with character validation
- `src/index.ts` — `app.listen(config.port, config.bindHost)`; startup log now reports `bindHost`
- `test/config.test.ts` — 3 new tests (loopback default · explicit override · malformed rejected)
- `.env.example` — `BIND_HOST=127.0.0.1` plus a warning comment

**Verified after the fix:**

```
CASE 1 default      bindHost=127.0.0.1  loopback HTTP 200  LAN HTTP 000 (refused)
CASE 2 BIND_HOST=0.0.0.0  loopback HTTP 200  LAN HTTP 200  (deliberate exposure still possible)
CASE 3 malformed "127.0.0.1; rm -rf /tmp/nope"
                    -> refused: "BIND_HOST contains invalid characters"; /tmp/nope NOT created
```

Exposure now requires a deliberate, explicit bind, and the injection attempt was rejected at
validation and never executed. Build still clean, **23/23 tests pass**.

## 5. Documentation inconsistency

The README says *"Copy `.env.example` to `.env`"*, but **nothing loads `.env`** — there is no dotenv
import, `loadConfig()` reads `process.env` directly, and the Dockerfile does not pass `--env-file`.
Following the README literally leaves the server failing with `OPENEMR_FHIR_BASE_URL is required`
(observed). Operators must supply real environment variables (correct for containers) — the README
step should be corrected or `--env-file` used explicitly.

## 6. Residual observations (not defects)

- `/healthz` is unauthenticated and reveals service name + version. Low risk; consider trimming the
  version if the endpoint is ever publicly exposed.
- No rate limiting or request throttling at the MCP boundary. Consider it before public exposure.
- `DevelopmentPassthroughVerifier` accepts any token. Correctly production-gated, but it should never
  be reachable in a shared or staging environment.
- HTTP is permitted for localhost only; HTTPS enforced everywhere else. Verified in code and tests.

## 7. Deployment gates — authority, not engineering

The package is honest that *building or connecting to OpenEMR does not make it production-approved*,
and its `SECURITY.md`/`SAFETY_CASE.md` release gates are correct. Two gates need the founder:

1. **Vendor/platform authority.** The README notes that as of 2026-09-13 OpenAI's official guidance
   places the Epic/EHR integration beyond individual *ChatGPT for Clinicians* accounts, and that
   **NPI/licence verification plus a BAA** are prerequisites before any PHI flows. Deploy only in an
   eligible organisational ChatGPT-for-Healthcare / regulated-Enterprise workspace.
2. **NURA-side prerequisites.** An authorization server (this package is a resource server only), an
   approved RFC 8693 token-exchange gateway, OpenEMR FHIR enabled under *Administration → Config →
   Connectors*, and a client registered with read/search scopes only.

**Not yet done, and stated as such:** no threat model, no tenant-isolation or wrong-patient testing,
no prompt-injection red-team, no OpenEMR conformance run against the deployed release, no clinical
summary evaluation, no rollback rehearsal. The connector is **untested against a live OpenEMR** — the
end-to-end run above used a synthetic config and a deliberately dead upstream.

---

## Assessment

This is **well above typical quality**: strict-mode TypeScript, a security model that is actually
implemented rather than described, tests that assert the security properties, honest documentation of
residual risk, and a coherent read-only clinical boundary that preserves provenance. The single real
defect was a bind-address contradiction with its own manifest, now fixed and regression-tested.

**Recommendation:** accept as the default read-only OpenEMR connector. Hold production deployment
until the §7 authority gates and the §7 test programme are satisfied.
