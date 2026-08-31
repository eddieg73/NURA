# NURA Hermes Event Bridge

A signed, append-only webhook receiver for Hermes. It accepts the canonical NURA event envelope, prevents replay and duplicate writes, stores an audit record, and can optionally create or update rows in the Hermes↔ChatGPT Notion Coordination Board.

## Architecture

```text
Hermes -> HTTPS/HMAC webhook -> SQLite audit/event store -> optional Notion coordination row
                                             -> protected event feed for JARVIS review
```

This follows the NURA event doctrine: events carry references, not PHI payloads. PHI-classified events require a `payload_ref` plus SHA-256 and are never forwarded to Notion.

## Security controls

- HMAC-SHA256 signature over `timestamp.event_id.raw_body`
- five-minute replay window by default
- key ID for secret rotation
- event-ID and idempotency-key uniqueness
- collision detection when a reused key has different content
- source-service allowlist
- maximum envelope size
- HTTPS enforcement behind Nginx Proxy Manager or Traefik
- append-only SQLite audit log using WAL
- protected admin feed and retry endpoint
- no request-body logging
- PHI forwarding block

## Endpoints

- `POST /v1/hermes/events` — receive signed event
- `GET /healthz` — process health
- `GET /readyz` — event-store readiness
- `GET /v1/hermes/events` — recent events, bearer token required
- `GET /v1/hermes/events/{event_id}` — one event, bearer token required
- `POST /v1/hermes/events/{event_id}/retry` — retry Notion delivery
- `GET /v1/hermes/stats` — delivery counts

## Required headers

```text
X-Hermes-Event-Id: <event_id>
X-Hermes-Timestamp: <unix-seconds>
X-Hermes-Key-Id: primary
X-Hermes-Signature: v1=<hmac-sha256-hex>
Content-Type: application/json
```

## Recommended event types

- `nura.hermes.review.requested.v1`
- `nura.hermes.status.updated.v1`
- `nura.hermes.alert.raised.v1`
- `nura.hermes.artifact.ready.v1`
- `nura.hermes.heartbeat.v1` — stored only by default

## Run locally

```bash
cp .env.example .env
# replace both secrets
python -m venv .venv
. .venv/bin/activate
pip install -r requirements-dev.txt
pytest

# for local HTTP only set REQUIRE_HTTPS=false
uvicorn app.asgi:app --host 127.0.0.1 --port 8080
```

Send a signed synthetic event:

```bash
python scripts/send_event.py \
  --url http://127.0.0.1:8080/v1/hermes/events \
  --work-item "Hermes webhook smoke test" \
  --summary "Synthetic event; no PHI"
```

## Hostinger deployment

1. Deploy on the Clinic or Edge node and keep port 8080 private.
2. Attach the container to the existing `nura_app` network.
3. Generate separate webhook/admin secrets with `openssl rand -hex 32`.
4. Add TLS routing such as `hermes-events.nuratech.ai` through NPM/Traefik.
5. Restrict source IP/Tailnet where practical in addition to HMAC.
6. Enable the Notion sink only after the integration is authorized for the coordination data source.
7. Run the same signed event twice; the second call must return `duplicate=true` and create no second downstream record.
8. Back up `/data/hermes-events.sqlite3` through the approved encrypted backup process.

Hermes should reuse the same `event_id`, body, and idempotency key for transport retries. New business events receive new IDs.
