"""Radiology reasoning schemas — the machine-readable contract (spec).
Hermes validates every gateway response against these; the model NEVER defines its own shape.
Likelihood and urgency are SEPARATE dimensions. Structured JSON output required.
"""
from typing import Optional, List, Dict, Any
from pydantic import BaseModel, Field, field_validator


class Finding(BaseModel):
    finding: str
    certainty: Optional[str] = None          # high | moderate | low
    severity: Optional[str] = None            # normal | abnormal | critical
    score: Optional[float] = None


class RadiologyReasoningInput(BaseModel):
    task: str = Field(default="radiology_reasoning")
    modality: str                             # DX | MG | US | DXA | CT | MR
    body_region: str
    indication: Optional[str] = None
    structured_findings: List[Finding] = Field(default_factory=list)   # from imaging model
    prior_findings: Optional[List[Dict[str, Any]]] = None
    relevant_labs: Optional[Dict[str, float]] = None
    meds_history: Optional[Dict[str, Any]] = None
    evidence_refs: Optional[List[str]] = None
    patient_ref: Optional[str] = None         # opaque; NO MRN/name/DOB (PHI policy)

    @field_validator("structured_findings")
    @classmethod
    def _has_findings(cls, v):
        # The imaging (visual) model must populate findings BEFORE the reasoning model runs.
        if not v:
            raise ValueError("structured_findings empty - visual model must run first; "
                             "never send raw pixels to a text-only reasoning model")
        return v


class Interpretation(BaseModel):
    status: str                              # normal | abnormal | indeterminate
    summary: str


class DifferentialEntry(BaseModel):
    rank: int
    condition: str
    relative_likelihood: str                 # high | moderate | low
    supporting_findings: List[str] = Field(default_factory=list)
    contradicting_findings: List[str] = Field(default_factory=list)
    missing_information: List[str] = Field(default_factory=list)


class MustNotMissItem(BaseModel):
    condition: str
    urgency: str                             # urgent | critical | expedited
    reason: str


class RadiologyReasoningOutput(BaseModel):
    interpretation: Interpretation
    differential: List[DifferentialEntry] = Field(default_factory=list)
    must_not_miss: List[MustNotMissItem] = Field(default_factory=list)
    recommendations: List[str] = Field(default_factory=list)
    uncertainty: List[str] = Field(default_factory=list)
    requires_provider_review: bool = True
    model: Dict[str, Any] = Field(default_factory=dict)

    @field_validator("differential")
    @classmethod
    def _ranked(cls, v):
        ranks = [d.rank for d in v]
        if ranks != sorted(ranks):
            raise ValueError("differential must be ranked (highest relative likelihood first)")
        return v
