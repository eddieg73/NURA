#!/usr/bin/env python3
"""NURA Diagnostic Engine — ranked differential (decision-support, provider-gated).
Input: age/sex, presentation, findings, labs. Output: most-likely dx + differential
with likelihood, reasoning, red flags, recommended workup — grounded in the
local Med42 model + the DocsGPT textbook RAG (fallback-graceful).
THE LABELS: "DIFFERENTIAL — decision-support. The provider confirms the diagnosis."
Usage: python3 nura-dx.py '{"age":68,"sex":"M","presentation":"acute chest pain, dyspnea","findings":"S1Q3T3, JVD","labs":"troponin elevated"}'
"""
import sys, json, urllib.request, urllib.error, subprocess

def local_llm(prompt, model="med42", timeout=240):
    body = json.dumps({"model": model, "prompt": prompt, "stream": False}).encode()
    req = urllib.request.Request("http://127.0.0.1:11434/api/generate", data=body,
                                 headers={"Content-Type": "application/json"})
    try:
        r = urllib.request.urlopen(req, timeout=timeout)
        return json.loads(r.read()).get("response", "").strip()
    except Exception as e:
        return f"[local model unavailable: {str(e)[:60]}]"

def docsgpt_ground(question):
    """Textbook grounding via the DocsGPT RAG (Clinic :7091). Graceful on failure.
    Runs over SSH (no tunnel needed; the self-signed-avoidance path)."""
    try:
        body = json.dumps({"question": question, "api_key": "REDACTED"})
        cmd = f"curl -s -m 150 -X POST http://127.0.0.1:7091/api/answer -H 'Content-Type: application/json' -d '{body}'"
        r = subprocess.run(["ssh", "-o", "BatchMode=yes",
                            "-i", "/opt/data/profiles/nura/home/.ssh/id_nura_clean",
                            "root@72.61.71.211", cmd],
                           capture_output=True, text=True, timeout=170)
        d = json.loads(r.stdout or "{}")
        return (d.get("answer") or "")[:600]
    except Exception as e:
        return f"[textbook RAG unavailable: {str(e)[:60]}]"

SYSTEM = """You are NURA, a clinical decision-support engine. Given the case, produce a RANKED DIFFERENTIAL:
JSON: {"most_likely": {"dx": "...", "likelihood": "high|moderate|low", "why": "..."},
"differential": [{"dx": "...", "likelihood": "...", "why": "..."} up to 4],
"red_flags": [...], "recommended_workup": [...],
"label": "DIFFERENTIAL - decision-support. The provider confirms the diagnosis. Never a final diagnosis."}
Base the ranking on pathophysiology + the case specifics. Be explicit about what the case LACKS. JSON only."""

def dx(case):
    prompt = f"{SYSTEM}\n\nCase: {json.dumps(case)}"
    raw = local_llm(prompt, model="med42")
    try:
        raw = raw.strip().lstrip("```json").rstrip("```").strip()
        d = json.loads(raw)
    except json.JSONDecodeError:
        d = {"structured_raw": raw[:800]}
    d["textbook_grounding"] = docsgpt_ground(
        f"What textbook features distinguish {case.get('presentation','')}? Key differential considerations.")
    return d

if __name__ == "__main__":
    case = json.loads(sys.argv[1]) if len(sys.argv) > 1 else {}
    print(json.dumps(dx(case), indent=2))
