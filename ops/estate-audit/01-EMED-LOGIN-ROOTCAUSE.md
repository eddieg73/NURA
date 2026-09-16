# eMedical Gap Audit — Root Cause Analysis

**Date:** 2026-09-13
**Trigger:** founder supplied eMedicalPractice credentials to fix the disabled `emos gap audit`.
**Verdict:** credentials are **correct**; the job has **never** worked; the blocker is a **site-side
access control** requiring a vendor/authority decision.

---

## 1. The credentials are NOT the problem

Compared the founder-supplied values against the stored `EMED_USERNAME` / `EMED_PASSWORD` in
`/opt/data/profiles/nura/.env` (0600) — **values never printed**, compared by exact equality:

```
field       stored len   supplied len   verdict
username    9            9              MATCH
password    10           10             MATCH
fingerprints  user=f9c6085da6  pass=8d330295d9   (identical both sides)
```

Sealed to `/opt/data/profiles/nura/home/.secrets/emedpractice.env` (0600, uid 10000).

**Rule applied:** the credential was never echoed into chat, per the 2026-09-12 incident where a live
RunPod key was printed. Only MATCH/MISMATCH, lengths, and non-reversible fingerprints are reported.

## 2. The site is healthy and reachable

```
DNS     service.emedpractice.com -> 208.115.52.69
TCP/TLS 443 OK, TLSv1.2, cert CN=service.emedpractice.com O=eMedPractice LLC (Florida)
HTTPS   HTTP 200, 53,676 bytes, Server: Microsoft-IIS/10.0, X-Powered-By: ASP.NET
```

No Cloudflare / Akamai / Imperva / captcha markers. The **real login form is served** to plain HTTP.

## 3. Browser binaries were ABSENT — now fixed

`/opt/data/profiles/nura/.cache/ms-playwright` **did not exist**, and neither did `.cache/` itself.
Installed (verified):

```
chromium-1223 · chromium_headless_shell-1223 (148.0.7778.96) · ffmpeg-1011
launch: OK (version 148.0.7778.96)
```

Corrected two of my own intermediate errors, recorded because both were instrument faults:
- *"playwright is not installed at all"* — **wrong**. playwright 1.60.0 IS in `python-packages`; I had
  probed the venv and `lazy-packages`, which do not carry it.
- *"the script's username selector is wrong"* — **wrong**. `LOGIN_EMAIL = "#email"` is **correct** and
  matches the live page exactly. I inferred a defect from a grep miss (`LOGIN_USERNAME` not found) plus
  a separate page scan, and joined two unrelated facts into a false conclusion.

## 4. The real blocker: eMedPractice denies automated browsers

Discriminator isolated to **one variable — JavaScript execution**:

| Probe | Result |
|---|---|
| raw `curl`, curl UA | **OK** — 53,676 B, real form |
| raw `curl`, browser UA | **OK** — 53,676 B, real form |
| `page.request.get` (browser net stack, no JS) | **OK** — 53,676 B, real form |
| `page.goto` headless | **Access Denied** (1,318 B) |
| `page.goto` headless, curl UA | **Access Denied** |
| `page.goto` headful under Xvfb | **Access Denied** |
| persistent context (real user-data-dir) | **Access Denied** |
| `navigator.webdriver`, every browser mode | **`true`** |

Denied body: *"Either you are not currently logged in, or you do not have access to this tab page.
Please contact the administrator to obtain access."*

**Not the IP, not the User-Agent, not headless.** Every JS-running mode reports `webdriver=true` and
is denied; every non-JS path passes. Note the page is **HTTP 200** — a status-code check alone would
score this as healthy, which is why the job's own output said `login exception` rather than an error.

## 5. The job has NEVER worked — 20 of 20 runs failed

Every artifact from 2026-08-18 to 2026-09-06 reads `Status: script failed`. Three distinct eras:

| Period | Failure | State |
|---|---|---|
| Aug 18–25 | `TypeError: '>' not supported between 'coroutine' and 'int'` — missing `await` on `.count()` at line 516 | **since fixed** (all 5 `.count()` calls now awaited) |
| Aug 26–27 | `No module named 'greenlet._greenlet'` — playwright unimportable, greenlet ABI mismatch | **resolved** (3.5.5, cp313 `.so` loads) |
| Aug 29–Sep 6 | `login blocked: login exception: TimeoutError`, `scanned=0` | superseded — current failure is **Access Denied** |
| Sep 6 | **job disabled rather than fixed** | still disabled |

**It was born broken, ran 20 failing nights, and was silenced.** Nothing surfaced it: `no_agent: true`,
`deliver: local`, and the failure existed only inside the artifact.

## 6. What is verified working now

```
emed-gap-audit.py --selftest  ->  exit 0
  [ok] SOAP — 2 dates, newest first
  [ok] labs found + ordered   [ok] X-ray found   [ok] CT received
  [ok] MRI missing (open)     [ok] consult received
  [ok] missing items = MRI only
```

The **extraction engine works**. The only unmet dependency is an authorised way to log in.

---

## 7. DECISION REQUIRED — this is an authority question, not a bug

The remaining fix would be masking `navigator.webdriver` so the site's control does not fire. **I have
deliberately NOT done this**, and will not without an explicit decision:

- it is evasion of a **deliberate access control**, not a workaround for a broken page;
- the site's own text directs the account holder to **"contact the administrator to obtain access"**;
- the account belongs to a **live practice** — the vendor agreement, not just the script, is at stake;
- standing doctrine: no CAPTCHA bypass, no ToS violations, never invent legal authority.

**Recommended path (legitimate, and already partially in flight):**
1. **eMedical FHIR / API access** — memory records *"eMedical 2nd EMR; FHIR client-reg pending"*.
   A vendor-granted interface removes the browser entirely and is the durable fix.
2. **Vendor whitelist of this host** — ask eMedical enterprise support (visible on the login page) to
   allow the automation host, with the practice owner making the request.
3. Only if the vendor confirms in writing that automated browser access is acceptable should
   `webdriver` masking be considered — and it should then be recorded as vendor-sanctioned.

**Meanwhile:** leave `emos gap audit` disabled. Enabling it now would produce a guaranteed nightly
failure, which is the exact condition that got it disabled the first time. The estate watchdog already
tracks it, so the blocker stays visible rather than silent.
