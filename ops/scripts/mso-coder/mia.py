#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
MIA — the AI Coder Assistant (MSO Coder Workspace, Phase 1)
============================================================
Interactive coding Q&A for the MSO dashboard: guideline-backed answers to
coder questions, grounded in the CMS-HCC V28 reference workbook and the
Med42 clinical lane.

Answers the spec's example queries:
  * "Is this documentation sufficient for diabetes with complications?"
  * "What is the RAF impact of adding CHF?"
  * "Does this note meet MEAT?"

DOCTRINE: every answer is decision SUPPORT. MIA never invents a diagnosis,
never assumes linkage, and every answer carries
DRAFT — PROVIDER APPROVAL REQUIRED. RAF values are reference estimates.
"""
import json
import os
import re

import nura_engine

STATUS_LABEL = "DRAFT \u2014 PROVIDER APPROVAL REQUIRED"
MIA_NAME = "MIA (AI Coder Assistant)"

# --------------------------------------------------------------------------
# Intent routing
# --------------------------------------------------------------------------
INTENT_PATTERNS = [
    ("meat", re.compile(
        r"meat|monitor.{0,20}evaluat|meet\s+meat|documentation\s+(?:frame|standard)", re.I)),
    ("sufficiency", re.compile(
        r"sufficient|adequate|enough|support.{0,20}(?:diagnos|code)|documentation\s+(?:for|of)\s+\w+", re.I)),
    ("raf_impact", re.compile(
        r"raf\s*(?:impact|effect|delta)?|impact\s+of\s+adding|what.{0,10}raf|adding\s+\w+|add\s+\w+.{0,20}(?:impact|raf)", re.I)),
]


def classify_intent(question):
    q = question or ""
    for intent, pat in INTENT_PATTERNS:
        if pat.search(q):
            return intent
    return "general"


# Condition keyword -> (label, canonical ICD-10 hint) for question parsing
CONDITION_KEYS = [
    ("diabetes|diabetic|dm2|dm1|t2dm", "diabetes"),
    ("chf|heart failure|congestive|hf\\b|i50", "heart_failure"),
    ("ckd|chronic kidney|renal|n18", "ckd"),
    ("copd|emphysema|chronic bronch", "copd"),
    ("cad|coronary|angina", "cad"),
    ("afib|atrial fibrill", "afib"),
    ("stroke|cva|cerebrovascular", "cva"),
    ("cancer|malignan|oncology", "cancer"),
    ("depress|mdd", "depression"),
    ("obes|bmi", "obesity"),
    ("ulcer|wound", "ulcer"),
    ("dementia|alzheimer|cognitive", "dementia"),
]


def find_condition(question):
    q = question or ""
    for pat, key in CONDITION_KEYS:
        if re.search(pat, q, re.I):
            return key
    return None


# --------------------------------------------------------------------------
# V28 reference helpers
# --------------------------------------------------------------------------
def _raf_for_code(code, ref):
    row = ref["code_map"].get(nura_engine.get_engine().canon(code))
    if not row:
        return None
    return {"code": row["code"], "hcc": row["hcc"], "hcc_desc": row["hcc_desc"],
            "raf": row["raf"], "desc": row["desc"]}


def _hcc_set(candidates):
    return {c["hcc"] for c in candidates if c.get("hcc")}


def _approx_bonus_for(term, hccs, notes):
    """Reuse the engine's interaction table (reference estimates)."""
    for b in notes:
        if term.lower() in b["term"].lower():
            return b
    return None


