#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
NURA CODING AGENT — MA RAF/HCC V28 decision support engine
===========================================================
Chart/encounter text IN  ->  structured candidate codes OUT (DRAFT only).

COMPLIANCE DOCTRINE (the law, from skills/health/nura-coding-agent/SKILL.md):
  * Decision SUPPORT only — NEVER autonomous diagnosis.
  * A diagnosis must be supported by the clinical record + provider
    assessment. Medications/labs/imaging/problem lists are CLUES, never proof.
  * Incomplete evidence -> a review prompt ("Consider evaluating for..."),
    never a silent confirmation.
  * Most specific code ONLY when documented (stage/type/laterality/acuity).
    Missing specificity -> a clarify-ask, never an assumption.
  * MEAT (Monitor/Evaluate/Assess/Address-Treat) = annual documentation frame.
  * Clinical accuracy BEFORE RAF. NEVER upcoding, unsupported linkage, or
    diagnosis substitution.
  * "History of X" != active X.
  * RAF values are reference estimates — verify against current CMS before
    any payment decision.

OPERATIONAL CONSTRAINTS:
  * READ-ONLY toward production data. This script writes NOTHING to disk and
    makes NO calls to OpenEMR/Perfex/CarePilot. Its only network egress is
    the Ollama API (default http://127.0.0.1:11434) for the Med42 pass.
  * Output = candidate codes with provider-approval labels ONLY.

INPUT:
  * stdin  |  --chart "text"  |  --chart-file path

OUTPUT SHAPE (SKILL.md):
  CANDIDATES:  code + HCC + RAF + supporting quote   [all DRAFT]
  GAPS:        missing specificity / documentation
  PROMPTS:     provider-review asks
  STATUS:      DRAFT — PROVIDER APPROVAL REQUIRED

USAGE:
  python3 nura-coding-agent.py --chart "72yo M. DM2 on metformin. CKD stage 3b ..."
  echo "$NOTE" | python3 nura-coding-agent.py --json
  python3 nura-coding-agent.py --chart-file note.txt --ollama http://72.60.163.140:11434
  python3 nura-coding-agent.py --chart "..." --no-llm     # pure rule-based
"""

import argparse
import json
import os
import re
import sys
import time
import unicodedata
import urllib.error
import urllib.request

# --------------------------------------------------------------------------
# Constants
# --------------------------------------------------------------------------
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
DEFAULT_REF = os.path.join(SCRIPT_DIR, "nura-coding-ref.json")
DEFAULT_OLLAMA = os.environ.get("NURA_CODING_OLLAMA", "http://127.0.0.1:11434")
DEFAULT_MODELS = ["med42:latest", "biomistral:latest"]   # Med42 first, per doctrine
LLM_TIMEOUT = float(os.environ.get("NURA_CODING_LLM_TIMEOUT", "150"))
MAX_LLM_CHART_CHARS = 6000                                # med42 ctx = 8192

STATUS_LABEL = "DRAFT \u2014 PROVIDER APPROVAL REQUIRED"
BANNER = (
    "NURA CODING AGENT \u2014 MA RAF/HCC V28 decision support\n"
    "DECISION SUPPORT ONLY \u2014 NOT A DIAGNOSIS \u2014 "
    "PROVIDER APPROVAL REQUIRED ON EVERY OUTPUT\n"
    "READ-ONLY: no writes to OpenEMR/Perfex/CarePilot. No PHI leaves the box."
)

# --------------------------------------------------------------------------
# Reference loading (stdlib only — the JSON sidecar is built by
# nura-coding-ref-extract.py from the MA RAF V28 workbook)
# --------------------------------------------------------------------------
def canon(code):
    """Canonical ICD-10 form used by the workbook: dots stripped (E11.9 -> E119)."""
    return str(code).replace(".", "").strip().upper()


def load_reference(ref_path):
    if not os.path.exists(ref_path):
        sys.stderr.write(
            f"FATAL: reference sidecar missing: {ref_path}\n"
            "Rebuild it:  uv run --with openpyxl nura-coding-ref-extract.py\n"
        )
        sys.exit(2)
    with open(ref_path, "r", encoding="utf-8") as f:
        raw = json.load(f)
    ref = {"quick": raw.get("quick_reference", []),
           "map": raw.get("icd10_hcc_map", []),
           "traps": raw.get("v28_traps", []),
           "interactions": raw.get("interactions", []),
           "prompts": raw.get("prompt_library", []),
           "tips": raw.get("tips_warnings", []),
           "guardrails": raw.get("guardrails", [])}
    # ---- indexed structures ----
    code_map = {}
    for row in ref["map"]:
        code = row[0].strip() if row and row[0] else ""
        if re.fullmatch(r"[A-TV-Z][0-9]{2,4}(?:\.[0-9A-Z]{1,4})?", code):
            code_map[canon(code)] = {
                "code": canon(code), "desc": row[1], "group": row[2],
                "hcc": row[4], "hcc_desc": row[5], "raf": row[6],
            }
    # tips: hcc -> warning text
    tip_by_hcc = {}
    for row in ref["tips"]:
        if len(row) >= 6 and row[0].upper().startswith("HCC"):
            tip_by_hcc[row[0].upper()] = row[5]
    # quick reference: hcc -> condition/raf
    quick_by_hcc = {}
    for row in ref["quick"][3:]:
        if len(row) >= 5 and row[1].upper().startswith("HCC"):
            quick_by_hcc[row[1].upper()] = {
                "condition": row[2], "raf": row[4], "codes": row[5]}
    ref["code_map"] = code_map
    ref["tip_by_hcc"] = tip_by_hcc
    ref["quick_by_hcc"] = quick_by_hcc
    return ref


def norm(text):
    """Lowercase + unicode-normalize for matching."""
    return unicodedata.normalize("NFKD", text).lower()


# --------------------------------------------------------------------------
# Domain signal library
# Each domain = documented-diagnosis patterns + clue patterns (signals, not
# proof) + curated candidate codes. Specificity is extracted, never assumed.
# --------------------------------------------------------------------------
ICD10_RE = re.compile(r"\b([A-TV-Z][0-9]{2}(?:\.[0-9A-Z]{1,4})?)\b")

# Codes that are "not a payment HCC in V28" — trap list from the workbook,
# extended with common no-HCC mentions.
TRAP_CODES = {
    "I10": "Essential hypertension alone — no payment HCC. Only counts WITH heart failure (I11.0) or CKD (I12.x/I13.x).",
    "I119": "Hypertensive heart disease without HF — removed from V28.",
    "I1310": "Hypertensive heart/CKD without HF — removed from V28.",
    "I2510": "CAD without angina — removed from V28. Use I25.11x only if angina documented.",
    "I252": "Old MI — history alone no longer sufficient in V28.",
    "I2582": "Chronic total occlusion — removed from V28 payment HCCs.",
    "E785": "Hyperlipidemia — no payment HCC in V28.",
    "E039": "Hypothyroidism — no payment HCC in any version.",
    "E440": "Moderate protein-calorie malnutrition — removed from V28 (was upcoded).",
    "E46": "Unspecified malnutrition — insufficient specificity.",
    "G4733": "OSA — removed from V28 payment HCCs.",
    "M1990": "Osteoarthritis — no payment HCC in V28.",
    "M810": "Osteoporosis without pathological fracture — no payment HCC in V28.",
    "K210": "GERD — no payment HCC in any model.",
    "R413": "Memory loss unspecified — does not map to a dementia HCC in V28.",
    "G4700": "Insomnia — no payment HCC.",
    "F32A": "Depression unspecified — unreliable payment HCC in V28. Specify severity.",
    "Z8739": "History codes (Z87.x) — never generate payment HCCs.",
}

# V28 trap conditions with alternative paths (workbook 🚫 sheet)
TRAP_ALTERNATIVES = [
    (r"\bCAD\b|cad\b|coronary artery disease", "angina",
     "CAD counts in V28 only WITH angina (I25.11x). If angina is documented, specify I25.11x; otherwise no payment HCC."),
    (r"\bhypertension\b|\bHTN\b", "heart_failure|heart failure|ckd|chronic kidney",
     "HTN alone has no HCC. It counts only with HF (I11.0) or CKD (I12.x/I13.x) — use those codes only if clinically established."),
    (r"\bold mi\b|old myocardial infarction|prior mi",
     None, "Old MI alone no longer counts. Document active CAD with angina (I25.11x) if present."),
    (r"\bosa\b|obstructive sleep apnea",
     "obesity hypoventilation|pickwickian|hypercapnia",
     "OSA was removed from V28. If hypercapnia is confirmed, document obesity hypoventilation (E66.2)."),
    (r"\bmalnutrition\b|protein.calorie",
     "severe",
     "Only severe protein-calorie malnutrition (E43) may qualify in V28; moderate/unspecified do not."),
]

# --------------------------------------------------------------------------
# Domain matchers: each returns list of findings
# finding = {kind: candidate|history|signal|trap, code, hcc, hcc_desc, raf,
#            condition, evidence, notes}
# --------------------------------------------------------------------------
def find_specificity(chart, patterns):
    """Return the first matching alternative from ordered (label, regex) pairs."""
    for label, pat in patterns:
        if re.search(pat, chart, re.I):
            return label
    return None


def make_candidate(code, evidence, ref, note=None, source="rule"):
    row = ref["code_map"].get(canon(code))
    if not row:
        return {"kind": "candidate", "code": canon(code), "hcc": None,
                "hcc_desc": None, "raf": None, "evidence": evidence,
                "condition": canon(code), "note": note or "no reference mapping — coder verify",
                "source": source, "unmapped": True}
    return {"kind": "candidate", "code": canon(code), "hcc": row["hcc"],
            "hcc_desc": row["hcc_desc"], "raf": row["raf"],
            "evidence": evidence, "condition": row["desc"],
            "note": note or "", "source": source, "unmapped": False}


def match_diabetes(chart, ref):
    out = []
    n = norm(chart)
    if not re.search(r"diabet|DM2|DM1|\bT2DM\b|\bT1DM\b|A1c|HbA1c|insulin|metformin|glipizide|glargine|semaglutide|ozempic", n, re.I):
        return out
    hx = history_spans(chart)
    documented = re.search(r"(type\s*[12]\s*)?diabet|\bDM2\b|\bDM1\b|\bT2DM\b|\bT1DM\b", n, re.I)
    in_history = documented and any(documented.group(0) in s for s in hx)
    # diagnosis present?
    dx_pat = re.search(
        r"(type\s*2\s*diabetes|type\s*1\s*diabetes|DM2|DM1|T2DM|T1DM|diabetes mellitus)"
        r"[^.;\n]{0,120}?(?:on|treated|controlled|uncontrolled|taking)?",
        n)
    has_dx = bool(re.search(
        r"type\s*(?:2|ii)\s*diabetes|type\s*(?:1|i)\s*diabetes|DM2|DM1|T2DM|T1DM|\bdiabetes mellitus\b",
        n)) and not in_history
    if in_history:
        out.append({"kind": "history", "condition": "Diabetes mellitus",
                    "note": "History of DM noted — clarify whether active.",
                    "evidence": ""})
        return out
    if has_dx:
        t1 = bool(re.search(r"type\s*(?:1|i)\b|\bDM1\b|\bT1DM\b", n, re.I))
        acute = re.search(r"\bDKA\b|ketoacidosis|hyperosmolar|HHS", n, re.I)
        nephro = re.search(r"nephropathy|diabetic (?:ckd|kidney)|DM2? (?:with )?CKD", n, re.I)
        neuro = re.search(r"neuropathy", n, re.I)
        retino = re.search(r"retinopathy", n, re.I)
        ckd_dx = re.search(r"ckd|chronic kidney disease|stage\s*3b|stage\s*4|stage\s*5", n, re.I)
        if acute:
            code = "E1110" if not t1 else "E1010"
            ev = acute.group(0)
            out.append(make_candidate(code, ev, ref,
                     note="Acute complication documented.", source="rule"))
            out.append({"kind": "note", "condition": "Diabetes acute complication",
                        "note": "HCC 35 same RAF as HCC 36/37 in V28 — accuracy first."})
        elif nephro:
            code = "E1122" if not t1 else "E1022"
            out.append(make_candidate(code, nephro.group(0), ref,
                     note="DM with diabetic CKD — relationship must be clinically established (do not assume linkage).",
                     source="rule"))
        elif neuro:
            out.append(make_candidate("E1142" if not t1 else "E1042",
                     neuro.group(0), ref, note="Diabetic neuropathy documented.", source="rule"))
        elif retino:
            out.append(make_candidate("E11319" if not t1 else "E10319",
                     retino.group(0), ref, note="Diabetic retinopathy documented — specify laterality/severity if known.", source="rule"))
        else:
            out.append(make_candidate("E119" if not t1 else "E109", "diabetes documented",
                     ref, note="Uncomplicated DM. V28: same RAF as complication HCCs — accuracy first.", source="rule"))
        if ckd_dx and not (nephro or re.search(r"diabetic ckd", n, re.I)):
            out.append({"kind": "gap", "condition": "Diabetes + CKD",
                        "note": "DM and CKD both documented. If the CKD is diabetic, document E11.22/E10.22 relationship explicitly (clinically established only)."})
        if not re.search(r"A1c|HbA1c|glucose", n, re.I):
            out.append({"kind": "gap", "condition": "Diabetes mellitus",
                        "note": "MEAT: add A1c/glucose monitoring + med adjustment evidence for annual recapture."})
    else:
        out.append({"kind": "signal", "condition": "Diabetes mellitus",
                    "note": "Consider evaluating for diabetes — A1c/glucose/meds suggest it but no diagnosis is documented."})
    return out


def match_ckd(chart, ref):
    out = []
    n = norm(chart)
    if not re.search(r"ckd|chronic kidney|renal insuff|esrd|end.stage renal|dialysis|eGFR|GFR\b|creatinine", n, re.I):
        return out
    hx = history_spans(chart)
    dx = re.search(r"ckd|chronic kidney disease|renal insufficiency|esrd|end[- ]stage renal|on dialysis|on hemodialysis|nephropathy", n, re.I)
    if dx and any(dx.group(0) in s for s in hx):
        out.append({"kind": "history", "condition": "CKD",
                    "note": "History of renal disease — clarify current stage/status.", "evidence": ""})
        return out
    if not dx:
        out.append({"kind": "signal", "condition": "Chronic kidney disease",
                    "note": "Reduced eGFR/creatinine noted but no CKD diagnosis documented — consider evaluating stage."})
        return out
    stage5 = re.search(r"stage\s*5|esrd|end[- ]stage|dialysis|hemodialysis|N18\.[56]|Z99\.2", n, re.I)
    stage4 = re.search(r"stage\s*4\b|N18\.4", n, re.I)
    stage3b = re.search(r"stage\s*3\s*[bB]|3b|N18\.32", n, re.I)
    stage3a = re.search(r"stage\s*3\s*[aA]|3a|N18\.31", n, re.I)
    stage3u = re.search(r"stage\s*3\b(?!\s*[ab])", n, re.I)
    if stage5:
        code = "N185"
        if re.search(r"esrd|end[- ]stage|dialysis|hemodialysis|Z99\.2", n, re.I):
            code = "N186"
            if re.search(r"dialysis|hemodialysis", n, re.I):
                out.append(make_candidate("Z992", "dialysis documented", ref,
                         note="Dialysis dependence (status code).", source="rule"))
        out.append(make_candidate(code, "CKD stage 5/ESRD documented", ref,
                 note="", source="rule"))
    elif stage4:
        out.append(make_candidate("N184", "CKD stage 4 documented", ref, source="rule"))
    elif stage3b:
        out.append(make_candidate("N1832", "CKD stage 3b documented", ref,
                 note="Stage 3b (N18.32) is the only stage-3 code that maps to HCC 328 in V28.", source="rule"))
    elif stage3a:
        out.append(make_candidate("N1831", "CKD stage 3a documented", ref,
                 note="Stage 3a (N18.31) does NOT generate a payment HCC in V28 — document accurately, do not upstage.", source="rule"))
    elif stage3u:
        out.append(make_candidate("N1830", "CKD stage 3 (substage unspecified)", ref,
                 note="Missing specificity: only 3b (N18.32) maps to HCC 328. Clarify 3a vs 3b — do NOT assume 3b.", source="rule"))
        out.append({"kind": "gap", "condition": "CKD stage 3",
                    "note": "Specify CKD stage 3a (GFR 45-59) vs 3b (GFR 30-44). Only 3b maps to HCC 328."})
    else:
        out.append({"kind": "signal", "condition": "CKD",
                    "note": "CKD mentioned without stage — document the stage (N18.x). Only stages 3b/4/5 generate V28 payment HCCs."})
    if not re.search(r"egfr|gfr\b|creatinine|cr\b", n, re.I):
        out.append({"kind": "gap", "condition": "CKD",
                    "note": "MEAT: add eGFR trend + monitoring evidence for annual recapture."})
    return out


def match_hf(chart, ref):
    out = []
    n = norm(chart)
    if not re.search(r"heart failure|\bCHF\b|\bHF\b|furosemide|lasix|bumetanide|EF\s*<?\d|bnp|nt.probnp|ejection fraction", n, re.I):
        return out
    hx = history_spans(chart)
    dx = re.search(r"heart failure|\bCHF\b|\bcongestive", n, re.I)
    if not dx:
        out.append({"kind": "signal", "condition": "Heart failure",
                    "note": "Diuretic/echo/BNP signals noted but no HF diagnosis documented — consider evaluating HF status."})
        return out
    if any(dx.group(0) in s for s in hx):
        out.append({"kind": "history", "condition": "Heart failure",
                    "note": "History of HF — clarify current phenotype and activity.", "evidence": ""})
        return out
    systolic = re.search(r"systolic", n, re.I)
    diastolic = re.search(r"diastolic", n, re.I)
    combined = re.search(r"combined|biventricular", n, re.I)
    acute = re.search(r"acute", n, re.I)
    chronic = re.search(r"chronic", n, re.I)
    # choose most specific I50.x
    if systolic and acute and chronic:
        code = "I5023"
    elif systolic and acute:
        code = "I5021"
    elif systolic:
        code = "I5022"
    elif diastolic and acute and chronic:
        code = "I5033"
    elif diastolic and acute:
        code = "I5031"
    elif diastolic:
        code = "I5032"
    elif combined:
        code = "I5042"
    else:
        code = "I509"
        out.append({"kind": "gap", "condition": "Heart failure",
                    "note": "Specify phenotype: systolic (I50.2x) / diastolic (I50.3x) / combined (I50.4x), and acute vs chronic."})
    ev = "HF documented" + (" (systolic)" if systolic else "") + (" (diastolic)" if diastolic else "")
    out.append(make_candidate(code, ev, ref, note="", source="rule"))
    if not re.search(r"EF\s*<?\d|ejection fraction|NYHA|nyha", n, re.I):
        out.append({"kind": "gap", "condition": "Heart failure",
                    "note": "MEAT: document EF% and NYHA class for annual recapture."})
    return out


def match_copd(chart, ref):
    out = []
    n = norm(chart)
    if not re.search(r"COPD|emphysema|chronic bronchitis|chronic lung", n, re.I):
        return out
    if any(re.search(r"COPD|emphysema", n, re.I).group(0) in s for s in history_spans(chart)):
        out.append({"kind": "history", "condition": "COPD",
                    "note": "History of COPD — clarify current status/severity.", "evidence": ""})
        return out
    out.append(make_candidate("J449", "COPD documented", ref, source="rule"))
    if not re.search(r"inhaler|spirometry|FEV1|oxygen|pft", n, re.I):
        out.append({"kind": "gap", "condition": "COPD",
                    "note": "MEAT: document inhaler regimen / spirometry / exacerbation status."})
    return out


def match_cad(chart, ref):
    out = []
    n = norm(chart)
    if not re.search(r"\bCAD\b|coronary artery disease|angina|I25", n, re.I):
        return out
    angina = re.search(r"angina", n, re.I)
    if angina:
        out.append(make_candidate("I25110", "CAD with angina documented", ref,
                 note="Use I25.11x only — specify site/stability as documented.", source="rule"))
    else:
        out.append({"kind": "trap", "condition": "Coronary artery disease",
                    "note": "CAD without angina has no payment HCC in V28 (I25.10). If angina is present, document it and use I25.11x."})
    return out


def match_afib(chart, ref):
    out = []
    n = norm(chart)
    if not re.search(r"atrial fibrillation|\bAFib\b|\bAF\b|arrhythmia|flutter", n, re.I):
        return out
    if re.search(r"atrial fibrillation|\bAFib\b", n, re.I):
        out.append(make_candidate("I4891", "Atrial fibrillation documented", ref, source="rule"))
    else:
        out.append({"kind": "signal", "condition": "Arrhythmia",
                    "note": "Arrhythmia mentioned without AF diagnosis — clarify type if clinically established."})
    return out


def match_cva(chart, ref):
    out = []
    n = norm(chart)
    if not re.search(r"stroke|CVA|infarct|cerebrovascular|carotid stenosis|TIA|hemiplegia|hemiparesis", n, re.I):
        return out
    hx = history_spans(chart)
    stroke = re.search(r"stroke|CVA|infarct", n, re.I)
    if stroke and any(stroke.group(0) in s for s in hx):
        out.append({"kind": "history", "condition": "Stroke",
                    "note": "History of stroke — document residual deficits/sequelae if present (I69.x).", "evidence": ""})
        return out
    if stroke:
        out.append(make_candidate("I639", "stroke documented", ref,
                 note="Specify ischemic vs hemorrhagic, and site, as documented.", source="rule"))
    elif re.search(r"carotid stenosis|cerebrovascular", n, re.I):
        out.append(make_candidate("I6521", "carotid stenosis documented", ref, source="rule"))
    elif re.search(r"\bTIA\b|transient ischemic", n, re.I):
        out.append({"kind": "trap", "condition": "TIA",
                    "note": "TIA alone does not map to a V28 payment HCC — document etiology if stroke is diagnosed."})
    return out


def match_cancer(chart, ref):
    out = []
    n = norm(chart)
    if not re.search(r"cancer|carcinoma|malignan|lymphoma|leukemia|oncology|metast", n, re.I):
        return out
    hx = history_spans(chart)
    m = re.search(r"cancer|carcinoma|malignan|lymphoma|leukemia", n, re.I)
    if m and any(m.group(0) in s for s in hx):
        out.append({"kind": "history", "condition": "Malignancy",
                    "note": "History of cancer ≠ active cancer — clarify active vs remission. Never code history as active.", "evidence": ""})
        return out
    if re.search(r"metast", n, re.I):
        out.append(make_candidate("C799", "metastatic cancer documented", ref,
                 note="Metastatic disease (HCC 8). Specify primary site as documented.", source="rule"))
    else:
        out.append({"kind": "signal", "condition": "Malignancy",
                    "note": "Active malignancy mentioned — document primary site, metastatic status, and current treatment for correct HCC."})
    return out


def match_dementia(chart, ref):
    out = []
    n = norm(chart)
    if not re.search(r"dementia|alzheimer|cognitive impair|MCI", n, re.I):
        return out
    if re.search(r"\bMCI\b|mild cognitive", n, re.I):
        out.append(make_candidate("G3184", "MCI documented", ref,
                 note="Mild neurocognitive disorder — HCC 127.", source="rule"))
        return out
    beh = re.search(r"behavioral|agitation|wandering|psychosis", n, re.I)
    out.append(make_candidate("F0390", "dementia documented", ref,
             note=("With behavioral disturbance (HCC 125)." if beh else "Without behavioral disturbance (HCC 126)."),
             source="rule"))
    return out


def match_mood_psych(chart, ref):
    out = []
    n = norm(chart)
    if re.search(r"\bschizophren|schizoaffective|psychosis", n, re.I):
        out.append(make_candidate("F209", "schizophrenia documented", ref, source="rule"))
    if re.search(r"\bbipolar\b|mania|manic", n, re.I):
        out.append(make_candidate("F319", "bipolar documented", ref, source="rule"))
    dep = re.search(r"depress|MDD", n, re.I)
    if dep and not any(dep.group(0) in s for s in history_spans(chart)):
        severe = re.search(r"severe", n, re.I)
        if severe:
            out.append(make_candidate("F322", "depression documented (severe)", ref, source="rule"))
        else:
            out.append(make_candidate("F321", "depression documented", ref,
                     note="Specify severity (mild/moderate/severe) — unspecified depression (F32.A) is unreliable in V28.",
                     source="rule"))
    if re.search(r"anxiety|PTSD|post.traumatic|\bOCD\b", n, re.I):
        out.append(make_candidate("F419", "anxiety documented", ref, source="rule"))
    if re.search(r"alcohol use disorder|alcoholism|etoh", n, re.I):
        out.append(make_candidate("F1020", "alcohol use disorder documented", ref, source="rule"))
    if re.search(r"drug use|substance use|opioid use disorder", n, re.I):
        out.append(make_candidate("F199", "substance use documented", ref, source="rule"))
    return out


def match_obesity(chart, ref):
    out = []
    n = norm(chart)
    if not re.search(r"obes|BMI", n, re.I):
        return out
    if re.search(r"morbid obes|severe obes|BMI\s*[=>]?\s*4[0-9]|BMI\s*[=>]?\s*50", n, re.I):
        out.append(make_candidate("E6601", "morbid obesity documented", ref, source="rule"))
    elif re.search(r"BMI\s*[=>]?\s*3[0-9]", n, re.I):
        out.append({"kind": "signal", "condition": "Obesity",
                    "note": "BMI in obese range — if clinically established as morbid obesity (BMI≥40), document E66.01."})
    return out


def match_ulcers(chart, ref):
    out = []
    n = norm(chart)
    if not re.search(r"pressure ulcer|pressure injury|bedsore|decubitus|skin ulcer|chronic ulcer", n, re.I):
        return out
    st4 = re.search(r"stage\s*4|stage iv", n, re.I)
    st3 = re.search(r"stage\s*3|stage iii", n, re.I)
    if st4:
        out.append(make_candidate("L8990", "pressure ulcer stage 4 documented", ref, source="rule"))
    elif st3:
        out.append(make_candidate("L8991", "pressure ulcer stage 3 documented", ref, source="rule"))
    elif re.search(r"skin ulcer|chronic ulcer", n, re.I):
        out.append(make_candidate("L9790", "chronic non-pressure skin ulcer documented", ref, source="rule"))
    else:
        out.append({"kind": "signal", "condition": "Pressure ulcer",
                    "note": "Pressure ulcer mentioned — document stage (3/4 map to HCC 154/155)."})
    return out


def match_dvt(chart, ref):
    out = []
    n = norm(chart)
    if not re.search(r"\bDVT\b|deep vein|venous thrombosis|\bVTE\b|pulmonary emb", n, re.I):
        return out
    if re.search(r"chronic", n, re.I):
        out.append(make_candidate("I82501", "chronic DVT documented", ref,
                 note="Use chronic DVT codes (I82.5xx) — specify laterality/vessel as documented.", source="rule"))
    else:
        out.append({"kind": "signal", "condition": "DVT/VTE",
                    "note": "DVT mentioned — specify chronicity: chronic DVT (I82.x1/x2) is the V28 code; acute-only does not map the same way."})
    return out


def match_pvd(chart, ref):
    out = []
    n = norm(chart)
    if not re.search(r"\bPAD\b|\bPVD\b|peripheral (?:vascular|arterial)|claudication", n, re.I):
        return out
    out.append(make_candidate("I739", "PVD documented", ref,
             note="Specify claudication vs critical limb ischemia as documented.", source="rule"))
    return out


def match_neuro_other(chart, ref):
    out = []
    n = norm(chart)
    if re.search(r"parkinson", n, re.I):
        out.append(make_candidate("G20", "Parkinson's documented", ref, source="rule"))
    if re.search(r"multiple sclerosis", n, re.I):
        out.append(make_candidate("G35", "MS documented", ref, source="rule"))
    if re.search(r"status epilepticus", n, re.I):
        out.append(make_candidate("G40101", "status epilepticus documented", ref, source="rule"))
    elif re.search(r"epilepsy|seizure disorder", n, re.I):
        out.append(make_candidate("G409", "epilepsy documented", ref, source="rule"))
    if re.search(r"quadripleg|tetrapleg", n, re.I):
        out.append(make_candidate("G8250", "quadriplegia documented", ref, source="rule"))
    elif re.search(r"parapleg|hemipleg|paralysis", n, re.I):
        out.append(make_candidate("G829", "paralysis documented", ref, source="rule"))
    return out


def match_rheum_infect(chart, ref):
    out = []
    n = norm(chart)
    if re.search(r"rheumatoid arthritis", n, re.I):
        out.append(make_candidate("M069", "RA documented", ref, source="rule"))
    if re.search(r"\bHIV\b|human immunodef", n, re.I):
        out.append(make_candidate("B20", "HIV documented", ref, source="rule"))
    if re.search(r"hep(?:atitis)?\s*C|\bHCV\b", n, re.I):
        out.append(make_candidate("B182", "chronic hepatitis C documented", ref, source="rule"))
    if re.search(r"cirrhosis|end.stage liver|hepatic failure", n, re.I):
        out.append(make_candidate("K746", "cirrhosis documented", ref, source="rule"))
    if re.search(r"sepsis|septicemia", n, re.I):
        out.append(make_candidate("A419", "sepsis documented", ref, source="rule"))
    return out


def match_status(chart, ref):
    out = []
    n = norm(chart)
    if re.search(r"transplant|transplanted", n, re.I):
        out.append(make_candidate("Z9481", "transplant status documented", ref, source="rule"))
    if re.search(r"amputat", n, re.I):
        out.append(make_candidate("Z89511", "amputation status documented", ref, source="rule"))
    return out


DOMAIN_MATCHERS = [
    match_diabetes, match_ckd, match_hf, match_copd, match_cad, match_afib,
    match_cva, match_cancer, match_dementia, match_mood_psych, match_obesity,
    match_ulcers, match_dvt, match_pvd, match_neuro_other,
    match_rheum_infect, match_status,
]


def history_spans(chart):
    """Spans following history markers: 'history of X', 'hx of X', 's/p X'."""
    n = norm(chart)
    spans = []
    for m in re.finditer(
        r"(?:history|hx|s/p|status post|prior|remote|previous)(?:\s+of)?\s+([^.;\n]{0,80})",
        n):
        spans.append(m.group(1))
    return spans


def scan_exact_codes(chart, ref):
    """Exact + prefix ICD-10 code scan against the 590-code map."""
    out = []
    seen = set()
    n = norm(chart)
    for m in ICD10_RE.finditer(chart.upper()):
        raw_code = m.group(1)
        code = canon(raw_code)
        if code in seen:
            continue
        seen.add(code)
        row = ref["code_map"].get(code)
        if row:
            out.append(make_candidate(code, f"code {raw_code} in chart", ref, source="rule"))
            continue
        # prefix resolution (longest prefix in map)
        best = None
        for k in sorted(ref["code_map"], key=len, reverse=True):
            if code.startswith(k):
                best = k
                break
        if best:
            out.append(make_candidate(best, f"code {raw_code} (resolved to {best})", ref,
                     note="Code not exact in reference — longest-prefix resolved.", source="rule"))
        else:
            trap = TRAP_CODES.get(code) or TRAP_CODES.get(code[:3])
            if trap:
                out.append({"kind": "trap", "condition": raw_code,
                            "note": f"{raw_code}: {trap}"})
            else:
                out.append({"kind": "signal", "condition": raw_code,
                            "note": f"Code {raw_code} not in the V28 reference — coder verify."})
    return out


def scan_traps(chart):
    out = []
    n = norm(chart)
    for pat, trigger_alt, note in TRAP_ALTERNATIVES:
        m = re.search(pat, n, re.I)
        if not m:
            continue
        if trigger_alt and re.search(trigger_alt, n, re.I):
            out.append({"kind": "trap", "condition": m.group(0),
                        "note": note + " (Qualifying condition may be present — use the combined code ONLY if the relationship is clinically established.)"})
            continue
        out.append({"kind": "trap", "condition": m.group(0), "note": note})
    # generic trap mentions by name: (pattern, label, note)
    trap_names = [
        (r"\bhyperlipidemia\b|\bhypercholesterol", "Hyperlipidemia",
         "Hyperlipidemia — no payment HCC in V28."),
        (r"\bhypothyroid", "Hypothyroidism",
         "Hypothyroidism — no payment HCC in any version."),
        (r"\bGERD\b|gastroesophageal reflux", "GERD",
         "GERD — no payment HCC in any model."),
        (r"\bosteoarthrit", "Osteoarthritis",
         "Osteoarthritis — no payment HCC in V28."),
        (r"\binsomnia\b", "Insomnia", "Insomnia — no payment HCC."),
        (r"\bosteoporosis\b", "Osteoporosis",
         "Osteoporosis without pathological fracture — no payment HCC (M80.x with fracture may qualify)."),
    ]
    for pat, label, note in trap_names:
        if re.search(pat, n, re.I):
            out.append({"kind": "trap", "condition": label, "note": note})
    return out


# --------------------------------------------------------------------------
# Evidence / MEAT scoring
# --------------------------------------------------------------------------
MEAT_MARKERS = {
    "Monitor": r"monitor|follow[- ]up|recheck|surveillance|annual|every \d+ months?|trend",
    "Evaluate": r"lab|A1c|HbA1c|eGFR|GFR|creatinine|BNP|echo|imaging|ultrasound|X[- ]?ray|CT\b|MRI|scope|biopsy|exam",
    "Assess": r"assess|stage|class|severity|EF\s*<?\d|controlled|uncontrolled|stable|worsening",
    "Treat": r"mg\b|mcg\b|metformin|insulin|lisinopril|losartan|furosemide|lasix|metoprolol|carvedilol|entresto|farxiga|jardiance|ozempic|warfarin|eliquis|xarelto|statin|atorvastatin|inhaler|symbicort|oxygen|diet|exercise|referral",
}


def meat_check(chart, candidate):
    missing = []
    n = norm(chart)
    for key, pat in MEAT_MARKERS.items():
        if not re.search(pat, n, re.I):
            missing.append(key)
    if len(missing) >= 3:
        return (f"MEAT gap — add {', '.join(missing)} evidence "
                f"for annual recapture of {candidate.get('condition') or candidate['code']}.")
    if missing:
        return (f"MEAT partial — consider documenting {', '.join(missing)} "
                f"for {candidate.get('condition') or candidate['code']}.")
    return None


# --------------------------------------------------------------------------
# Interaction bonuses (reference estimates, approximate)
# --------------------------------------------------------------------------
def interaction_bonuses(candidates):
    hccs = {c["hcc"] for c in candidates if c.get("hcc")}
    notes = []
    def has(*codes):
        return all(c in hccs for c in codes)
    dm = ("HCC 35" in hccs or "HCC 36" in hccs or "HCC 37" in hccs)
    if has("HCC 85", "HCC 211"):
        notes.append({"term": "CHF + COPD", "approx_bonus": "~0.155",
                      "note": "Both must have separate MEAT each visit."})
    if dm and has("HCC 85"):
        notes.append({"term": "Diabetes + CHF", "approx_bonus": "~0.121",
                      "note": "Document both conditions separately each visit."})
    if dm and (has("HCC 326") or has("HCC 327")):
        notes.append({"term": "Diabetes + CKD Stage 4-5", "approx_bonus": "~0.128",
                      "note": "Also triggers E11.22 if CKD is diabetic (clinically established)."})
    if has("HCC 85") and (has("HCC 326") or has("HCC 327")):
        notes.append({"term": "CHF + CKD Stage 4+", "approx_bonus": "~0.175",
                      "note": "Cardiorenal — document both with co-management."})
    if dm and has("HCC 85") and (has("HCC 326") or has("HCC 327")):
        notes.append({"term": "Diabetes + CHF + CKD (triple)", "approx_bonus": "~0.221",
                      "note": "High-value triple interaction — all 3 documented annually."})
    if len(hccs) >= 4:
        notes.append({"term": f"Count bonus ({len(hccs)} HCCs)", "approx_bonus": "count bonus",
                      "note": "V28 rewards complexity — each additional legitimate HCC adds interaction credit."})
    return notes


# --------------------------------------------------------------------------
# Med42 (Ollama) lane
# --------------------------------------------------------------------------
LLM_SYSTEM = (
    "You are a medical coding decision-support assistant for CMS-HCC V28. "
    "Extract ONLY diagnoses explicitly documented in the chart. NEVER invent "
    "diagnoses. NEVER assume linkage between conditions. Distinguish active "
    "conditions from history. A medication, lab, or problem list entry is a "
    "clue, not proof of a diagnosis. Respond with STRICT JSON only:\n"
    '{"diagnoses":[{"condition":"...","icd10":"...","quote":"verbatim text '
    'from chart","status":"active|history"}],'
    '"clarifications":["missing specificity asks, phrased as questions"],'
    '"signals":["findings without a documented diagnosis, phrased as '
    'provider-review questions"]}'
)


def call_med42(chart, ollama_url, model, timeout):
    payload = {
        "model": model,
        "stream": False,
        "options": {"temperature": 0.1, "num_predict": 700},
        "messages": [
            {"role": "system", "content": LLM_SYSTEM},
            {"role": "user", "content": chart[:MAX_LLM_CHART_CHARS]},
        ],
    }
    req = urllib.request.Request(
        f"{ollama_url.rstrip('/')}/api/chat",
        data=json.dumps(payload).encode("utf-8"),
        headers={"Content-Type": "application/json"},
    )
    with urllib.request.urlopen(req, timeout=timeout) as resp:
        body = json.loads(resp.read().decode("utf-8"))
    return body.get("message", {}).get("content", "")


def tolerant_json(text):
    """Extract the first balanced JSON object from model output."""
    if not text:
        return None
    start = text.find("{")
    if start == -1:
        return None
    depth, in_str, esc = 0, False, False
    for i in range(start, len(text)):
        ch = text[i]
        if in_str:
            if esc:
                esc = False
            elif ch == "\\":
                esc = True
            elif ch == '"':
                in_str = False
        elif ch == '"':
            in_str = True
        elif ch == "{":
            depth += 1
        elif ch == "}":
            depth -= 1
            if depth == 0:
                try:
                    return json.loads(text[start:i + 1])
                except Exception:
                    return None
    return None


def med42_pass(chart, ollama_url, models, timeout):
    """Returns (lanes_tried, findings, error). Graceful fallback on ANY failure."""
    last_err = None
    for model in models:
        try:
            raw = call_med42(chart, ollama_url, model, timeout)
            parsed = tolerant_json(raw)
            if not parsed:
                last_err = f"{model}: non-JSON response"
                continue
            findings = []
            for d in parsed.get("diagnoses", []):
                cond = str(d.get("condition", ""))
                code = str(d.get("icd10", "")).upper().replace(" ", "")
                quote = str(d.get("quote", ""))[:200]
                status = str(d.get("status", "active"))
                if not re.fullmatch(r"[A-TV-Z][0-9]{2,4}(?:\.[0-9A-Z]{1,4})?", code):
                    findings.append({"kind": "llm_note", "condition": cond or code,
                                     "note": f"Med42 flagged '{cond or code}' ({status}) — code not parsable, coder verify."})
                    continue
                findings.append({
                    "kind": "history" if status == "history" else "candidate",
                    "code": code, "condition": cond, "evidence": quote,
                    "source": f"med42 ({model.split(':')[0]})", "llm_status": status,
                })
            for c in parsed.get("clarifications", [])[:10]:
                findings.append({"kind": "llm_prompt", "note": str(c)[:300]})
            for s in parsed.get("signals", [])[:10]:
                findings.append({"kind": "llm_prompt", "note": str(s)[:300]})
            return f"med42 ({model})", findings, None
        except (urllib.error.URLError, TimeoutError, OSError, ValueError, json.JSONDecodeError) as e:
            last_err = f"{model}: {e.__class__.__name__}: {e}"
    return "rule-based only (fallback)", [], last_err


# --------------------------------------------------------------------------
# Merge + assemble
# --------------------------------------------------------------------------
def merge_findings(rule_findings, llm_findings, ref):
    candidates, gaps, prompts, traps, histories, notes = [], [], [], [], [], []
    cand_key = {}
    for f in rule_findings:
        if f["kind"] == "candidate":
            if f.get("unmapped"):
                key = ("unmapped", f["code"])
            else:
                key = ("hcc", f["hcc"], f["code"])
            if key in cand_key:
                continue
            cand_key[key] = f
            candidates.append(f)
        elif f["kind"] == "gap":
            gaps.append(f["note"])
        elif f["kind"] == "signal":
            prompts.append(f["note"])
        elif f["kind"] == "trap":
            traps.append(f)
        elif f["kind"] == "history":
            histories.append(f)
        elif f["kind"] == "note":
            notes.append(f)
    # LLM additions — never override reference RAF, never duplicate by HCC
    for f in llm_findings:
        if f["kind"] == "candidate":
            f["code"] = canon(f["code"])
            row = ref["code_map"].get(f["code"])
            if row:
                f.update({"hcc": row["hcc"], "hcc_desc": row["hcc_desc"],
                          "raf": row["raf"], "unmapped": False,
                          "condition": row["desc"], "note": ""})
                key = ("hcc", row["hcc"], f["code"])
            else:
                f.update({"hcc": None, "hcc_desc": None, "raf": None,
                          "unmapped": True, "note": "no reference mapping — coder verify"})
                key = ("unmapped", f["code"])
            if key in cand_key:
                # enrich evidence only
                prev = cand_key[key]
                if f.get("evidence") and f["evidence"] not in prev.get("evidence", ""):
                    prev["evidence"] = f"{prev.get('evidence','')} | med42: {f['evidence']}".strip(" |")
            else:
                cand_key[key] = f
                candidates.append(f)
        elif f["kind"] == "history":
            histories.append({"condition": f["condition"], "note": "Med42: chart says history — clarify active vs history.", "evidence": f.get("evidence", "")})
        elif f["kind"] == "llm_prompt":
            prompts.append(f["note"])
        elif f["kind"] == "llm_note":
            notes.append(f)
    return candidates, gaps, prompts, traps, histories, notes


# --------------------------------------------------------------------------
# Output
# --------------------------------------------------------------------------
def render_text(candidates, gaps, prompts, traps, histories, notes, bonuses,
                lane, llm_error, chart_len):
    lines = []
    w = 100
    lines.append("=" * w)
    lines.append(BANNER)
    lines.append("=" * w)
    lines.append(f"ENGINE LANE: {lane}")
    if llm_error:
        lines.append(f"LLM NOTE: {llm_error}")
    lines.append(f"CHART: {chart_len} chars analyzed | Reference: CMS-HCC V28 workbook sidecar")
    lines.append("-" * w)
    lines.append("CANDIDATES  (code + HCC + RAF + evidence — every row DRAFT):")
    lines.append("-" * w)
    if candidates:
        for c in candidates:
            raf = c.get("raf") or "—"
            hcc = c.get("hcc") or "NO-V28-HCC"
            hcc_desc = c.get("hcc_desc") or ""
            ev = c.get("evidence") or ""
            note = f"  \u26a0 {c['note']}" if c.get("note") else ""
            lines.append(f"  [DRAFT] {c['code']:<9} {hcc:<11} RAF {raf:<6} {hcc_desc}")
            lines.append(f"          condition: {c.get('condition','')}  (source: {c.get('source','rule')})")
            if ev:
                lines.append(f"          evidence: \"{ev}\"")
            if note:
                lines.append(note)
    else:
        lines.append("  (none)")
    lines.append("-" * w)
    lines.append("GAPS  (missing specificity / documentation):")
    for g in gaps:
        lines.append(f"  - {g}")
    if not gaps:
        lines.append("  (none)")
    lines.append("-" * w)
    lines.append("PROMPTS  (provider-review asks — never silent confirmations):")
    for p in prompts:
        lines.append(f"  - {p}")
    if not prompts:
        lines.append("  (none)")
    lines.append("-" * w)
    if traps:
        lines.append("TRAP NOTES  (V28 — no payment HCC unless noted):")
        for t in traps:
            lines.append(f"  - {t['condition']}: {t['note']}")
        lines.append("-" * w)
    if histories:
        lines.append("HISTORY vs ACTIVE  (history never coded as active):")
        for h in histories:
            lines.append(f"  - {h['condition']}: {h['note']}")
        lines.append("-" * w)
    if bonuses:
        lines.append("INTERACTION BONUSES  (reference estimates — APPROXIMATE):")
        for b in bonuses:
            lines.append(f"  - {b['term']}: {b['approx_bonus']} — {b['note']}")
        lines.append("-" * w)
    if notes:
        lines.append("NOTES:")
        for n in notes:
            lines.append(f"  - {n.get('condition','')}: {n['note']}")
        lines.append("-" * w)
    lines.append(f"STATUS: {STATUS_LABEL}")
    lines.append("RAF values are reference estimates — verify against current CMS before any payment decision.")
    lines.append("=" * w)
    return "\n".join(lines)


def render_json(candidates, gaps, prompts, traps, histories, notes, bonuses,
                lane, llm_error, chart_len):
    return json.dumps({
        "engine": "nura-coding-agent",
        "lane": lane,
        "llm_error": llm_error,
        "chart_chars": chart_len,
        "candidates": candidates,
        "gaps": gaps,
        "prompts": prompts,
        "trap_notes": traps,
        "history_notes": histories,
        "notes": notes,
        "interaction_bonuses": bonuses,
        "status": STATUS_LABEL,
        "compliance": {
            "read_only": True,
            "no_emr_writes": True,
            "provider_approval_required": True,
            "raf_values_approximate": True,
        },
    }, indent=2)


# --------------------------------------------------------------------------
# main
# --------------------------------------------------------------------------
def main(argv=None):
    ap = argparse.ArgumentParser(
        description="NURA Coding Agent — MA RAF/HCC V28 decision support (DRAFT only).",
        epilog="Read-only. Output = candidates + gaps + prompts + DRAFT label. No EMR writes.")
    ap.add_argument("--chart", help="encounter/chart text (else stdin)")
    ap.add_argument("--chart-file", help="path to chart text file")
    ap.add_argument("--json", action="store_true", help="JSON output")
    ap.add_argument("--no-llm", action="store_true", help="skip the Med42/Ollama pass")
    ap.add_argument("--ollama", default=DEFAULT_OLLAMA,
                    help=f"Ollama base URL (default {DEFAULT_OLLAMA})")
    ap.add_argument("--model", default=None,
                    help="Ollama model (default: med42:latest, then biomistral)")
    ap.add_argument("--llm-timeout", type=float, default=LLM_TIMEOUT,
                    help=f"LLM request timeout seconds (default {LLM_TIMEOUT})")
    ap.add_argument("--ref", default=DEFAULT_REF, help="reference JSON sidecar path")
    ap.add_argument("--self-test", action="store_true",
                    help="run the built-in sample encounter and exit")
    args = ap.parse_args(argv)

    # ---- chart in ----
    if args.self_test:
        chart = SAMPLE_ENCOUNTER
    elif args.chart_file:
        with open(args.chart_file, "r", encoding="utf-8", errors="replace") as f:
            chart = f.read()
    elif args.chart:
        chart = args.chart
    elif not sys.stdin.isatty():
        chart = sys.stdin.read()
    else:
        ap.error("no chart provided (use --chart, --chart-file, or stdin)")

    ref = load_reference(args.ref)
    t0 = time.time()

    # ---- rule-based lane (always) ----
    findings = []
    for matcher in DOMAIN_MATCHERS:
        findings.extend(matcher(chart, ref))
    findings.extend(scan_exact_codes(chart, ref))
    findings.extend(scan_traps(chart))

    # ---- Med42 lane (when reachable) ----
    lane, llm_findings, llm_error = "rule-based only", [], None
    if not args.no_llm:
        models = [args.model] if args.model else DEFAULT_MODELS
        lane, llm_findings, llm_error = med42_pass(chart, args.ollama, models, args.llm_timeout)
        if llm_findings:
            lane = f"{lane} + rule-based"
        else:
            lane = f"rule-based only (Med42 unavailable)"
    else:
        lane = "rule-based only (--no-llm)"

    candidates, gaps, prompts, traps, histories, notes = merge_findings(
        findings, llm_findings, ref)

    # ---- MEAT check per candidate against the actual chart ----
    for c in candidates:
        meat = meat_check(chart, c)
        if meat:
            gaps.append(meat)

    # dedupe gaps/prompts, preserve order
    gaps = list(dict.fromkeys(gaps))
    prompts = list(dict.fromkeys(prompts))

    bonuses = interaction_bonuses(candidates)
    chart_len = len(chart)

    if args.json:
        print(render_json(candidates, gaps, prompts, traps, histories, notes,
                          bonuses, lane, llm_error, chart_len))
    else:
        print(render_text(candidates, gaps, prompts, traps, histories, notes,
                          bonuses, lane, llm_error, chart_len))
    return 0


SAMPLE_ENCOUNTER = (
    "ENCOUNTER NOTE (synthetic test case)\n"
    "72-year-old male, established patient, follow-up.\n"
    "Assessment/Plan:\n"
    "1. Type 2 diabetes mellitus (E11.9), on metformin 1000 mg BID. A1c 7.2% — "
    "improving. Continue, recheck A1c in 3 months.\n"
    "2. Chronic kidney disease stage 3b (N18.32), eGFR 38, on lisinopril 10 mg "
    "daily. Monitor BMP q6 months.\n"
    "3. Chronic systolic congestive heart failure (I50.22), EF 35% on last echo, "
    "NYHA class II, on furosemide 40 mg daily and metoprolol succinate 50 mg.\n"
    "4. Hypertension — controlled on lisinopril.\n"
    "Problem list: DM2, CKD3b, CHF (systolic, chronic), HTN.\n"
    "Follow up in 3 months. Continue current meds."
)

if __name__ == "__main__":
    sys.exit(main())
