from __future__ import annotations

import json
import logging
from contextlib import asynccontextmanager
from typing import Annotated, Any

from fastapi import Depends, FastAPI, Header, HTTPException, Request, Response, status
from fastapi.responses import JSONResponse
from pydantic import ValidationError

from .config import Settings
from .models import DataClassification, EventReceipt, HermesEvent
from .notion_sink import NotionCoordinationSink, NotionSinkError
from .security import SignatureError, verify_request
from .storage import EventStore, IdempotencyConflict

LOGGER = logging.getLogger("nura.hermes_event_bridge")


def create_app(settings: Settings | None = None) -> FastAPI:
    active_settings = settings or Settings.from_env()
    store = EventStore(active_settings.db_path)
    notion_sink = (
        NotionCoordinationSink(
            token=active_settings.notion_token or "",
            data_source_id=active_settings.notion_coordination_data_source_id or "",
            api_version=active_settings.notion_api_version,
            timeout_seconds=active_settings.notion_timeout_seconds,
        )
        if active_settings.notion_enabled else None
    )

    @asynccontextmanager
    async def lifespan(_: FastAPI):
        store.initialize()
        yield
        if notion_sink:
            notion_sink.close()

    app = FastAPI(
        title="NURA Hermes Event Bridge",
        version="1.0.0",
        docs_url="/docs" if active_settings.enable_docs else None,
        redoc_url=None,
        openapi_url="/openapi.json" if active_settings.enable_docs else None,
        lifespan=lifespan,
    )

    @app.middleware("http")
    async def security_headers(request: Request, call_next):
        response = await call_next(request)
        response.headers["X-Content-Type-Options"] = "nosniff"
        response.headers["X-Frame-Options"] = "DENY"
        response.headers["Referrer-Policy"] = "no-referrer"
        response.headers["Cache-Control"] = "no-store"
        return response

    def require_admin(authorization: Annotated[str | None, Header()] = None) -> None:
        expected = f"Bearer {active_settings.admin_bearer_token}"
        if authorization != expected:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Unauthorized")

    @app.get("/healthz")
    def healthz() -> dict[str, str]:
        return {"status": "ok"}

    @app.get("/readyz")
    def readyz() -> dict[str, str]:
        if not store.ping():
            raise HTTPException(status_code=503, detail="Event store unavailable")
        return {"status": "ready"}

    @app.post("/v1/hermes/events", response_model=EventReceipt, status_code=status.HTTP_202_ACCEPTED)
    async def receive_event(
        request: Request,
        response: Response,
        x_hermes_event_id: Annotated[str | None, Header()] = None,
        x_hermes_timestamp: Annotated[str | None, Header()] = None,
        x_hermes_signature: Annotated[str | None, Header()] = None,
        x_hermes_key_id: Annotated[str | None, Header()] = None,
    ) -> EventReceipt:
        if active_settings.require_https:
            forwarded_proto = request.headers.get("x-forwarded-proto")
            if request.url.scheme != "https" and forwarded_proto != "https":
                raise HTTPException(status_code=400, detail="HTTPS is required")
        if request.headers.get("content-type", "").split(";", 1)[0] != "application/json":
            raise HTTPException(status_code=415, detail="Content-Type must be application/json")
        raw_body = await request.body()
        if not raw_body:
            raise HTTPException(status_code=400, detail="Request body is required")
        if len(raw_body) > active_settings.max_body_bytes:
            raise HTTPException(status_code=413, detail="Event envelope is too large")

        required_headers = {
            "X-Hermes-Event-Id": x_hermes_event_id,
            "X-Hermes-Timestamp": x_hermes_timestamp,
            "X-Hermes-Signature": x_hermes_signature,
            "X-Hermes-Key-Id": x_hermes_key_id,
        }
        missing = [name for name, value in required_headers.items() if not value]
        if missing:
            raise HTTPException(status_code=400, detail=f"Missing headers: {', '.join(missing)}")

        try:
            verify_request(
                raw_body=raw_body,
                event_id=x_hermes_event_id or "",
                timestamp=x_hermes_timestamp or "",
                signature_header=x_hermes_signature or "",
                key_id=x_hermes_key_id or "",
                expected_key_id=active_settings.webhook_key_id,
                secret=active_settings.webhook_secret,
                max_age_seconds=active_settings.max_age_seconds,
            )
        except SignatureError as exc:
            raise HTTPException(status_code=401, detail=str(exc)) from exc

        try:
            event = HermesEvent.model_validate(json.loads(raw_body))
        except (json.JSONDecodeError, ValidationError) as exc:
            raise HTTPException(status_code=422, detail="Invalid Hermes event envelope") from exc
        if str(event.event_id) != x_hermes_event_id:
            raise HTTPException(status_code=400, detail="Header and body event IDs differ")
        if active_settings.allowed_source_services and event.source_service not in active_settings.allowed_source_services:
            raise HTTPException(status_code=403, detail="Source service is not allowlisted")

        try:
            ingest_result = store.ingest(
                event=event,
                raw_body=raw_body,
                remote_addr=request.client.host if request.client else None,
                signature_key_id=x_hermes_key_id or "",
            )
        except IdempotencyConflict as exc:
            raise HTTPException(status_code=409, detail=str(exc)) from exc

        if ingest_result.duplicate:
            response.status_code = status.HTTP_200_OK
            return _receipt(ingest_result.record, duplicate=True)

        if event.event_type not in active_settings.sink_event_types:
            store.mark_sink_result(str(event.event_id), status="ignored")
        elif event.data_classification is DataClassification.PHI:
            store.mark_sink_result(str(event.event_id), status="blocked_phi")
        elif event.notification is None:
            store.mark_sink_result(str(event.event_id), status="no_notification")
        elif notion_sink is None:
            store.mark_sink_result(str(event.event_id), status="not_configured")
        else:
            try:
                resource_id = notion_sink.publish(event)
                store.mark_sink_result(str(event.event_id), status="delivered", resource_id=resource_id)
            except NotionSinkError as exc:
                store.mark_sink_result(str(event.event_id), status="failed", error=str(exc))
                LOGGER.warning("Notion sink failed event_id=%s event_type=%s", event.event_id, event.event_type)

        stored = store.get(str(event.event_id))
        if stored is None:
            raise HTTPException(status_code=500, detail="Event persistence failure")
        return _receipt(stored, duplicate=False)

    @app.get("/v1/hermes/events", dependencies=[Depends(require_admin)])
    def list_events(limit: int = 50) -> list[dict[str, Any]]:
        return [_public_record(record) for record in store.list_recent(limit)]

    @app.get("/v1/hermes/events/{event_id}", dependencies=[Depends(require_admin)])
    def get_event(event_id: str) -> dict[str, Any]:
        record = store.get(event_id)
        if record is None:
            raise HTTPException(status_code=404, detail="Event not found")
        return _public_record(record)

    @app.post("/v1/hermes/events/{event_id}/retry", dependencies=[Depends(require_admin)])
    def retry_event(event_id: str) -> dict[str, Any]:
        record = store.get(event_id)
        if record is None:
            raise HTTPException(status_code=404, detail="Event not found")
        event = HermesEvent.model_validate(record["envelope"])
        if notion_sink is None:
            raise HTTPException(status_code=409, detail="Notion sink is not configured")
        if event.data_classification is DataClassification.PHI:
            raise HTTPException(status_code=409, detail="PHI events cannot be forwarded to Notion")
        if event.notification is None:
            raise HTTPException(status_code=409, detail="Event has no coordination notification")
        try:
            resource_id = notion_sink.publish(event)
            store.mark_sink_result(event_id, status="delivered", resource_id=resource_id)
        except NotionSinkError as exc:
            store.mark_sink_result(event_id, status="failed", error=str(exc))
            raise HTTPException(status_code=502, detail="Notion delivery failed") from exc
        return _public_record(store.get(event_id) or record)

    @app.get("/v1/hermes/stats", dependencies=[Depends(require_admin)])
    def stats() -> dict[str, Any]:
        return store.stats()

    @app.exception_handler(Exception)
    async def unhandled_exception(_: Request, exc: Exception):
        LOGGER.exception("Unhandled Hermes bridge error", exc_info=exc)
        return JSONResponse(status_code=500, content={"detail": "Internal server error"})

    return app


def _receipt(record: dict[str, Any], *, duplicate: bool) -> EventReceipt:
    return EventReceipt(
        event_id=record["event_id"], accepted=True, duplicate=duplicate,
        sink_status=record["sink_status"], received_at=record["received_at"]
    )


def _public_record(record: dict[str, Any]) -> dict[str, Any]:
    keys = (
        "event_id", "idempotency_key", "event_type", "source_service", "classification",
        "occurred_at", "received_at", "payload_ref", "sink_status", "sink_attempts",
        "sink_last_error", "sink_resource_id", "envelope"
    )
    return {key: record[key] for key in keys}
