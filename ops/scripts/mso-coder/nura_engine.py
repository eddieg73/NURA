#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
NURA ENGINE WRAPPER — the MSO Coder's reuse of the existing decision-support engine
=====================================================================================
Loads /opt/data/profiles/nura/scripts/nura-coding-agent.py via importlib (the
IMPORT/wrap, not a copy) and exposes one pipeline entry point used by
mso-coder-api.py, mia.py and queue.py.

COMPLIANCE (unchanged from the engine's doctrine):
  * Decision SUPPORT only — NEVER autonomous diagnosis.
  * Every output carries the DRAFT — PROVIDER APPROVAL REQUIRED label.
  * READ-ONLY toward production data: no writes to OpenEMR/Perfex/CarePilot,
    no PHI egress. The only network egress is the local Ollama (Med42) lane.
"""
import importlib.util
import os
import sys

ENGINE_PATH = os.path.join(
    os.path.dirname(os.path.abspath(__file__)), "..", "nura-coding-agent.py"
)

_engine = None


def get_engine():
    """Import the existing engine once per process (importlib — no copy)."""
    global _engine
    if _engine is None:
        spec = importlib.util.spec_from_file_location("nura_coding_agent", ENGINE_PATH)
        mod = importlib.util.module_from_spec(spec)
        sys.modules["nura_coding_agent"] = mod  # allow pickle-ish introspection
        spec.loader.exec_module(mod)
        _engine = mod
    return _engine


def analyze_chart(chart, use_llm=True, ollama_url=None, models=None,
                  timeout=None, ref_path=None):
    """
    The full engine pipeline: chart text IN -> structured findings OUT.

    Returns a dict:
      {
        "ref":          the loaded V28 reference (indexed),
        "candidates":   [ {kind, code, hcc, hcc_desc, raf, evidence, condition,
                           note, source, unmapped} ],
        "gaps":         [str],   "prompts": [str],  "traps": [ {condition,note} ],
        "histories":    [..],    "notes":   [..],
        "interaction_bonuses": [ {term, approx_bonus, note} ],
        "lane":         str,     "llm_error": str|None,  "chart_chars": int,
      }
    """
    eng = get_engine()
    ref = eng.load_reference(ref_path or eng.DEFAULT_REF)

    findings = []
    for matcher in eng.DOMAIN_MATCHERS:
        findings.extend(matcher(chart, ref))
    findings.extend(eng.scan_exact_codes(chart, ref))
    findings.extend(eng.scan_traps(chart))

    lane, llm_findings, llm_error = "rule-based only", [], None
    if use_llm:
        url = ollama_url or eng.DEFAULT_OLLAMA
        models = models or eng.DEFAULT_MODELS
        timeout = timeout or eng.LLM_TIMEOUT
        lane, llm_findings, llm_error = eng.med42_pass(chart, url, models, timeout)
        if llm_findings:
            lane = f"{lane} + rule-based"
        else:
            lane = "rule-based only (Med42 unavailable)"

    candidates, gaps, prompts, traps, histories, notes = eng.merge_findings(
        findings, llm_findings, ref)

    # MEAT check per candidate against the actual chart
    for c in candidates:
        meat = eng.meat_check(chart, c)
        if meat:
            gaps.append(meat)
    gaps = list(dict.fromkeys(gaps))
    prompts = list(dict.fromkeys(prompts))

    return {
        "ref": ref,
        "candidates": candidates,
        "gaps": gaps,
        "prompts": prompts,
        "traps": traps,
        "histories": histories,
        "notes": notes,
        "interaction_bonuses": eng.interaction_bonuses(candidates),
        "lane": lane,
        "llm_error": llm_error,
        "chart_chars": len(chart),
    }


if __name__ == "__main__":  # quick smoke test (no args needed)
    eng = get_engine()
    print(f"engine loaded from: {ENGINE_PATH}")
    print(f"reference map entries: {len(eng.load_reference(eng.DEFAULT_REF)['code_map'])}")
    out = analyze_chart(eng.SAMPLE_ENCOUNTER, use_llm=False)
    print(f"rule-based lane: {out['lane']} | candidates: {len(out['candidates'])}")
    for c in out["candidates"]:
        print(f"  {c['code']} {c.get('hcc')} raf={c.get('raf')} :: {c.get('condition')}")
