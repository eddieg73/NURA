#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
MSO CODER API — Phase 1 (Medicare Advantage MSO Coder Workspace)
=================================================================
FastAPI service for the MSO dashboard (CarePilot integration target).

Endpoints:
  POST /review          chart JSON/text -> the spec's expected outputs:
                          diagnosis recommendations (ICD-10 + HCC + confidence
                          + evidence), RAF impact (before/after/delta), MEAT
                          compliance validation, audit record.
  POST /mia/ask         MIA — the AI Coder Assistant (see mia.py)
  GET  /mia/            MIA info + example queries
  POST /queue/submit    review + enqueue into the priority queue (queue.py)
  GET  /queue           priority-ordered queue (PHI-stripped)
  GET  /queue/metrics   queue metrics counters
  GET  /audit           in-memory audit trail summaries (no chart text)
  GET  /health          service + engine + Ollama lane status

DOCTRINE (non-negotiable):
  * Every output is DRAFT — PROVIDER APPROVAL REQUIRED.
  * Never invent diagnoses; only recommend what the chart documents.
  * No production data writes: in-memory audit/queue only. No OpenEMR/
    Perfex/CarePilot calls. PHI-stripped test data only (PHI screen rejects
    SSN/phone/MRN/email patterns with HTTP 422).
  * RAF values are reference estimates — verify against current CMS.
