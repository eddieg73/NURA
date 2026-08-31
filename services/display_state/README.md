# NURA Display-State Service

Small Flask service that exposes the current NURA edge-display state and serves the browser display client.

## Purpose

The service converts a local JSON state document into a versioned HTTP interface for browser and edge consumers. It is an operational display surface, not a clinical decision engine.

## Endpoints

- `GET /healthz` — validates that the configured state file can be loaded.
- `GET /api/v1/display-state` — returns the current display-state document with `Cache-Control: no-store`.
- `GET /` — serves the browser display UI.

## Configuration

| Variable | Default | Purpose |
| --- | --- | --- |
| `DISPLAY_STATE_FILE` | `display_state.example.json` | JSON state document |
| `DISPLAY_STALE_SECONDS` | `900` | Age after which state is marked stale |
| `DISPLAY_BIND` | `127.0.0.1` locally; `0.0.0.0` in container | Bind address |
| `DISPLAY_PORT` | `8787` | HTTP port |

Do not place credentials or PHI in the display-state payload.

## Local run

```bash
python -m venv .venv
. .venv/bin/activate
pip install -r requirements.txt
python app.py
curl -fsS http://127.0.0.1:8787/healthz
curl -fsS http://127.0.0.1:8787/api/v1/display-state
```

## Tests

```bash
python -m unittest -v test_app.py
```

## Container

```bash
docker build -t nura/display-state:local .
docker run --rm -p 127.0.0.1:8787:8787 nura/display-state:local
curl -fsS http://127.0.0.1:8787/healthz
```

## Production requirements

Before exposing this service:

1. inspect the target host for port and proxy conflicts;
2. keep the application port private and terminate TLS at the approved reverse proxy;
3. provide state through a controlled writer or mounted file;
4. verify stale-state behavior;
5. verify logs contain no PHI or secrets;
6. verify health after container restart;
7. document the deployed image/commit SHA and rollback image; and
8. monitor the health endpoint and stale-state signal.

## Data classification

Expected classification: operational metadata only. PHI and credentials are prohibited from the state document and browser display.
