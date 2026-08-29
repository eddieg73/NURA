# OIE Mirth 4.6.0 Admin Password — Fixed In-Place (2026-08-23)

**Status:** RESOLVED — `/api/users/_login` → SUCCESS, `/api/channels` → 200.

## Root cause
The 4.6.0 engine (`nuratech/connect:4.6.0-nura.1`, admin `:8445`, MLLP `:6661→:6663`)
was 401-ing on every candidate password, including the sealed file and the default.
The prior diagnosis ("custom KDF — decompile or redeploy fresh, 0 channels") was
WRONG on both counts.

- Mirth/OIE ≥4.4 verifies passwords with **PBKDF2WithHmacSHA256, 600,000
  iterations, 8-byte salt, 256-bit key**, stored as `base64(salt[8] ‖ digest[32])`.
- This DB was **seeded with a LEGACY single SHA-256 hash** (`SHA256(salt ‖ password)` —
  the <4.4 format, resolving to the stock default `admin`), and **no
  `digest.fallback.algorithm` is configured**, so NO password could verify
  (plain SHA-256 and PBKDF2 both returned 401 — the earlier "custom KDF" claim was false).

## Fix (in-place, no redeploy)
```bash
# On Clinic: docker exec mirth-oie46-postgres-db-1 psql -U mirth -d enginedb
# Compute: base64(salt8 ‖ PBKDF2_hmac_sha256(pw, salt, 600000, 32))
UPDATE person_password SET password='<new-blob>', password_date=now() WHERE person_id=1;
```
Verified live: `/api/users/_login` → `SUCCESS`; `GET /api/channels` → 200.

## CRITICAL — the engine is NOT empty
Holds 3 channels. A "fresh redeploy to reset admin" would DESTROY them:
- `SOLIS_ENSURE_INBOUND` (f82dac78-...) — STARTED, container :6661 → host :6663, 4 msgs received
- `OPENEMR_HERMES_BRIDGE` (...661)
- `RISPACS_HERMES_BRIDGE` (...662)

Only `:6663`/`:8086`/`:8445` are listening on host; the described 6665/6666/6667 remain
to be verified once the ORU return loop is wired.

## Current admin credential
- username `admin`, new password sealed **`/opt/data/mirth-oie-admin.txt`** (0600).
- `.env` `MIRTH_PASS` is the OLD 4.5.2 engine (port 8444) — dead for 4.6.0.
