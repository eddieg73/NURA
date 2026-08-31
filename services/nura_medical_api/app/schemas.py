from __future__ import annotations

from datetime import datetime
from typing import Literal

from pydantic import BaseModel, EmailStr, Field, field_validator


Role = Literal["clinician", "reviewer", "admin"]
Operation = Literal["scribe", "dx", "synthesis"]
ReviewStatus = Literal["draft", "approved", "rejected"]


class RegisterRequest(BaseModel):
    email: EmailStr
    password: str = Field(min_length=12, max_length=128)
    full_name: str = Field(min_length=2, max_length=160)
    organization_name: str = Field(min_length=2, max_length=160)


class LoginRequest(BaseModel):
    email: EmailStr
    password: str = Field(min_length=1, max_length=128)
    device_label: str | None = Field(default=None, max_length=160)


class RefreshRequest(BaseModel):
    refresh_token: str = Field(min_length=32, max_length=512)
    device_label: str | None = Field(default=None, max_length=160)


class LogoutRequest(BaseModel):
    refresh_token: str = Field(min_length=32, max_length=512)


class UserOut(BaseModel):
    id: str
    organization_id: str
    email: EmailStr
    full_name: str
    role: Role
    active: bool


class TokenPair(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"
    expires_in: int
    user: UserOut


class DifferentialItem(BaseModel):
    label: str
    support: str
    confidence: Literal["low", "medium", "high"] = "low"


class ProvenanceItem(BaseModel):
    source_type: str
    source_id: str | None = None
    note: str | None = None


class ClinicalOutput(BaseModel):
    source_facts: list[str] = Field(default_factory=list)
    interpretation: str
    differential: list[DifferentialItem] = Field(default_factory=list)
    dangerous_alternatives: list[str] = Field(default_factory=list)
    red_flags: list[str] = Field(default_factory=list)
    missing_data: list[str] = Field(default_factory=list)
    recommended_next_step: str
    urgency: Literal["routine", "urgent", "emergent", "undetermined"] = "undetermined"
    confidence: Literal["low", "medium", "high"] = "low"
    evidence_as_of: str
    limitations: list[str] = Field(default_factory=list)
    provenance: list[ProvenanceItem] = Field(default_factory=list)


class ClinicalDraftRequest(BaseModel):
    operation: Operation
    case_text: str = Field(min_length=1, max_length=30_000)
    patient_reference: str | None = Field(default=None, max_length=160)
    consent_attested: bool

    @field_validator("case_text")
    @classmethod
    def strip_case_text(cls, value: str) -> str:
        value = value.strip()
        if not value:
            raise ValueError("case_text must not be blank")
        return value


class ClinicalDraftOut(BaseModel):
    id: str
    encounter_id: str
    operation: Operation
    output: ClinicalOutput
    provider_name: str
    model_name: str | None
    status: ReviewStatus
    created_at: datetime
    reviewed_by: str | None = None
    reviewed_at: datetime | None = None
    review_comment: str | None = None
    provider_approval_required: bool = True


class ReviewRequest(BaseModel):
    status: Literal["approved", "rejected"]
    comment: str | None = Field(default=None, max_length=4_000)


class TaskCreate(BaseModel):
    title: str = Field(min_length=1, max_length=240)
    detail: str | None = Field(default=None, max_length=8_000)
    priority: Literal["low", "normal", "high", "urgent"] = "normal"


class TaskUpdate(BaseModel):
    status: Literal["open", "in_progress", "completed", "cancelled"] | None = None
    priority: Literal["low", "normal", "high", "urgent"] | None = None
    title: str | None = Field(default=None, min_length=1, max_length=240)
    detail: str | None = Field(default=None, max_length=8_000)


class TaskOut(BaseModel):
    id: str
    title: str
    detail: str | None
    status: str
    priority: str
    created_at: datetime
    completed_at: datetime | None


class LegalConfigOut(BaseModel):
    privacy_policy_url: str
    terms_url: str
    support_url: str
    clinical_disclaimer: str
    account_deletion_available: bool = True


class AccountDeleteRequest(BaseModel):
    password: str = Field(min_length=1, max_length=128)
    confirmation: Literal["DELETE"]
