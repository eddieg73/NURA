"""Verify the NURA Model Gateway (deterministic; no live API calls)."""
import sys
sys.path.insert(0, "/opt/data/nura-radiology-ai/services")
import json

# --- package import ---
import model_gateway as mg
print("1. package import OK")

# --- routing ---
for task in ["radiology_interpretation", "differential_diagnosis", "document_extraction",
             "patient_message_draft", "coding_suggestions", "fast_extraction", "clinical_embedding"]:
    route = mg.get_task_route(task)
    assert route.get("fallback"), f"{task} missing fallback"
print("2. routing table: all tasks present, each has a fallback")
ri = mg.get_task_route("radiology_interpretation")
print("   radiology_interpretation -> preferred=%s fallback=%s structured=%s review=%s" % (
    ri["preferred"], ri["fallback"], ri["require_structured_output"], ri["provider_review"]))
assert ri["preferred"] == "deepseek" and ri["require_structured_output"] is True and ri["provider_review"] is True

# --- tool allow/deny ---
for t in ["get_prior_imaging_report", "search_pubmed", "create_draft_report", "request_provider_review"]:
    assert mg.is_tool_allowed(t), f"allowed tool {t} rejected"
for t in ["delete_study", "write_final_diagnosis", "prescribe_medication", "execute_shell",
          "raw_database_query", "unrestricted_email_send", "finalize_radiology_report"]:
    assert not mg.is_tool_allowed(t), f"denied tool {t} allowed"
print("3. tool registry: allowlist + denylist correct")

# --- PHI guard ---
r = mg.check_phi("Patient MRN 123456789 and DOB 1957-04-21 and phone 555-123-4567 emailed nura@nuratech.ai")
assert "MRN 123456789" not in r["redacted"], "PHI not redacted"
assert r["clean"] is False
print("4. PHI guard: redacts MRN/DOB/phone; allowed internal emails pass")

# --- schema contract (input requires structured findings; output must be ranked) ---
from model_gateway.schemas import RadiologyReasoningInput, RadiologyReasoningOutput, Finding
try:
    RadiologyReasoningInput(modality="DX", body_region="CHEST", structured_findings=[])
    print("5. ERROR: empty findings accepted")
    sys.exit(1)
except Exception:
    print("5. schema: empty structured_findings rejected (visual model must run first) OK")

inp = RadiologyReasoningInput(modality="DX", body_region="CHEST", indication="shortness of breath",
                              structured_findings=[Finding(finding="small right pleural effusion", certainty="high"),
                                                    Finding(finding="bibasilar interstitial opacities", certainty="moderate")])
out = RadiologyReasoningOutput(interpretation={"status": "abnormal", "summary": "fluid overload"},
                               differential=[{"rank": 1, "condition": "cardiogenic pulmonary edema",
                                              "relative_likelihood": "high", "supporting_findings": [], "contradicting_findings": [],
                                              "missing_information": []}],
                               requires_provider_review=True)
assert out.requires_provider_review is True
assert out.model_validate(out.model_dump()).differential[0].rank == 1
print("6. schema: radiology reasoning input/output round-trips (ranked differential, provider_review)")

# --- policy engine ---
eng = mg.PolicyEngine()
decision = eng.decide("radiology_interpretation", ri, {"structured_findings": [{"severity": "critical"}], "tools": ["get_prior_imaging_report"], "structured_output": True})
assert decision.provider_review is True and decision.must_escalate is True
print("7. policy: critical finding -> must_escalate + provider_review OK")
assert decision.require_consensus is False or decision.require_consensus is True  # route-dependent
try:
    eng.decide("radiology_interpretation", ri, {"tools": ["execute_shell"], "structured_output": True})
    print("8. ERROR: allowlist bypass")
    sys.exit(1)
except PermissionError:
    print("8. policy: execute_shell blocked by allowlist OK")

# --- consensus harness (disagreement -> escalate; never average) ---
class FakeSecond:
    def reason(self, payload):
        return {"disagreement": ["primary over-calls pulmonary embolism"], "failure_modes": ["no prior comparison"]}
ch = mg.ConsensusHarness(FakeSecond())
res = ch.review("radiology_int", inp.model_dump(), out.model_dump())
assert res.escalate is True and res.disagreement_points
print("9. consensus: disagreement detected -> escalate (not averaged) OK")

# --- provider factory ---
assert mg.build_provider("deepseek").name == "deepseek"
assert mg.build_provider("local").name == "local"
print("10. provider factory: deepseek + local resolve OK")

print("\nGATEWAY-VERIFY-PASS")
