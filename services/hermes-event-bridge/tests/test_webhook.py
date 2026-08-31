from __future__ import annotations

import hashlib
import json
import time
from datetime import datetime, timezone
from pathlib import Path
from uuid import uuid4

from fastapi.testclient import TestClient

from app.config import Settings
from app.main import create_app
from app.security import sign_request

SECRET = "s" * 64
ADMIN = "a" * 64


def make_settings(db_path: Path) -> Settings:
    return Settings(
        webhook_secret=SECRET,
        webhook_key_id="primary",
        admin_bearer_token=ADMIN,
        db_path=db_path,
        require_https=False,
        notion_enabled=False,
        allowed_source_services=frozenset({"hermes-agent"}),
    )


def make_event(*, event_id: str | None = None, idempotency_key: str | None = None):
    actual_event_id = event_id or str(uuid4())
    return {
        "spec_version": "1.0",
        "event_id": actual_event_id,
        "event_type": "nura.hermes.review.requested.v1",
        "source_service": "hermes-agent",
        "tenant_id": "nuratech",
        "correlation_id": str(uuid4()),
        "idempotency_key": idempotency_key or hashlib.sha256(actual_event_id.encode()).hexdigest(),
        "occurred_at": datetime.now(timezone.utc).isoformat(),
        "data_classification": "INTERNAL",
        "provenance": {"test": True},
        "severity": "info",
        "notification": {
            "work_item": "Review Hermes artifact",
            "summary": "Synthetic test event",
            "lane": "Platform/Engineering",
            "priority": "P2",
            "status": "Needs Review",
            "work_type": "Review",
            "owner": "Hermes",
            "reviewer": "ChatGPT",
        },
    }


def signed_request(event: dict, *, timestamp: int | None = None, secret: str = SECRET):
    raw = json.dumps(event, separators=(",", ":"), sort_keys=True).encode()
    ts = str(timestamp or int(time.time()))
    event_id = event["event_id"]
    return raw, {
        "Content-Type": "application/json",
        "X-Hermes-Event-Id": event_id,
        "X-Hermes-Timestamp": ts,
        "X-Hermes-Key-Id": "primary",
        "X-Hermes-Signature": sign_request(secret, ts, event_id, raw),
    }


def test_accepts_signed_event(tmp_path: Path):
    app = create_app(make_settings(tmp_path / "events.db"))
    event = make_event()
    raw, headers = signed_request(event)
    with TestClient(app) as client:
        response = client.post("/v1/hermes/events", content=raw, headers=headers)
        assert response.status_code == 202
        assert response.json()["duplicate"] is False
        assert response.json()["sink_status"] == "not_configured"


def test_rejects_bad_signature(tmp_path: Path):
    app = create_app(make_settings(tmp_path / "events.db"))
    event = make_event()
    raw, headers = signed_request(event, secret="x" * 64)
    with TestClient(app) as client:
        assert client.post("/v1/hermes/events", content=raw, headers=headers).status_code == 401


def test_rejects_replay(tmp_path: Path):
    app = create_app(make_settings(tmp_path / "events.db"))
    event = make_event()
    raw, headers = signed_request(event, timestamp=int(time.time()) - 1000)
    with TestClient(app) as client:
        assert client.post("/v1/hermes/events", content=raw, headers=headers).status_code == 401


def test_deduplicates_identical_event(tmp_path: Path):
    app = create_app(make_settings(tmp_path / "events.db"))
    event = make_event()
    raw, headers = signed_request(event)
    with TestClient(app) as client:
        assert client.post("/v1/hermes/events", content=raw, headers=headers).status_code == 202
        second = client.post("/v1/hermes/events", content=raw, headers=headers)
        assert second.status_code == 200
        assert second.json()["duplicate"] is True


def test_rejects_idempotency_collision(tmp_path: Path):
    app = create_app(make_settings(tmp_path / "events.db"))
    shared_key = "k" * 64
    first_event = make_event(idempotency_key=shared_key)
    second_event = make_event(idempotency_key=shared_key)
    first_raw, first_headers = signed_request(first_event)
    second_raw, second_headers = signed_request(second_event)
    with TestClient(app) as client:
        assert client.post("/v1/hermes/events", content=first_raw, headers=first_headers).status_code == 202
        assert client.post("/v1/hermes/events", content=second_raw, headers=second_headers).status_code == 409


def test_rejects_phi_notification(tmp_path: Path):
    app = create_app(make_settings(tmp_path / "events.db"))
    event = make_event()
    event["data_classification"] = "PHI"
    event["payload_ref"] = "b2://nura-private/events/object.json"
    event["payload_sha256"] = "f" * 64
    raw, headers = signed_request(event)
    with TestClient(app) as client:
        assert client.post("/v1/hermes/events", content=raw, headers=headers).status_code == 422


def test_admin_feed_requires_token(tmp_path: Path):
    app = create_app(make_settings(tmp_path / "events.db"))
    with TestClient(app) as client:
        assert client.get("/v1/hermes/events").status_code == 401
        assert client.get("/v1/hermes/events", headers={"Authorization": f"Bearer {ADMIN}"}).status_code == 200


def test_source_allowlist(tmp_path: Path):
    app = create_app(make_settings(tmp_path / "events.db"))
    event = make_event()
    event["source_service"] = "unknown-agent"
    raw, headers = signed_request(event)
    with TestClient(app) as client:
        assert client.post("/v1/hermes/events", content=raw, headers=headers).status_code == 403
