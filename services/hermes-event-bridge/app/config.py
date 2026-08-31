from __future__ import annotations

import os
from dataclasses import dataclass
from pathlib import Path


def _as_bool(value: str | None, default: bool = False) -> bool:
    if value is None:
        return default
    return value.strip().lower() in {"1", "true", "yes", "on"}


def _as_csv(value: str | None) -> frozenset[str]:
    if not value:
        return frozenset()
    return frozenset(item.strip() for item in value.split(",") if item.strip())


@dataclass(frozen=True, slots=True)
class Settings:
    webhook_secret: str
    webhook_key_id: str
    admin_bearer_token: str
    db_path: Path
    max_body_bytes: int = 262_144
    max_age_seconds: int = 300
    require_https: bool = True
    enable_docs: bool = False
    allowed_source_services: frozenset[str] = frozenset()
    notion_enabled: bool = False
    notion_token: str | None = None
    notion_coordination_data_source_id: str | None = None
    notion_api_version: str = "2026-03-11"
    notion_timeout_seconds: float = 10.0
    sink_event_types: frozenset[str] = frozenset(
        {
            "nura.hermes.review.requested.v1",
            "nura.hermes.status.updated.v1",
            "nura.hermes.alert.raised.v1",
            "nura.hermes.artifact.ready.v1",
        }
    )

    @classmethod
    def from_env(cls) -> "Settings":
        settings = cls(
            webhook_secret=os.getenv("HERMES_WEBHOOK_SECRET", ""),
            webhook_key_id=os.getenv("HERMES_WEBHOOK_KEY_ID", "primary"),
            admin_bearer_token=os.getenv("ADMIN_BEARER_TOKEN", ""),
            db_path=Path(os.getenv("EVENT_DB_PATH", "/data/hermes-events.sqlite3")),
            max_body_bytes=int(os.getenv("MAX_BODY_BYTES", "262144")),
            max_age_seconds=int(os.getenv("WEBHOOK_MAX_AGE_SECONDS", "300")),
            require_https=_as_bool(os.getenv("REQUIRE_HTTPS"), True),
            enable_docs=_as_bool(os.getenv("ENABLE_DOCS"), False),
            allowed_source_services=_as_csv(os.getenv("ALLOWED_SOURCE_SERVICES")),
            notion_enabled=_as_bool(os.getenv("NOTION_ENABLED"), False),
            notion_token=os.getenv("NOTION_TOKEN") or None,
            notion_coordination_data_source_id=(
                os.getenv("NOTION_COORDINATION_DATA_SOURCE_ID") or None
            ),
            notion_api_version=os.getenv("NOTION_API_VERSION", "2026-03-11"),
            notion_timeout_seconds=float(os.getenv("NOTION_TIMEOUT_SECONDS", "10")),
            sink_event_types=(
                _as_csv(os.getenv("SINK_EVENT_TYPES"))
                or cls.__dataclass_fields__["sink_event_types"].default
            ),
        )
        settings.validate()
        return settings

    def validate(self) -> None:
        if len(self.webhook_secret) < 32:
            raise ValueError("HERMES_WEBHOOK_SECRET must be at least 32 characters")
        if len(self.admin_bearer_token) < 32:
            raise ValueError("ADMIN_BEARER_TOKEN must be at least 32 characters")
        if self.max_body_bytes < 1024:
            raise ValueError("MAX_BODY_BYTES must be at least 1024")
        if not 30 <= self.max_age_seconds <= 3600:
            raise ValueError("WEBHOOK_MAX_AGE_SECONDS must be between 30 and 3600")
        if self.notion_enabled:
            if not self.notion_token:
                raise ValueError("NOTION_TOKEN is required when NOTION_ENABLED=true")
            if not self.notion_coordination_data_source_id:
                raise ValueError(
                    "NOTION_COORDINATION_DATA_SOURCE_ID is required when NOTION_ENABLED=true"
                )