# --------------------------------------------------------------------------
# Handlers
# --------------------------------------------------------------------------
def answer_sufficiency(question, chart, ref):
    cond = find_condition(question) or "diabetes"
    out = nura_engine.analyze_chart(chart, use_llm=False) if chart else None
    rules, checklist, verdict_parts = [], [], []

    if cond == "diabetes":
        rules = [
            "V28: DM complication HCCs (E11.2x nephropathy/CKD, E11.4x neuropathy, "
            "E11.3x retinopathy, E11.6x other) carry the SAME RAF (0.166) as "
            "uncomplicated E11.9 (HCC 37) \u2014 accuracy first, never inflate for RAF.",
            "The 'with' linkage must be clinically established by the provider \u2014 "
            "MIA never assumes CKD is diabetic just because both appear.",
            "MEAT must be documented annually for recapture (A1c/glucose monitoring, "
            "med adjustment, complication assessment).",
        ]
        checklist = [
            "Type documented (T2DM/T1DM) and active (not 'history of')",
            "Complication explicitly named (nephropathy, neuropathy, retinopathy, ...)",
            "Provider-established causal linkage ('DM with CKD' \u2192 E11.22)",
            "MEAT evidence in the note: A1c/glucose + medication adjustment + assessment",
        ]
        if out:
            cands = out["candidates"]
            dm = [c for c in cands if c.get("code", "").startswith("E11")]
            if not dm:
                verdict_parts.append(
                    "The note contains NO documented diabetes diagnosis \u2014 "
                    "insufficient. A medication or A1c alone is a clue, not proof.")
            else:
                comp = [c for c in dm if c["code"] not in ("E119", "E118", "E109")]
                if comp:
                    verdict_parts.append(
                        f"Complication documented and coded ({', '.join(c['code'] for c in comp)}) "
                        "\u2014 sufficient for HCC 36 IF the provider established the linkage.")
                else:
                    verdict_parts.append(
                        "DM is documented as UNCOMPLICATED (E11.9) \u2014 sufficient for "
                        "HCC 37. No complication is documented; do NOT assume one.")
                meats = []
                for c in dm:
                    m = nura_engine.get_engine().meat_check(chart, c)
                    if m:
                        meats.append(m)
                if meats:
                    verdict_parts.append("Documentation gaps: " + "; ".join(meats[:2]))
                else:
                    verdict_parts.append("MEAT appears met for the documented DM.")
    else:
        rules = [f"Condition '{cond}': verify the specific ICD-10 + HCC in the V28 "
                 f"workbook; documentation must name the diagnosis (stage/type as "
                 f"documented) plus MEAT evidence. Chart evidence, not problem lists, "
                 f"drives sufficiency."]
        checklist = ["Diagnosis explicitly assessed by the provider",
                     "Specificity present only as documented (never assumed)",
                     "MEAT evidence for annual recapture"]
        if out:
            verdict_parts.append(
                f"The provided note was analyzed: {len(out['candidates'])} candidate "
                f"code(s) surfaced \u2014 see the full /review for evidence quotes.")

    verdict = " ".join(verdict_parts) if verdict_parts else \
        "Provide a chart note to assess sufficiency against actual documentation."
    return {
        "intent": "sufficiency",
        "condition": cond,
        "answer": verdict,
        "guideline": rules,
        "checklist": checklist,
        "chart_evidence": ([c.get("evidence", "") for c in out["candidates"][:5]]
                           if out and out["candidates"] else []),
        "references": ["CMS-HCC V28 reference workbook \u2014 Diabetes rows "
                       "(HCC 35/36/37, RAF 0.166)", "MEAT documentation guide"],
        "status": STATUS_LABEL,
    }


def answer_raf_impact(question, chart, ref):
    cond = find_condition(question) or "heart_failure"
    label = {"heart_failure": "CHF", "ckd": "CKD", "diabetes": "diabetes",
             "copd": "COPD", "cad": "CAD with angina"}.get(cond, cond)

    row = None
    if cond == "heart_failure":
        row = _raf_for_code("I5022", ref)  # chronic systolic CHF -> HCC 85
    elif cond == "ckd":
        row = _raf_for_code("N1832", ref)  # stage 3b -> HCC 328
    elif cond == "diabetes":
        row = _raf_for_code("E119", ref)   # uncomplicated -> HCC 37
    elif cond == "copd":
        row = _raf_for_code("J449", ref)
    elif cond == "cad":
        row = _raf_for_code("I25110", ref)

    before, after, delta = 0.0, 0.0, 0.0
    existing_hccs, bonuses = set(), []
    current_text = None
    if chart:
        out = nura_engine.analyze_chart(chart, use_llm=False)
        existing_hccs = _hcc_set(out["candidates"])
        before = round(sum(float(c.get("raf") or 0)
                           for c in out["candidates"] if c.get("hcc")), 3)
        bonuses = out["interaction_bonuses"]
        current_text = (f"The note currently documents HCC(s): "
                        f"{sorted(existing_hccs) or ['none']} (sum \u2248 {before}). ")

    if not row:
        answer = (f"I could not resolve '{label}' to a V28 reference row from the "
                  f"question alone \u2014 provide the exact diagnosis wording.")
    else:
        added = float(row["raf"])
        after = round(before + added, 3)
        delta = round(after - before, 3)
        rel_notes = []
        # interaction terms that involve the added HCC and an existing one
        if cond == "heart_failure":
            if any(h in ("HCC 35", "HCC 36", "HCC 37") for h in existing_hccs):
                rel_notes.append("Diabetes + CHF interaction \u2248 +0.121 (approximate).")
            if any(h in ("HCC 326", "HCC 327") for h in existing_hccs):
                rel_notes.append("CHF + CKD stage 4+ interaction \u2248 +0.175 (approximate).")
            if any(h in ("HCC 35", "HCC 36", "HCC 37") for h in existing_hccs) and \
               any(h in ("HCC 326", "HCC 327") for h in existing_hccs):
                rel_notes.append("Triple DM + CHF + CKD interaction \u2248 +0.221 (approximate).")
        answer = (
            f"Adding {label} ({row['code']} \u2192 {row['hcc']}, {row['hcc_desc']}) adds "
            f"\u2248 {added:.3f} RAF. {current_text or 'With no chart provided, before = 0. '}"
            f"Estimated after \u2248 {after:.3f}; delta \u2248 +{delta:.3f}. "
            + " ".join(rel_notes)
            + " These are REFERENCE estimates \u2014 coefficients depend on model year, "
              "segment, demographics and hierarchy rules; verify against current CMS "
              "before any payment decision. Documentation must support the diagnosis "
              "(never add CHF for RAF alone)."
        )
    return {
        "intent": "raf_impact",
        "condition": label,
        "target": row,
        "raf_before_approx": before,
        "raf_after_approx": after,
        "raf_delta_approx": delta,
        "answer": answer,
        "references": [f"CMS-HCC V28 workbook \u2014 {row['hcc']} {row['hcc_desc']} "
                       f"RAF {row['raf']}" if row else "V28 workbook (verify row)"],
        "status": STATUS_LABEL,
    }


