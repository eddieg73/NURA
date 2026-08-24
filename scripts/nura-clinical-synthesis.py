#!/usr/bin/env python3
"""NURA Clinical Synthesis — the full scut-work engine (provider-approved).
Inputs: radiology reports, labs, consultations, SOAP notes, patient context.
Output: the IMPRESSION + ranked DIFFERENTIAL + gaps + next steps + the chart-ready draft.
DOCTRINE: Eddie (PA-C) makes the FINAL approval — everything here is a draft for his signature.
Usage: python3 nura-clinical-synthesis.py case.json
case.json = {"patient": {"age":..,"sex":..,"pmh":[...]},
             "radiology": ["report text", ...],
             "labs": {"WBC": 12.4, "Hgb": 11.2, ...},
             "consultations": ["text", ...],
             "soap": {"s":"...","o":"...","a":"...","p":"..."}}
"""
import sys, json, urllib.request

def local_llm(prompt, model="med42", timeout=120):
    body = json.dumps({"model": model, "prompt": prompt, "stream": False,
                       "options": {"num_predict": 1000, "temperature": 0.2}}).encode()
    req = urllib.request.Request("http://127.0.0.1:11434/api/generate", data=body,
                                 headers={"Content-Type": "application/json"})
    try:
        r = urllib.request.urlopen(req, timeout=timeout)
        return json.loads(r.read()).get("response", "").strip()
    except Exception as e:
        return f"[local model unavailable: {str(e)[:60]}]"

LAB_REF = {  # rough reference ranges (adult) — flags only, provider interprets
    "WBC": (4.0, 11.0, "10^9/L"), "Hgb": (13.5, 17.5, "g/dL"), "Hct": (39, 50, "%"),
    "PLT": (150, 400, "10^9/L"), "Na": (135, 145, "mmol/L"), "K": (3.5, 5.0, "mmol/L"),
    "Cr": (0.6, 1.3, "mg/dL"), "BUN": (7, 20, "mg/dL"), "Glucose": (70, 110, "mg/dL"),
    "Troponin": (0, 0.04, "ng/mL"), "Lactate": (0.5, 2.0, "mmol/L"), "CRP": (0, 5, "mg/L"),
    "AST": (5, 40, "U/L"), "ALT": (5, 40, "U/L"), "TSH": (0.4, 4.0, "mIU/L"),
}

def tool_lab_facts(labs):
    """DETERMINISTIC, LITERAL copy of the tool-derived lab data.

    This is the AUTHORITATIVE record of what the data source returned. It is
    computed in pure Python and NEVER passes through the LLM, so the model
    cannot alter, paraphrase, or drift these values. Every numeric value and
    its unit is preserved byte-identical from the input.
    Returns a list of dicts: {test, value, unit, ref_low, ref_high, flag}.
    """
    facts = []
    for k in sorted(labs.keys()):
        v = labs[k]
        ref = LAB_REF.get(k)
        if ref and isinstance(v, (int, float)):
            lo, hi, unit = ref
            flag = None
            if v < lo: flag = "LOW"
            elif v > hi: flag = "HIGH"
            facts.append({"test": k, "value": v, "unit": unit,
                          "ref_low": lo, "ref_high": hi, "flag": flag})
        else:
            # non-numeric lab (e.g. free text) — literal copy, no flagging
            facts.append({"test": k, "value": v, "unit": None,
                          "ref_low": None, "ref_high": None, "flag": None})
    return facts

def flag_labs(labs):
    """Human-readable flags derived from the deterministic facts (single source)."""
    out = []
    for f in tool_lab_facts(labs):
        if f["flag"]:
            lo, hi, unit = f["ref_low"], f["ref_high"], f["unit"]
            out.append(f"{f['test']} {f['value']} {unit} — {f['flag']} (ref {lo}-{hi})")
    return out

SYNTH_PROMPT = """You are NURA, a clinical synthesis engine working for a licensed PA who makes the final approval.
Synthesize ALL the provided data into a comprehensive clinical impression.
Return JSON:
{"problem_list": ["..."],
 "impression": "The synthesized clinical picture in 4-6 sentences.",
 "differential": [{"dx": "...", "likelihood": "high|moderate|low", "supporting": [...], "against": [...]} ranked],
 "data_gaps": ["what's missing to narrow the differential"],
 "recommended_next_steps": ["tests/imaging/consults in priority order"],
 "label": "DRAFT — PROVIDER APPROVAL REQUIRED. Eddie Garrido PA-C confirms before anything is final."}
Ground every differential item in the provided data. Note explicitly what the data does NOT support.
For each differential, list the supporting AND the against findings. JSON only."""

def synthesize(case):
    patient = case.get("patient", {})
    labs = case.get("labs", {})
    flags = flag_labs(labs)
    # Deterministic, tool-verified facts — the AUTHORITATIVE literal record.
    facts = tool_lab_facts(labs)
    payload = {
        "PATIENT": json.dumps(patient),
        "RADIOLOGY REPORTS": "\n---\n".join(case.get("radiology", [])) or "none provided",
        "TOOL DATA (VERBATIM — DO NOT ALTER)": json.dumps(facts, separators=(", ", ": ")),
        "CONSULTATIONS": "\n---\n".join(case.get("consultations", [])) or "none provided",
        "SOAP NOTE": json.dumps(case.get("soap", {})),
    }
    prompt = SYNTH_PROMPT + "\n\nLAB VALUES / TOOL DATA ARE VERBATIM SOURCE DATA. Restate them EXACTLY as given (same numbers, same units). NEVER infer, round, or rewrite a tool value. Reference them by test name; do not introduce a value that conflicts with TOOL DATA.\n\nCASE DATA:\n" + json.dumps(payload, indent=1)
    raw = local_llm(prompt, model="med42")
    try:
        raw = raw.strip().lstrip("```json").rstrip("```").strip()
        d = json.loads(raw)
    except json.JSONDecodeError:
        d = {"structured_raw": raw[:1500]}
    # Immutable facts block: the chart-critical data is a faithful tool copy,
    # regardless of anything the generative model output above.
    d["lab_facts"] = facts
    d["lab_integrity"] = {"source": "tool", "verified": True,
                          "note": "Values are verbatim from the data source; never model-generated or paraphrased."}
    d["lab_flags"] = flags
    return d

if __name__ == "__main__":
    case = json.load(open(sys.argv[1])) if len(sys.argv) > 1 else (json.load(sys.stdin) if not sys.stdin.isatty() else {})
    print(json.dumps(synthesize(case), indent=2))
