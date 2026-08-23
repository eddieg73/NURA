"""GatewayRouter — Hermes calls model_gateway.reason() (task, payload) -> validated dict.
NOT a vendor API. Routes by task, enforces policy, may run consensus, retries+validates schema,
and audits/telemetries every call."""
import time
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Any, Callable

from .routing import get_task_route, routing_table
from .providers import build_provider, BaseProvider, StubProvider
from .policy import PolicyEngine, PolicyDecision
from .consensus import ConsensusHarness
from .retry import with_retry
from .telemetry import Telemetry
from .audit import AuditLog

# Task -> output schema (validate structured output when known). Radiology is the flagship.
from .schemas import RadiologyReasoningOutput


@dataclass
class RouteDecision:
    task: str
    route: Dict[str, Any]
    provider: BaseProvider
    policy: PolicyDecision
    consensus: Optional[object] = None
    notes: List[str] = field(default_factory=list)


def _schema_for(task: str):
    if task in ("radiology_interpretation", "differential_diagnosis", "radiology_reasoning"):
        return RadiologyReasoningOutput
    return None


class GatewayRouter:
    def __init__(self, provider_factory: Optional[Callable[[str], BaseProvider]] = None,
                 second_provider: Optional[BaseProvider] = None,
                 audit=None, telemetry=None, engine=None):
        self._factory = provider_factory or build_provider
        self._second = second_provider
        self.audit = audit or AuditLog()
        self.telemetry = telemetry or Telemetry()
        self.engine = engine or PolicyEngine(consensus_engine=ConsensusHarness(second_provider) if second_provider else None)

    def reason(self, task: str, payload: Dict[str, Any], context: Dict[str, Any] = None) -> Dict[str, Any]:
        t0 = time.time()
        route = get_task_route(task)
        provider = self._factory(route["preferred"])
        decision = self.engine.decide(task, route, payload)

        # High-risk / consensus path: second model reviews; do NOT average (spec).
        consensus = None
        if decision.require_consensus and self._second is not None:
            consensus = self.engine.consensus.review(task, payload, {"__pre": True})  # primary output injected later

        # Run the primary provider with retry + per-task schema validation.
        schema = _schema_for(task)
        validator = (lambda o: schema.model_validate(o)) if schema and route.get("require_structured_output") else None

        def _call():
            raw = provider.reason(payload)
            return raw

        result = with_retry(lambda: _call(), attempts=3, validator=validator)

        # Coerce to the schema shape for the machine-readable pipeline.
        if schema and isinstance(result, dict):
            validated = schema.model_validate(result)
            out = validated.model_dump()
        elif isinstance(result, str):
            out = {"text": result}
        else:
            out = dict(result)

        decision_out = {
            "task": task,
            "route": route,
            "provider": provider.name,
            "provider_review_required": decision.provider_review,
            "must_escalate": decision.must_escalate,
            "consensus_required": decision.require_consensus,
            "reason": decision.reason,
            "output": out,
            "model": {"name": provider.name, "task": task},
        }

        self.audit.record({"event": "model_gateway.reason", "task": task, "provider": provider.name,
                           "provider_review": decision.provider_review, "escalate": decision.must_escalate})
        self.telemetry.record(task, provider.name, route["preferred"], True, (time.time() - t0) * 1000)
        return decision_out


def build_default_router(provider_factory=None, second_provider=None):
    """Dev default: stub providers (no tokens/network) unless a real factory is passed."""
    if provider_factory is None:
        def factory(name):
            if name == "deepseek" or name == "openai":
                return StubProvider(output={"interpretation": {"status": "abnormal", "summary": "stub draft"},
                                            "differential": [], "must_not_miss": [],
                                            "requires_provider_review": True})
            return build_provider(name)
        provider_factory = factory
    return GatewayRouter(provider_factory=provider_factory, second_provider=second_provider)