def answer_meat(question, chart, ref):
    eng = nura_engine.get_engine()
    if not chart:
        return {
            "intent": "meat",
            "answer": ("Provide the note text and I will score each documented "
                       "condition against Monitor / Evaluate / Assess / Treat. "
                       "MEAT is required annually per HCC for recapture."),
            "guideline": ["Monitor: labs, surveillance, follow-up cadence",
                          "Evaluate: results, imaging, response to therapy",
                          "Assess/Address: status, severity, stage, plan changes",
                          "Treat: medication adjustment, procedures, referrals"],
            "references": ["MEAT documentation guide (V28 workbook)"],
            "status": STATUS_LABEL,
        }
    out = nura_engine.analyze_chart(chart, use_llm=False)
    per_condition = []
    for c in out["candidates"]:
        met, missing = [], []
        n = eng.norm(chart)
        for letter, pat in eng.MEAT_MARKERS.items():
            (met if re.search(pat, n, re.I) else missing).append(letter)
        status = "met" if len(missing) == 0 else ("partial" if len(missing) <= 1 else "gap")
        per_condition.append({
            "condition": c.get("condition") or c["code"],
            "icd10": c["code"],
            "hcc": c.get("hcc"),
            "meat_status": status,
            "met_components": met,
            "missing_components": missing,
        })
    met_n = sum(1 for p in per_condition if p["meat_status"] == "met")
    unmet = [p for p in per_condition if p["meat_status"] != "met"]
    verdict = (f"MEAT assessment complete for {len(per_condition)} documented "
               f"condition(s): {met_n} meet MEAT fully.")
    if unmet:
        verdict += " " + "; ".join(
            f"{p['icd10']} is {p['meat_status']}"
            f" (missing {', '.join(p['missing_components'])})" for p in unmet) + "."
    else:
        verdict += " All conditions meet MEAT."
    fix = []
    for p in per_condition:
        if p["missing_components"]:
            fix.append(f"{p['icd10']}: add "
                       + " / ".join(p["missing_components"]) + " evidence")
    return {
        "intent": "meat",
        "answer": verdict,
        "per_condition": per_condition,
        "fixes": fix,
        "references": ["MEAT documentation guide (V28 workbook)"],
        "status": STATUS_LABEL,
    }


MIA_SYSTEM = (
    "You are MIA, a Medicare Advantage risk-adjustment coding assistant. "
    "Answer the coder's question using ONLY the CMS-HCC V28 reference rules "
    "provided and, when given, the chart text. NEVER invent a diagnosis, "
    "NEVER assume condition linkage, and never quote a RAF value not present "
    "in the rules. If the rules do not cover the question, say so and list "
    "what the coder should verify. Keep answers under 150 words. End every "
    "answer with: DRAFT — PROVIDER APPROVAL REQUIRED."
)


