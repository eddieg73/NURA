"""Consensus harness (spec). For high-risk cases, a SECOND model reviews the primary's output
to detect disagreement, unsupported assumptions, missing information, and failure modes.
Do NOT average diagnoses — flag disagreement for provider escalation."""
from dataclasses import dataclass, field
from typing import List, Optional, Dict, Any


@dataclass
class ConsensusResult:
    agreement: bool
    disagreement_points: List[str] = field(default_factory=list)
    unsupported_assumptions: List[str] = field(default_factory=list)
    missing_information: List[str] = field(default_factory=list)
    failure_modes: List[str] = field(default_factory=list)
    escalate: bool = False


class ConsensusHarness:
    """Primary provider produces the draft; a SECOND provider reviews it. Not averaging."""

    def __init__(self, second_provider, schemas_module=None):
        self.second = second_provider
        self.schemas = schemas_module

    def review(self, task: str, input_payload: dict, primary_output: dict) -> ConsensusResult:
        reframe = {
            "task": f"critical_review_{task}",
            "primary_output": primary_output,
            "input": input_payload,
            "question": ("Identify only: (1) disagreement with the primary, (2) unsupported "
                         "assumptions, (3) missing information, (4) possible failure modes. "
                         "Do not propose a different diagnosis to average."),
        }
        resp = self.second.reason(reframe)  # returns dict with those four lists
        reason = {
            "disagreement": list((resp or {}).get("disagreement", [])),
            "unsupported": list((resp or {}).get("unsupported_assumptions", [])),
            "missing": list((resp or {}).get("missing_information", [])),
            "failure_modes": list((resp or {}).get("failure_modes", [])),
        }
        escalate = bool(reason["disagreement"] or reason["failure_modes"])
        return ConsensusResult(
            agreement=not escalate,
            disagreement_points=reason["disagreement"],
            unsupported_assumptions=reason["unsupported"],
            missing_information=reason["missing"],
            failure_modes=reason["failure_modes"],
            escalate=escalate,
        )
