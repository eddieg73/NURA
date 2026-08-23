"""Policy engine — enforces provider review, consensus for high-risk, and safe tool calls.
Independent of the model: this is Hermes' safety layer, not a model judgment."""
from dataclasses import dataclass, field
from typing import List, Optional, Dict, Any
from .tool_registry import assert_tool_allowed
from .phi_policy import PHIGuard


@dataclass
class PolicyDecision:
    route: Dict[str, Any]
    must_escalate: bool
    require_consensus: bool
    provider_review: bool
    reason: List[str] = field(default_factory=list)
    bypass: bool = False


class PolicyEngine:
    def __init__(self, consensus_engine=None, phi_guard=None):
        self.phi = phi_guard or PHIGuard()
        self.consensus = consensus_engine  # ConsensusHarness

    def decide(self, task: str, route: dict, input_payload: dict) -> PolicyDecision:
        reasons = []
        # 1. Tool safety: any tool the model will call must be allowlisted.
        for tool in input_payload.get("tools", []):
            try:
                assert_tool_allowed(tool)
            except PermissionError as e:
                reasons.append(str(e))
                return PolicyDecision(route, True, False, True, reasons)

        # 2. Structured output requirement.
        if route.get("require_structured_output") and not input_payload.get("structured_output", True):
            reasons.append("task requires structured output")

        # 3. Clinical safety: provider review / consensus, from the routing table.
        high_risk = bool(input_payload.get("high_risk") or
                         any(f.get("severity") == "critical" for f in input_payload.get("structured_findings", [])))
        require_consensus = bool(route.get("consensus_required_if_high_risk")) and high_risk
        provider_review = bool(route.get("provider_review", True))
        if high_risk:
            reasons.append("high-risk/critical finding detected")

        # 4. PHI: no patient identifiers on the external wire.
        # (checked at the provider boundary by phi_policy; here we pre-flag)
        if input_payload.get("phi_allowed") is False:
            reasons.append("PHI not allowed for this task/route")

        return PolicyDecision(route=route,
                              must_escalate=high_risk,
                              require_consensus=require_consensus,
                              provider_review=provider_review,
                              reason=reasons)