def _rule_context(ref):
    lines = ["CMS-HCC V28 reference (verbatim excerpts):"]
    for r in ref["quick_reference"][3:14]:
        if r and len(r) >= 5 and r[1].startswith("HCC"):
            lines.append(f"- {r[1]} {r[2]}: RAF {r[4]} (codes: {r[5][:60]})")
    lines.append("Interactions (approximate): " + "; ".join(
        f"{b['term']} {b['approx_bonus']}" for b in ref.get("interactions", [])[:6]
        if isinstance(b, dict)) if ref.get("interactions") else "")
    lines.append("Guardrails: never infer diagnosis from meds/labs/problem lists; "
                 "never add specificity; history \u2260 active; RAF values are "
                 "reference estimates.")
    return "\n".join(lines)


def answer_general(question, chart, ref, use_llm=True, ollama_url=None,
                   timeout=None):
    eng = nura_engine.get_engine()
    if use_llm:
        try:
            payload_ctx = _rule_context(ref)
            user = f"QUESTION: {question}\n"
            if chart:
                user += f"CHART (synthetic/test only): {chart[:3000]}\n"
            user += f"\nRULES:\n{payload_ctx}"
            raw = eng.call_med42(user, ollama_url or eng.DEFAULT_OLLAMA,
                                 "med42:latest", timeout or eng.LLM_TIMEOUT)
            answer = (raw or "").strip()
            if answer:
                return {"intent": "general", "llm_model": "med42:latest",
                        "answer": answer, "status": STATUS_LABEL,
                        "references": ["CMS-HCC V28 workbook excerpts (injected)"]}
        except Exception as e:  # graceful fallback — never crash MIA
            llm_err = f"{e.__class__.__name__}: {e}"
        else:
            llm_err = "Med42 unavailable"
    else:
        llm_err = None
    return {
        "intent": "general",
        "answer": ("I answer coding questions grounded in the CMS-HCC V28 "
                   "reference. I can currently handle: (1) documentation "
                   "sufficiency for a condition, (2) RAF impact of adding a "
                   "condition, (3) MEAT checks on a note. Med42 lane "
                   f"{'was unreachable (' + llm_err + ')' if llm_err else 'skipped'} \u2014 "
                   "ask one of those three forms with a chart note attached."),
        "llm_error": llm_err,
        "references": ["CMS-HCC V28 workbook"],
        "status": STATUS_LABEL,
    }


# --------------------------------------------------------------------------
# Main entry
# --------------------------------------------------------------------------
def mia_answer(question, chart=None, use_llm=True, ollama_url=None, timeout=None):
    eng = nura_engine.get_engine()
    ref = eng.load_reference(eng.DEFAULT_REF)
    intent = classify_intent(question)
    if intent == "sufficiency":
        res = answer_sufficiency(question, chart, ref)
    elif intent == "raf_impact":
        res = answer_raf_impact(question, chart, ref)
    elif intent == "meat":
        res = answer_meat(question, chart, ref)
    else:
        res = answer_general(question, chart, ref, use_llm=use_llm,
                             ollama_url=ollama_url, timeout=timeout)
    res.update({"assistant": MIA_NAME, "question": question,
                "draft": True, "provider_approval_required": True})
    return res


# --------------------------------------------------------------------------
# FastAPI router (mounted by mso-coder-api.py at /mia)
# --------------------------------------------------------------------------
def build_mia_router():
    from fastapi import APIRouter
    from pydantic import BaseModel

    router = APIRouter(prefix="/mia", tags=["mia"])

    class MiaAsk(BaseModel):
        question: str
        chart: str = ""
        use_llm: bool = True

    @router.post("/ask")
    def mia_ask(body: MiaAsk):
        return mia_answer(question=body.question, chart=body.chart or None,
                          use_llm=body.use_llm)

    @router.get("/")
    def mia_info():
        return {"assistant": MIA_NAME,
                "examples": [
                    "Is this documentation sufficient for diabetes with complications?",
                    "What is the RAF impact of adding CHF?",
                    "Does this note meet MEAT?"],
                "grounding": "CMS-HCC V28 reference workbook + Med42 lane",
                "status": STATUS_LABEL}

    return router


if __name__ == "__main__":  # CLI smoke test
    import argparse
    ap = argparse.ArgumentParser(description="MIA — AI Coder Assistant (DRAFT only)")
    ap.add_argument("--question", required=True)
    ap.add_argument("--chart", default="", help="chart text or path to a .txt")
    ap.add_argument("--no-llm", action="store_true")
    args = ap.parse_args()
    chart = None
    if args.chart:
        chart = args.chart if not os.path.exists(args.chart) else \
            open(args.chart, encoding="utf-8").read()
    print(json.dumps(mia_answer(args.question, chart=chart,
                                use_llm=not args.no_llm), indent=2))
