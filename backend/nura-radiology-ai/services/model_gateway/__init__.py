"""NURA Model Gateway — catalog + reason() entrypoint (Hermes calls this, never a vendor API).

Hermes = nervous system (workflow/tool-control/events/safety/audit), model-agnostic.
DeepSeek = interchangeable reasoning cortex; imaging models = visual cortex that emit
structured findings FIRST. reason() routes by task, validates schema, enforces PHI/policy,
retries/falls back, audits every call.
"""
from .router import GatewayRouter, routing_table, RouteDecision, build_default_router
from .routing import get_task_route
from .schemas import (
    RadiologyReasoningInput, RadiologyReasoningOutput, Interpretation,
    DifferentialEntry, MustNotMissItem,
)
from .tool_registry import TOOL_ALLOWLIST, TOOL_DENYLIST, is_tool_allowed
from .phi_policy import PHIGuard, check_phi
from .policy import PolicyEngine, PolicyDecision
from .consensus import ConsensusHarness, ConsensusResult
from .retry import with_retry
from .telemetry import Telemetry
from .audit import AuditLog

def build_gateway(**kwargs):
    """Factory: dev default returns a router wired to a schema-validating stub provider."""
    from .router import build_default_router
    return build_default_router()

__all__ = [
    "GatewayRouter", "routing_table", "RouteDecision",
    "RadiologyReasoningInput", "RadiologyReasoningOutput", "Interpretation",
    "DifferentialEntry", "MustNotMissItem",
    "TOOL_ALLOWLIST", "TOOL_DENYLIST", "is_tool_allowed",
    "PHIGuard", "check_phi", "PolicyEngine", "PolicyDecision",
    "with_retry", "Telemetry", "AuditLog", "build_gateway",
]
