"""Model routing table (spec: model routing table). Route by TASK, not by model availability.
Each task: preferred provider, fallback, structured output requirement, provider review,
consensus-if-high-risk, PHI constraint."""
import yaml, os

DEFAULT = {
    "radiology_interpretation": {
        "preferred": "deepseek", "fallback": "local-medical-llm",
        "require_structured_output": True, "provider_review": True,
        "consensus_required_if_high_risk": False,
    },
    "differential_diagnosis": {
        "preferred": "deepseek", "fallback": "openai",
        "require_structured_output": True, "provider_review": True,
        "consensus_required_if_high_risk": True,
        "provide_critical-finding_alert": True,
    },
    "document_extraction": {
        "preferred": "local", "fallback": "deepseek",
        "require_structured_output": True, "provider_review": False,
    },
    "patient_message_draft": {
        "preferred": "deepseek", "fallback": "local",
        "require_structured_output": True, "provider_review": True,
        "provider_approval_required": True,
    },
    "coding_suggestions": {
        "preferred": "deepseek", "fallback": "openai",
        "require_structured_output": False, "provider_review": False,
        "provider_or_coder_review": True,
    },
    "evidence_synthesis": {
        "preferred": "deepseek", "fallback": "local-medical-llm",
        "require_structured_output": True, "provider_review": False,
    },
    "fast_extraction": {
        "preferred": "local", "fallback": "deepseek",
        "require_structured_output": True, "provider_review": False,
    },
    "clinical_embedding": {
        "preferred": "local-encoder", "fallback": "local",
        "require_structured_output": False, "provider_review": False,
    },
}

def _load():
    # Allow a file override; fall back to the in-code defaults (deterministic, no secret).
    path = os.path.join(os.path.dirname(__file__), "routing.yaml")
    if os.path.exists(path):
        with open(path) as f:
            table = yaml.safe_load(f) or {}
        return {**DEFAULT, **table}
    return DEFAULT

routing_table = _load()

def get_task_route(task: str) -> dict:
    if task not in routing_table:
        raise KeyError(f"no route for task '{task}'; add it to the routing table")
    return dict(routing_table[task])
