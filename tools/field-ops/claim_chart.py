#!/usr/bin/env python3
"""
claim_chart.py — Patent Claim-Chart + Design-Around Analyzer (NURA internal, original)

Purpose: safely ingest a competitor patent claim and (a) map it element-by-element
against a NURA feature, (b) return a binary all-elements verdict, (c) flag the
specific element(s) to VARY to reach design-around/whitespace. Replaces the
"X% rule" myth with an evidence-based chart.

This is NOT legal advice. It is an engineering FTO/prior-art triage helper.
Any proximity question routes to LEXA / outside counsel before code.

Usage:
    python3 claim_chart.py --claim "<claim text>" --feature "<feature text>" [--json]
"""
import argparse, sys, json, re

EXACT   = "MATCH"
PARTIAL = "PARTIAL"
ABSENT  = "ABSENT"

COMMON_SYNONYMS = {
    "near-eye display": ["head-mounted", "glasses", "eyewear", "ar glasses", "hud", "visor"],
    "in-plane illuminator": ["side-firing led", "edge-lit led", "in-plane light source", "flat led"],
    "glint": ["reflection", "corneal reflection", "specular return", "pupil glint"],
    "gaze": ["eye direction", "looking at", "view direction", "attention point"],
    "corrective lens": ["prescription lens", "dioptric element", "corrective optic"],
    "waveguide": ["lightguide", "optical guide", "light path", "holographic element"],
    "processor": ["controller", "cpu", "compute"],
    "sensor": ["camera", "detector", "transducer"],
    "patient health record": ["ehr", "emr", "chart", "encounter", "history"],
    "safety mode": ["safe state", "failsafe", "restrictive mode", "hold state"],
}

def tokenify(s):
    return set(re.findall(r"[a-z0-9]+", s.lower()))

def element_terms(elem):
    """Split a claim element phrase into the key technical terms to look for."""
    toks = tokenify(elem)
    # drop pure stop-words to improve signal
    stop = {"a","an","the","of","to","in","on","for","and","or","with","at","by",
            "is","are","be","that","said","means","coupled","configured","adapted",
            "positioned","wherein","thereof","such","this","from","into","as"}
    return toks - stop

def map_elements(claim_elements, feature, synonyms=None):
    syn = dict(COMMON_SYNONYMS)
    if synonyms:
        syn.update(synonyms)
    feat_toks = tokenify(feature)
    feat_syn = set(feat_toks)
    for k, vals in syn.items():
        for v in vals:
            feat_syn |= tokenify(v)
    chart = []
    for i, elem in enumerate(claim_elements, 1):
        terms = element_terms(elem)
        if not terms:
            continue
        hits = terms & feat_toks
        # fuzzy: also count if the phrase's head noun is present
        head = terms & set(tokenify(elem.split()[-1])) if elem.split() else set()
        if hits or head:
            # exact-ish: phrase core present
            if len(hits) >= max(1, int(len(terms)*0.6)):
                verdict = EXACT
            else:
                verdict = PARTIAL
        else:
            verdict = ABSENT
        chart.append({
            "element#": i,
            "claim_element": elem,
            "verdict": verdict,
            "matched_terms": sorted(hits),
            "note": "vary this element to design-around" if verdict in (PARTIAL, ABSENT) else "met"
        })
    return chart

def overall(chart):
    if not chart:
        return "NO_ELEMENTS", []
    met = [c for c in chart if c["verdict"] == "MATCH"]
    notmet = [c for c in chart if c["verdict"] in ("PARTIAL", "ABSENT")]
    if not notmet:
        return "ALL_ELEMENTS_MET -> INFRINGEMENT RISK (design-around ONE claim element)", []
    return "WHITESPACE / DESIGN-AROUND -> vary these element(s):", notmet

def cmd(args):
    claim_elements = [e.strip() for e in re.split(r";\s*|\n", args.claim) if e.strip()]
    chart = map_elements(claim_elements, args.feature)
    verdict, notmet = overall(chart)
    out = {
        "claim_elements": len(claim_elements),
        "verdict": verdict,
        "design_around_elements": [c["claim_element"] for c in notmet],
        "chart": chart,
    }
    if args.json:
        print(json.dumps(out, indent=2))
    else:
        print(f"ELEMENTS: {out['claim_elements']}")
        print(f"VERDICT:  {verdict}")
        if out["design_around_elements"]:
            print("DESIGN-AROUND: change one of:")
            for el in out["design_around_elements"]:
                print(f"   - {el}")
        for c in chart:
            print(f"   [{c['element#']:02d}] {c['verdict']:8s} {c['claim_element'][:60]}")
    return 0

def selftest():
    """Prove the tool: Meta in-plane eye-tracking claim vs a NURA clinical-HUD feature."""
    claim = (
        "a near-eye display comprising an in-plane illuminator; "
        "an eye-tracking camera configured to capture an image of the eye and a glint; "
        "a corrective lens assembly; a processor; a waveguide"
    )
    # NURA feature: a provider HUD that does NOT use in-plane illumination or glint gaze
    feature = ("Head-mounted clinical decision-HUD for providers. Uses a paired handheld phone as "
               "the display. No in-lens illumination, no glint-based eye tracking. Reads the patient "
               "chart (EHR) and a processor to surface care gaps. No waveguide optics.")
    chart = map_elements(
        [c.strip() for c in re.split(r";\s*|\n", claim) if c.strip()],
        feature)
    verdict, notmet = overall(chart)
    print("[SELFTEST] claim elements:", len(chart))
    print("[SELFTEST] verdict:", verdict)
    if notmet:
        print("[SELFTEST] design-around candidates:")
        for c in notmet:
            print("[SELFTEST]   -", c["claim_element"])
    # assertions: NURA feature must NOT read on the optical eye-tracking elements
    assert verdict.startswith("WHITESPACE"), "expected whitespace verdict"
    assert any("illuminator" in c["claim_element"].lower() or "glint" in c["claim_element"].lower()
               for c in notmet), "expected illuminator/glint to be the design-around lever"
    print("[SELFTEST] PASS: NURA clinical-HUD avoids the claimed optics; illuminator/glint = design-around lever")
    return 0

if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "--selftest":
        sys.exit(selftest())
    p = argparse.ArgumentParser(description="Patent claim-chart + design-around analyzer")
    p.add_argument("--claim", required=True, help="Semicolon/newline-separated claim elements")
    p.add_argument("--feature", required=True, help="NURA feature/capability description")
    p.add_argument("--json", action="store_true", help="output JSON")
    sys.exit(cmd(p.parse_args()))
