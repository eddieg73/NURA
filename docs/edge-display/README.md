# NURA OSINT Edge Display

## Status

Implementation scaffold is now committed. The physical ESP32/Raspberry Pi screen and Notion display are designed as presentation clients of the same normalized state.

## Architecture

```text
OSINT sources
    |
    v
Hermes / collector services
    |
    v
Verification + confidence layer
    |
    v
GET /api/v1/display-state
    |
    +--> ESP32 / Raspberry Pi display
    |
    +--> Notion / browser edge display
```

## Implemented files

- `services/display_state/app.py` — Flask service with `/api/v1/display-state` and `/healthz`.
- `services/display_state/display_state.example.json` — version 1.0 state contract example.
- `services/display_state/web/index.html` — live JARVIS-style browser/Notion display, polling every 30 seconds.
- `services/display_state/Dockerfile` — container build and health check.
- `services/display_state/test_app.py` — API smoke tests.
- `docs/edge-display/display.html` — standalone display client that can target an API using `?api=`.

## DisplayState contract

```json
{
  "schema_version": "1.0",
  "generated_at": "2026-08-31T05:00:00Z",
  "system_status": "ONLINE",
  "threat_level": "NORMAL",
  "p0_alerts": 0,
  "source_health": "HEALTHY",
  "brief_status": "READY",
  "top_signal": {
    "title": "Waiting for next verified high-priority item",
    "priority": "P2",
    "confidence": "H",
    "domain": "Ops/Vendor",
    "provenance": []
  },
  "watch_domains": ["Geo/Regional","Cyber/Tech","Ops/Vendor","Markets","Space/Aviation","Weather"]
}
```

## Local smoke test

```bash
cd services/display_state
python -m venv .venv
. .venv/bin/activate
pip install -r requirements.txt
python -m unittest test_app.py
python app.py
```

Open `http://127.0.0.1:8787/` and verify `/healthz` and `/api/v1/display-state`.

## Docker smoke test

```bash
cd services/display_state
docker build -t nura-display-state .
docker run --rm -p 8787:8787 nura-display-state
```

## Hostinger deployment boundary

Do not deploy over the existing Hermes installation without first inventorying its containers, reverse proxy, ports, volumes, environment files, backups, and current repository revision. Recommended deployment is a separate container behind the existing TLS reverse proxy, with an authenticated or network-restricted write path for Hermes and a least-privilege read endpoint for displays.

## Security and governance

- Never hard-code credentials in firmware, Notion, or GitHub.
- Preserve source provenance for every displayed claim.
- Prefer primary sources and corroborate high-impact claims when feasible.
- Explicitly label low-confidence/speculative information.
- Minimize PII; do not target private individuals.
- Cache last-known-good state on edge devices and show stale state visibly.

## Acceptance criteria

- ESP32 and Notion show the same top signal and threat state.
- Both consume the same versioned payload.
- Last-sync timestamp and stale status are visible.
- P0 events can override normal display state.
- Every displayed signal can be traced to provenance in the OSINT board.

## Remaining deployment work

1. Inspect the Hostinger Hermes runtime and choose an unused internal port/reverse-proxy route.
2. Deploy `services/display_state` as a separate container.
3. Connect Hermes verified-output workflow to atomically update the DisplayState store.
4. Publish the HTTPS display URL.
5. Embed that HTTPS URL in Notion.
6. Configure the ESP32/Raspberry Pi client against the same endpoint.
