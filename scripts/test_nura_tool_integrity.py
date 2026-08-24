#!/usr/bin/env python3
"""Fixture test: structured-output integrity for nura-clinical-synthesis.

Proves the AUTHORITATIVE facts block (tool_lab_facts) is a faithful, literal
copy of the tool-derived lab data — byte-identical values/units/flags — and
that it is IMMUNE to model paraphrase. We monkeypatch local_llm to return a
narrative that just tried to alter a value; the facts block must still be exact.

Run: python3 test_nura_tool_integrity.py   (no live model needed)
"""
import json, sys, importlib.util
_PATH = "/opt/data/scripts/nura-clinical-synthesis.py"
_spec = importlib.util.spec_from_file_location("nura_clinical_synthesis", _PATH)
ncs = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(ncs)

def test_pure_facts_are_literal():
    labs = {"WBC": 12.4, "Hgb": 11.2, "Glucose": 90, "Cr": "unable-to-repeat"}
    facts = {f["test"]: f for f in ncs.tool_lab_facts(labs)}
    # exact numeric + unit preserved
    assert facts["WBC"]["value"] == 12.4, facts["WBC"]
    assert facts["WBC"]["unit"] == "10^9/L"
    assert facts["WBC"]["flag"] == "HIGH"      # 12.4 > 11.0
    assert facts["Hgb"]["value"] == 11.2 and facts["Hgb"]["unit"] == "g/dL"
    assert facts["Glucose"]["value"] == 90 and facts["Glucose"]["flag"] is None
    # non-numeric lab carried as literal text, no flag
    assert facts["Cr"]["value"] == "unable-to-repeat" and facts["Cr"]["flag"] is None
    return True

def test_facts_immune_to_model_paraphrase():
    # Simulate an LLM that ignores the instruction and rewrites WBC.
    bad = {"problem_list": ["leukocytosis (WBC ~11.9)"],
           "impression": "WBC looks around 11.9, borderline.",
           "differential": [], "data_gaps": [], "recommended_next_steps": []}
    ncs.local_llm = lambda prompt, model="med42", timeout=1500: json.dumps(bad)
    case = {"patient": {"age": 54, "sex": "M", "pmh": ["HTN"]},
            "radiology": [], "labs": {"WBC": 12.4, "Hgb": 11.2}, "consultations": [],
            "soap": {"s": "x", "o": "x", "a": "x", "p": "x"}}
    out = ncs.synthesize(case)
    f = {x["test"]: x for x in out["lab_facts"]}
    # The facts block must be the EXACT tool data, not the model's 11.9.
    assert f["WBC"]["value"] == 12.4, f"FACTS ALTERED: {f['WBC']}"
    assert f["WBC"]["unit"] == "10^9/L"
    assert f["Hgb"]["value"] == 11.2
    assert out["lab_integrity"]["verified"] is True
    assert out["lab_integrity"]["source"] == "tool"
    # flags derive from the pure facts, unchanged by model output
    assert out["lab_flags"] and any("WBC 12.4" in x for x in out["lab_flags"])
    return True

def test_flag_labs_single_source():
    assert ncs.flag_labs({"WBC": 12.4}) == ["WBC 12.4 10^9/L — HIGH (ref 4.0-11.0)"]
    assert ncs.flag_labs({"Glucose": 90}) == []
    return True

if __name__ == "__main__":
    tests = [test_pure_facts_are_literal, test_facts_immune_to_model_paraphrase, test_flag_labs_single_source]
    passed = 0
    for t in tests:
        r = t()
        print(f"  PASS  {t.__name__}")
        assert r
        passed += 1
    print(f"\nRESULT: {passed}/{len(tests)} passed — structured-output integrity verified.")
    sys.exit(0)
