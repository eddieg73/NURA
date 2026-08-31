from __future__ import annotations

import re
from datetime import datetime
from enum import Enum
from typing import Any, Literal
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field, HttpUrl, model_validator


class DataClassification(str, Enum):
    PUBLIC = "PUBLIC"
    INTERNAL = "INTERNAL"
    CONFIDENTIAL = "CONFIDENTIAL"
    PHI = "PHI"


class Severity(str, Enum):
    INFO = "info"
    WARNING = "warning"
    ERROR = "error"
    CRITICAL = "critical"


class CoordinationNotification(BaseModel):
    model_config = ConfigDict(extra="forbid", str_strip_whitespace=True)

    work_item: str = Field(min_length=3, max_length=300)
    summary: str = Field(min_length=1, max_length=1800)
    lane: Literal["Platform/Engineering", "CRM/Revenue", "Clinical", "Infra"] = "Platform/Engineering"
    priority: Literal["P1", "P2", "P3", "P4"] = "P2"
    status: Literal["Assigned", "In Progress", "Needs Review", "Approved", "Blocked", "Done"] = "Needs Review"
    work_type: Literal["Build", "Review", "Decision", "Bug", "Ops"] = "Review"
    owner: Literal["Hermes", "ChatGPT", "Eddie"] = "Hermes"
    reviewer: Literal["Hermes", "ChatGPT", "Eddie"] = "ChatGPT"
    link: HttpUrl | None = None
    target_page_id: str | None = Field(default=None, pattern=r"^[0-9a-fA-F-]{32,36}$")


class HermesEvent(BaseModel):
    model_config = ConfigDict(extra="forbid", str_strip_whitespace=True)

    spec_version: Literal["1.0"]
    event_id: UUID
    event_type: str = Field(min_length=3, max_length=160, pattern=r"^[a-z0-9][a-z0-9._-]+$")
    source_service: str = Field(min_length=2, max_length=100, pattern=r"^[A-Za-z0-9][A-Za-z0-9._-]+$")
    tenant_id: str | None = Field(default=None, max_length=128)
    patient_ref: str | None = Field(default=None, max_length=128)
    correlation_id: str | None = Field(default=None, max_length=128)
    causation_id: str | None = Field(default=None, max_length=128)
    idempotency_key: str = Field(min_length=16, max_length=128)
    occurred_at: datetime
    data_classification: DataClassification
    payload_ref: str | None = Field(default=None, max_length=2048)
    payload_sha256: str | None = Field(default=None, pattern=r"^[0-9a-fA-F]{64}$")
    provenance: dict[str, Any] = Field(default_factory=dict)
    notification: CoordinationNotification | None = None
    severity: Severity = Severity.INFO

    @model_validator(mode="after")
    def enforce_reference_only_phi(self) -> "HermesEvent":
        if self.occurred_at.tzinfo is None:
            raise ValueError("occurred_at must include a timezone")
        if self.payload_ref and not self.payload_sha256:
            raise ValueError("payload_sha256 is required when payload_ref is present")
        if self.data_classification is DataClassification.PHI:
            if self.notification is not None:
                raise ValueError("PHI events may not include notification text or direct payloads")
            if not self.payload_ref or not self.payload_sha256:
                raise ValueError("PHI events require payload_ref and payload_sha256")
        if self.payload_ref and not re.match(r"^(s3|b2|https)://", self.payload_ref):
            raise ValueError("payload_ref must use s3://, b2://, or https://")
        return self


class EventReceipt(BaseModel):
    event_id: str
    accepted: bool
    duplicate: bool
    sink_status: str
    received_at: str
