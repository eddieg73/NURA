# Security Measures — CarePilot server (eMedical login) · best-practice

For Osama — the server/app that automates the Solis/eMedical login. Apply these before any further PHI automation.

## 1. Web-server security headers (add at the Nginx/HTTPS layer)
```nginx
# carepilot vhost / server block
add_header Strict-Transport-Security "max-age=31536000; includeSubDomains" always;
add_header Content-Security-Policy "default-src 'self'; script-src 'self'; img-src 'self' data:; style-src 'self' 'unsafe-inline'; object-src 'none'; base-uri 'self'; frame-ancestors 'none'" always;
add_header X-Frame-Options "DENY" always;
add_header X-Content-Type-Options "nosniff" always;
add_header Referrer-Policy "strict-origin-when-cross-origin" always;
add_header Permissions-Policy "camera=(), microphone=(), geolocation=()" always;
proxy_hide_header X-Powered-By;           # stop leaking "PHP/8.4.21"
server_tokens off;
```
Then `nginx -t && systemctl reload nginx`.

## 2. Credential & secret hygiene (the login creds)
- All Solis / eMedical / OAuth creds live in a **sealed secret store** (`.env` 0600 / vault), **never in code or committed** — past leaks were from hardcoded creds.
- **Least-privilege scopes** (read-only where possible); **rotate** on personnel/contract change; kill any token not in use.
- If the login is automated: randomize + throttle the login cadence (the bot-board flags burst activity), use the vendor's **API** not a portal scrape (see #4).

## 3. PHI compliance
- **BAA** on file for any eMedical/EHR/HIPAA data processing (eMedical FHIR server, backups).
- **Encryption at rest + in transit** (TLS 1.3/1.2 only); **no PHI in logs** (debug logs strip member/HCC identifiers).
- **Role-based access** — staff/agents see only the minimum; no PHI in unsecured push/CRM/chat.
- Keep the CarePilot app + DB on a **non-public network** (it's already behind the CDN edge); no admin/DB ports public.

## 4. The automation lane — use the sanctioned API, not a stealth scrape
- If CarePilot logs into the eMedical **web portal** with a stealth browser/anti-bot bypass to pull PHI, that's a **vendor-terms + compliance risk** even for your own data. 
- Switch the eMedical pull to the **vendor FHIR/REST API** (SiteAdmin → FhirSetup → register a client, OIDC) — clean, auditable, no bot-wall. This is what we've wired on the NURA side (`nura_emedical_fhir.py`).

## 5. Operational hardening
- **2FA/MFA** on CarePilot admin + the eMedical login (we honored the OTP gate — do the same).
- **Rate-limit** the login + API; **audit-log** all automated access (who/what/when, correlation id).
- **Least-privilege accounts** for the automation (service account, not a human admin).
- Monitor for **unusual volume/anomalous logins** (the bot-board will flag burst/repeat patterns).

## 6. Other (from the white-hat scan of carepilot.nuratech.ai)
- ✅ Already good: TLS 1.3 + Let's Encrypt, `secure`/`httponly`/`samesite` cookies, Laravel CSRF, no exposed `.env`/`.git`/admin paths.
- ⚠️ Fix: the 5 headers above (HSTS/CSP/XFO/XCTO/Referrer) + hide `X-Powered-By` + `server_tokens off`.
