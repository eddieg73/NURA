from __future__ import annotations

import hashlib
import json
import sqlite3
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from .models import HermesEvent


class IdempotencyConflict(RuntimeError):
    pass


@dataclass(frozen=True, slots=True)
class IngestResult:
    record: dict[str, Any]
    duplicate: bool


class EventStore:
    def __init__(self, db_path: Path):
        self.db_path = db_path

    def _connect(self) -> sqlite3.Connection:
        connection = sqlite3.connect(self.db_path, timeout=10)
        connection.row_factory = sqlite3.Row
        connection.execute("PRAGMA journal_mode=WAL")
        connection.execute("PRAGMA foreign_keys=ON")
        connection.execute("PRAGMA busy_timeout=5000")
        return connection

    def initialize(self) -> None:
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        with self._connect() as connection:
            connection.executescript(
                """
                CREATE TABLE IF NOT EXISTS events (
                    event_id TEXT PRIMARY KEY,
                    idempotency_key TEXT NOT NULL UNIQUE,
                    body_sha256 TEXT NOT NULL,
                    event_type TEXT NOT NULL,
                    source_service TEXT NOT NULL,
                    tenant_id TEXT,
                    correlation_id TEXT,
                    classification TEXT NOT NULL,
                    occurred_at TEXT NOT NULL,
                    received_at TEXT NOT NULL,
                    payload_ref TEXT,
                    payload_sha256 TEXT,
                    envelope_json TEXT NOT NULL,
                    remote_addr TEXT,
                    signature_key_id TEXT NOT NULL,
                    sink_status TEXT NOT NULL DEFAULT 'pending',
                    sink_attempts INTEGER NOT NULL DEFAULT 0,
                    sink_last_error TEXT,
                    sink_resource_id TEXT
                );
                CREATE INDEX IF NOT EXISTS idx_events_received_at ON events(received_at DESC);
                CREATE INDEX IF NOT EXISTS idx_events_type ON events(event_type, received_at DESC);
                CREATE INDEX IF NOT EXISTS idx_events_sink_status ON events(sink_status, received_at DESC);
                """
            )

    def ping(self) -> bool:
        with self._connect() as connection:
            return connection.execute("SELECT 1").fetchone()[0] == 1

    def ingest(self, *, event: HermesEvent, raw_body: bytes, remote_addr: str | None, signature_key_id: str) -> IngestResult:
        received_at = datetime.now(timezone.utc).isoformat()
        body_sha256 = hashlib.sha256(raw_body).hexdigest()
        envelope_json = json.dumps(event.model_dump(mode="json"), separators=(",", ":"))
        event_id = str(event.event_id)
        try:
            with self._connect() as connection:
                connection.execute(
                    """
                    INSERT INTO events (
                        event_id, idempotency_key, body_sha256, event_type,
                        source_service, tenant_id, correlation_id, classification,
                        occurred_at, received_at, payload_ref, payload_sha256,
                        envelope_json, remote_addr, signature_key_id, sink_status
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                    """,
                    (
                        event_id, event.idempotency_key, body_sha256, event.event_type,
                        event.source_service, event.tenant_id, event.correlation_id,
                        event.data_classification.value, event.occurred_at.isoformat(),
                        received_at, event.payload_ref, event.payload_sha256,
                        envelope_json, remote_addr, signature_key_id, "pending",
                    ),
                )
        except sqlite3.IntegrityError:
            existing = self.get(event_id) or self.get_by_idempotency_key(event.idempotency_key)
            if existing is None:
                raise
            if existing["body_sha256"] != body_sha256:
                raise IdempotencyConflict("Event ID or idempotency key already exists with different content")
            return IngestResult(record=existing, duplicate=True)
        record = self.get(event_id)
        if record is None:
            raise RuntimeError("Accepted event could not be read back")
        return IngestResult(record=record, duplicate=False)

    def get(self, event_id: str) -> dict[str, Any] | None:
        with self._connect() as connection:
            row = connection.execute("SELECT * FROM events WHERE event_id = ?", (event_id,)).fetchone()
        return self._row_to_dict(row)

    def get_by_idempotency_key(self, key: str) -> dict[str, Any] | None:
        with self._connect() as connection:
            row = connection.execute("SELECT * FROM events WHERE idempotency_key = ?", (key,)).fetchone()
        return self._row_to_dict(row)

    def list_recent(self, limit: int = 50) -> list[dict[str, Any]]:
        safe_limit = max(1, min(limit, 200))
        with self._connect() as connection:
            rows = connection.execute("SELECT * FROM events ORDER BY received_at DESC LIMIT ?", (safe_limit,)).fetchall()
        return [self._row_to_dict(row) for row in rows if row is not None]

    def mark_sink_result(self, event_id: str, *, status: str, resource_id: str | None = None, error: str | None = None) -> None:
        safe_error = error[:1000] if error else None
        with self._connect() as connection:
            connection.execute(
                """
                UPDATE events SET sink_status = ?, sink_attempts = sink_attempts + 1,
                    sink_last_error = ?, sink_resource_id = COALESCE(?, sink_resource_id)
                WHERE event_id = ?
                """,
                (status, safe_error, resource_id, event_id),
            )

    def stats(self) -> dict[str, Any]:
        with self._connect() as connection:
            total = connection.execute("SELECT COUNT(*) FROM events").fetchone()[0]
            rows = connection.execute("SELECT sink_status, COUNT(*) AS count FROM events GROUP BY sink_status").fetchall()
            latest = connection.execute("SELECT received_at FROM events ORDER BY received_at DESC LIMIT 1").fetchone()
        return {
            "total": total,
            "by_sink_status": {row["sink_status"]: row["count"] for row in rows},
            "latest_received_at": latest["received_at"] if latest else None,
        }

    @staticmethod
    def _row_to_dict(row: sqlite3.Row | None) -> dict[str, Any] | None:
        if row is None:
            return None
        result = dict(row)
        result["envelope"] = json.loads(result.pop("envelope_json"))
        return result
