# Ensure reader (CarePilot Integrations)

Thin **propose-only** bridge from the Ensure (Solis) portal into CarePilot FastAPI.

## Lanes

| Lane | Name | Status |
|------|------|--------|
| **A** | Ensure RPA (Playwright read-only against `https://solis.ensuredatasolutions.com/Login`) | Active scaffold — smoke + propose-only intake |
| **B** | SFTP EG (`/ToSolis/` writes) | **HELD** until Martin allowlists egress `72.61.71.211`. Do not implement uploads. |

## Safety

- AI / automation = **propose-only**. No auto-orders, claims, diagnoses, med changes, or patient messages.
- Never commit secrets. Creds live in sealed `/tmp/nura-portal-creds.env` (0600) staged from profile env.
- Smoke prints `AUTH=OK|FAILED|BLOCKED` + URL (+ optional title) only — no PHI, no password, no dashboard dumps.

## Layout

- `ensure_smoke.py` — auth-only Playwright smoke
- `ensure_to_fastapi.py` — map extract/JSON → propose-only intake POST (or write `out/` if engine down)
- `out/` — normalized offline envelopes
- `.venv/` — local Playwright runtime (host Python 3.12)

## Smoke

```bash
cd /root/.hermes/carepilot/integrations/ensure_reader
ENSURE_CHROME=/root/.cache/ms-playwright/chromium-1234/chrome-linux64/chrome \
  ./.venv/bin/python ensure_smoke.py
```

## Intake stub

```bash
./.venv/bin/python ensure_to_fastapi.py --demo
# or
./.venv/bin/python ensure_to_fastapi.py --json /path/to/rows.json --base http://127.0.0.1:8100
```

Target intake path (default): `POST /api/integrations/ensure/intake`  
If that route is not wired yet, script falls back to writing `out/*.json`.

## FastAPI container

See `/root/.hermes/carepilot/backend/docker-compose.yml` (host port **8100** → container 8000).