"""
import hashlib
import os
import re
import sys
import threading
import time
import uuid
from collections import deque
from datetime import datetime, timezone

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, SCRIPT_DIR)

import nura_engine          # noqa: E402  (the reuse of nura-coding-agent.py)
from mia import build_mia_router   # noqa: E402
from queue import get_queue        # noqa: E402

STATUS_LABEL = "DRAFT \u2014 PROVIDER APPROVAL REQUIRED"
APP_NAME = "MSO Coder Workspace API (Phase 1)"
APP_VERSION = "0.1.0-phase1"

app = FastAPI(title=APP_NAME, version=APP_VERSION,
              description="Medicare Advantage MSO coding decision support. "
                          "All outputs DRAFT — provider approval required.")

# ---------------------------------------------------------------------------
# PHI screen — Phase 1 accepts PHI-stripped test data only
# ---------------------------------------------------------------------------
PHI_PATTERNS = [
    ("ssn", re.compile(r"\b\d{3}-\d{2}-\d{4}\b")),
    ("phone", re.compile(r"\b\(?\d{3}\)?[-.\s]\d{3}[-.\s]\d{4}\b")),
    ("mrn", re.compile(r"\bMRN\s*[:#]?\s*\d{4,}\b", re.I)),
    ("email", re.compile(r"\b[\w.+-]+@[\w-]+\.[\w.]+\b")),
]


def phi_screen(chart_text):
    hits = []
    for kind, pat in PHI_PATTERNS:
        m = pat.search(chart_text or "")
        if m:
            hits.append((kind, m.group(0)))
    return hits


# ---------------------------------------------------------------------------
# In-memory audit store (no production data writes; no chart text retained)
# ---------------------------------------------------------------------------
_AUDIT_LOCK = threading.Lock()
_AUDIT_LOG = deque(maxlen=500)


def store_audit(record):
    with _AUDIT_LOCK:
        _AUDIT_LOG.appendleft(record)
    return record


# ---------------------------------------------------------------------------
# Confidence scoring (deterministic, explainable)
# ---------------------------------------------------------------------------
def compute_confidence(cand, meat_status, chart_text=""):
    if cand.get("unmapped"):
        base, why = 0.45, "no V28 reference mapping — coder verify"
    else:
        ev = cand.get("evidence") or ""
        code = cand.get("code") or ""
        # literal ICD-10 in the chart (canonical "E119" matches "E11.9" too)
        if len(code) > 3:
            lit = re.compile(r"\b" + re.escape(code[:3]) + r"\.?"
                             + re.escape(code[3:]) + r"\b")
        else:
            lit = re.compile(r"\b" + re.escape(code) + r"\b")
        exact_code = " in chart" in ev or bool(lit.search(chart_text or ""))
        llm_support = "med42" in ev
        if exact_code and llm_support:
            base, why = 0.97, "exact ICD-10 in chart + Med42 corroboration"
        elif exact_code:
            base, why = 0.90, "exact ICD-10 code present in chart"
        elif llm_support:
            base, why = 0.70, "Med42 extraction only (no literal code in chart)"
        else:
            base, why = 0.75, "rule-based domain match"
    if meat_status == "gap":
        base -= 0.15
        why += "; MEAT gap"
    elif meat_status == "partial":
        base -= 0.05
        why += "; MEAT partial"
    elif meat_status == "met":
        base += 0.02
        why += "; MEAT met"
    base = max(0.05, min(0.98, base))
    level = "high" if base >= 0.85 else ("medium" if base >= 0.60 else "low")
    return round(base, 2), level, why


# ---------------------------------------------------------------------------
# Core review pipeline (reused by POST /review and POST /queue/submit)
# ---------------------------------------------------------------------------
def _resolve_codes(codes, ref):
    """Canonicalize + resolve codes against the V28 reference."""
    eng = nura_engine.get_engine()
    out = []
    for raw in codes:
        code = eng.canon(raw)
        row = ref["code_map"].get(code)
        if row:
            out.append({"code": code, "hcc": row["hcc"], "hcc_desc": row["hcc_desc"],
                        "raf": row["raf"], "desc": row["desc"]})
        else:
            out.append({"code": code, "hcc": None, "hcc_desc": None, "raf": None,
                        "desc": "not in V28 reference — coder verify"})
    return out


def _suspected_from_prompts(prompts, ref):
    """Map engine signal prompts to suspected-HCC entries (estimate only)."""
    suspected = []
    for p in prompts:
        m = re.search(r"consider evaluating for\s+(.+?)(?:[.\u2014-]|$)", p, re.I)
        if not m:
            continue
        cond = m.group(1).strip().rstrip(" -—")
        raf_est = None
        hcc_est = None
        for hcc_key, row in sorted(ref["quick_by_hcc"].items()):
            if cond.lower() in (row["condition"] or "").lower():
                hcc_est, raf_est = hcc_key, row["raf"]
                break
        suspected.append({
            "condition": cond,
            "note": p,
            "flag": "suspected",
            "hcc_estimate": hcc_est,
            "raf_estimate": raf_est,
            "action": "provider review — never code without a documented diagnosis",
        })
    return suspected


def _unrecaptured(prior_year_codes, current_resolved, recommended, chart, ref):
    """Prior-year codes absent from current codes AND absent from the chart's
    documented evidence -> recapture flags for provider review."""
    current_hccs = {r["hcc"] for r in current_resolved if r["hcc"]}
    recommended_hccs = {c.get("hcc") for c in recommended if c.get("hcc")}
    current_code_set = {r["code"] for r in current_resolved}
    eng = nura_engine.get_engine()
    out = []
    for raw in prior_year_codes:
        code = eng.canon(raw)
        row = ref["code_map"].get(code)
        hcc = row["hcc"] if row else None
        evidenced = re.search(re.escape(raw), chart, re.I) is not None
        if (code in current_code_set) or (hcc and hcc in recommended_hccs) or evidenced:
            continue  # recaptured or evidenced this year
        if hcc and hcc in current_hccs:
            continue
        if row:
            out.append({
                "code": code, "hcc": hcc, "hcc_desc": row["hcc_desc"],
                "raf_estimate": row["raf"], "flag": "unrecaptured",
                "note": "Prior-year code not documented in this chart and not in "
                        "current codes — provider review for recapture.",
            })
        else:
            trap_note = ""
            if code == "I252":
                trap_note = ("V28 trap: old MI alone no longer generates a payment "
                             "HCC — document active CAD with angina (I25.11x) if present.")
            out.append({
                "code": code, "hcc": None, "hcc_desc": None, "raf_estimate": None,
                "flag": "unrecaptured",
                "note": ("Prior-year code absent this year. " + trap_note).strip(),
            })
    return out


def _meat_per_recommendation(chart, cand):
    eng = nura_engine.get_engine()
    n = eng.norm(chart)
    met, missing = [], []
    for letter, pat in eng.MEAT_MARKERS.items():
        (met if re.search(pat, n, re.I) else missing).append(letter)
    status = "met" if len(missing) == 0 else ("partial" if len(missing) <= 1 else "gap")
    return status, met, missing


def run_review(chart_text, current_codes, prior_year_codes, coder_id,
               patient_ref, use_llm=True, ollama_url=None, meta=None):
    """Chart in -> full spec-shaped review payload. DRAFT on every section."""
    eng = nura_engine.get_engine()
    ref = eng.load_reference(eng.DEFAULT_REF)

    out = nura_engine.analyze_chart(chart_text, use_llm=use_llm,
                                    ollama_url=ollama_url)
    now = datetime.now(timezone.utc).isoformat(timespec="seconds")

    # ---- 1) Diagnosis recommendations: ICD-10 + HCC + confidence + evidence
    recommendations = []
    raf_hcc_seen = set()
    for cand in out["candidates"]:
        meat_status, met, missing = _meat_per_recommendation(chart_text, cand)
        conf, level, why = compute_confidence(cand, meat_status, chart_text)
        rec = {
            "icd10": cand["code"],
            "hcc": cand.get("hcc"),
            "hcc_desc": cand.get("hcc_desc"),
            "raf": cand.get("raf"),
            "condition": cand.get("condition"),
            "confidence": conf,
            "confidence_level": level,
            "confidence_rationale": why,
            "evidence": cand.get("evidence", ""),
            "source": cand.get("source", "rule"),
            "meat": {"status": meat_status, "met": met, "missing": missing},
            "draft": True,
            "provider_approval_required": True,
        }
        if cand.get("unmapped"):
            rec["note"] = "No V28 payment-HCC mapping in the reference — coder verify."
        elif cand.get("note"):
            rec["note"] = cand["note"]
        if cand.get("hcc") and cand["hcc"] not in raf_hcc_seen:
            raf_hcc_seen.add(cand["hcc"])
        recommendations.append(rec)

    # ---- 2) RAF impact: before / after / delta
    current_resolved = _resolve_codes(current_codes, ref)
    raf_before = round(sum(float(r["raf"]) for r in current_resolved
                           if r["raf"] and r["hcc"]), 3)
    raf_after = round(sum(float(c["raf"]) for c in out["candidates"]
                          if c.get("raf") and c.get("hcc")
                          and c["hcc"] in raf_hcc_seen), 3)
    # one RAF per HCC group (simple max — full V28 hierarchy logic is V2)
    raf_after = round(sum(max(float(c["raf"]) for c in out["candidates"]
                              if c.get("raf") and c.get("hcc") == h)
                          for h in raf_hcc_seen), 3)
    raf_delta = round(raf_after - raf_before, 3)

    unrecaptured = _unrecaptured(prior_year_codes, current_resolved,
                                 out["candidates"], chart_text, ref)
    suspected = _suspected_from_prompts(out["prompts"], ref)

    raf_impact = {
        "before": raf_before,
        "after": raf_after,
        "delta": raf_delta,
        "approximate": True,
        "hierarchy_note": ("Phase-1 simplification: one RAF per HCC group "
                           "(max coefficient); full V28 hierarchy + count-bonus "
                           "logic is V2. Demographic factors not included."),
        "current_codes_resolved": current_resolved,
        "interaction_bonuses": out["interaction_bonuses"],
        "unrecaptured": unrecaptured,
        "suspected": suspected,
        "draft": True,
    }

    # ---- 3) Compliance validation (MEAT + sufficiency)
    meat_rows = [{
        "icd10": r["icd10"], "hcc": r["hcc"], "condition": r["condition"],
        "meat_status": r["meat"]["status"],
        "met_components": r["meat"]["met"],
        "missing_components": r["meat"]["missing"],
    } for r in recommendations]
    met_n = sum(1 for m in meat_rows if m["meat_status"] == "met")
    compliance = {
        "meat": {
            "per_recommendation": meat_rows,
            "summary": (f"MEAT met for {met_n} of {len(meat_rows)} recommended "
                        f"condition(s)."),
            "meets_meat": bool(meat_rows) and met_n == len(meat_rows),
        },
        "documentation_sufficiency": {
            "suspected_undocumented": suspected,
            "history_vs_active": out["histories"],
            "trap_notes": out["traps"],
        },
        "provider_review_required": True,
        "draft": True,
    }

    # ---- 4) Audit record
    changes = []
    current_set = {r["code"] for r in current_resolved}
    rec_by_code = {r["icd10"]: r for r in recommendations}
    for code in sorted(current_set - set(rec_by_code)):
        row = next((r for r in current_resolved if r["code"] == code), {})
        changes.append({"action": "remove", "code": code, "hcc": row.get("hcc"),
                        "raf": row.get("raf"),
                        "note": "Not documented/recommended in this review — provider confirm."})
    for code in sorted(current_set & set(rec_by_code)):
        r = rec_by_code[code]
        changes.append({"action": "keep", "code": code, "hcc": r["hcc"],
                        "raf": r["raf"], "confidence": r["confidence"]})
    for code in sorted(set(rec_by_code) - current_set):
        r = rec_by_code[code]
        changes.append({"action": "add", "code": code, "hcc": r["hcc"],
                        "raf": r["raf"], "confidence": r["confidence"],
                        "evidence": r["evidence"]})
    for u in unrecaptured:
        changes.append({"action": "recapture-review", "code": u["code"],
                        "hcc": u["hcc"], "raf": u["raf_estimate"],
                        "note": u["note"]})

    audit = {
        "review_id": uuid.uuid4().hex[:12],
        "timestamp_utc": now,
        "coder_id": coder_id,
        "patient_ref": patient_ref,
        "input_sha256": hashlib.sha256(chart_text.encode("utf-8")).hexdigest()[:16],
        "chart_chars": out["chart_chars"],
        "original_codes": [r["code"] for r in current_resolved],
        "recommended_codes": [r["icd10"] for r in recommendations],
        "changes": changes,
        "raf_before": raf_before,
        "raf_after": raf_after,
        "raf_delta": raf_delta,
        "engine_lane": out["lane"],
        "llm_error": out["llm_error"],
        "status": STATUS_LABEL,
        "audit_compliant": True,
        "notes": ["In-memory audit only — no production data writes (Phase 1).",
                  "Chart text is NOT retained; only the SHA-256 prefix is stored."],
    }

    payload = {
        "review_id": audit["review_id"],
        "generated_at_utc": now,
        "coder_id": coder_id,
        "patient_ref": patient_ref,
        "status": STATUS_LABEL,
        "draft": True,
        "diagnosis_recommendations": recommendations,
        "raf_impact": raf_impact,
        "compliance_validation": compliance,
        "provider_review": {
            "gaps": out["gaps"],
            "prompts": out["prompts"],
            "trap_notes": out["traps"],
            "history_notes": out["histories"],
            "notes": out["notes"],
            "draft": True,
        },
        "audit_record": audit,
        "engine": {"lane": out["lane"], "llm_error": out["llm_error"],
                   "chart_chars": out["chart_chars"]},
        "compliance_flags": {
            "read_only": True,
            "no_emr_writes": True,
            "phi_stripped_test_data_only": True,
            "provider_approval_required": True,
            "raf_values_approximate": True,
        },
        "chart_meta": meta or {},
    }
    store_audit({
        "review_id": audit["review_id"], "timestamp_utc": now, "coder_id": coder_id,
        "patient_ref": patient_ref, "input_sha256": audit["input_sha256"],
        "chart_chars": audit["chart_chars"], "raf_delta": raf_delta,
        "n_recommendations": len(recommendations), "lane": out["lane"],
        "status": STATUS_LABEL,
    })
    return payload


# ---------------------------------------------------------------------------
# Request model
# ---------------------------------------------------------------------------
class ReviewRequest(BaseModel):
    chart: str = Field(..., description="Chart/encounter text (PHI-stripped "
                                         "synthetic test data only)")
    current_codes: list = Field(default=[], description="Currently coded ICD-10s "
                                                        "(the RAF 'before')")
    prior_year_codes: list = Field(default=[], description="Last year's codes "
                                                           "(recapture check)")
    coder_id: str = "MSO-CODER"
    patient_ref: str = "SYNTHETIC"
    use_llm: bool = True
    meta: dict = Field(default={})


# ---------------------------------------------------------------------------
# Routes
# ---------------------------------------------------------------------------
@app.get("/")
def root():
    return {"service": APP_NAME, "version": APP_VERSION,
            "status": STATUS_LABEL,
            "endpoints": ["POST /review", "POST /mia/ask", "POST /queue/submit",
                          "GET /queue", "GET /queue/metrics", "GET /audit",
                          "GET /health"],
            "doctrine": "decision support only — never invents diagnoses — "
                        "no production writes — PHI-stripped test data only"}


@app.post("/review")
def review(body: ReviewRequest):
    hits = phi_screen(body.chart)
    if hits:
        raise HTTPException(status_code=422, detail={
            "error": "PHI pattern(s) detected — Phase 1 accepts PHI-stripped "
                     "test data only.",
            "detected": [{"type": t, "value": v} for t, v in hits]})
    if not body.chart.strip():
        raise HTTPException(status_code=422,
                            detail={"error": "empty chart text"})
    return run_review(body.chart, body.current_codes, body.prior_year_codes,
                      body.coder_id, body.patient_ref, use_llm=body.use_llm,
                      meta=body.meta)


@app.post("/queue/submit")
def queue_submit(body: ReviewRequest):
    payload = review(body)
    item = get_queue().submit(payload, patient_ref=body.patient_ref,
                              source="mso-api")
    return {"queue_item": item, "review": payload,
            "status": STATUS_LABEL}


@app.get("/queue")
def queue_view():
    return get_queue().snapshot()


@app.get("/queue/metrics")
def queue_metrics():
    return {"metrics": get_queue().metrics(), "status": STATUS_LABEL}


@app.get("/audit")
def audit_view():
    with _AUDIT_LOCK:
        records = list(_AUDIT_LOG)
    return {"count": len(records), "records": records,
            "note": "Chart text never stored — SHA-256 prefixes only.",
            "status": STATUS_LABEL}


@app.get("/health")
def health():
    ref_entries = 0
    try:
        eng = nura_engine.get_engine()
        ref = eng.load_reference(eng.DEFAULT_REF)
        ref_entries = len(ref["code_map"])
    except Exception as e:
        return {"ok": False, "error": str(e)}
    ollama = False
    try:
        import urllib.request
        with urllib.request.urlopen(eng.DEFAULT_OLLAMA + "/api/tags", timeout=3) as r:
            ollama = r.status == 200
    except Exception:
        ollama = False
    return {"ok": True, "service": APP_NAME, "version": APP_VERSION,
            "engine": "nura-coding-agent (wrapped via importlib)",
            "reference_entries": ref_entries,
            "ollama_lane_reachable": ollama,
            "queue_metrics": get_queue().metrics(),
            "status": STATUS_LABEL}


# MIA router (interactive Q&A)
app.include_router(build_mia_router())


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="127.0.0.1",
                port=int(os.environ.get("MSO_CODER_PORT", "8643")))
