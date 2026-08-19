#!/usr/bin/env python3
"""NURA ID Reference — the infectious-disease lane (keyless + local).
Antibiotics/antivirals/antiparasitics: the drug identity (RxNav), the label
data (openFDA), the interactions (RxNav), and the pathogen→therapy guidance
(Med42, the stewardship framing). EVERY output: provider-approval labeled.
Usage: python3 nura-id-ref.py ceftriaxone
       python3 nura-id-ref.py --pathogen "CAP, elderly, renal dose"
"""
import sys, json, urllib.request, urllib.parse

def rxnav_rxcui(name):
    u = f"https://rxnav.nlm.nih.gov/REST/rxcui.json?name={urllib.parse.quote(name)}"
    d = json.loads(urllib.request.urlopen(u, timeout=20).read())
    ids = d.get("idGroup", {}).get("rxnormId", [])
    return ids[0] if ids else None

def rxnav_interactions(rxcui):
    u = f"https://rxnav.nlm.nih.gov/REST/interaction/list.json?rxcuis={rxcui}"
    try:
        d = json.loads(urllib.request.urlopen(u, timeout=20).read())
        pairs = d.get("fullInteractionTypeGroup", [])
        out = []
        for g in pairs:
            for it in g.get("fullInteractionType", []):
                for p in it.get("interactionPair", []):
                    for c in p.get("interactionConcept", []):
                        if c.get("sourceConceptItem", {}).get("id") == str(rxcui):
                            out.append({"interacts_with": c.get("minConceptItem", {}).get("name"),
                                        "severity": it.get("comment", "")[:80]})
        return out[:10]
    except Exception:
        return []

def openfda_label(name):
    u = f"https://api.fda.gov/drug/label.json?search=openfda.brand_name:%22{urllib.parse.quote(name)}%22&limit=1"
    try:
        d = json.loads(urllib.request.urlopen(u, timeout=20).read())
        r = d["results"][0]
        return {"brand": r.get("openfda", {}).get("brand_name", [""])[0],
                "indications": (r.get("indications_and_usage") or [""])[0][:400],
                "warnings": (r.get("warnings") or [""])[0][:200]}
    except Exception:
        return None

def med42_guidance(prompt_text):
    prompt = ("You are NURA ID reference for a licensed PA. Stewardship-framed guidance: "
              "the likely therapy, the dosing considerations, the alternatives, the resistance notes. "
              "Never a final prescription. End with exactly 'DRAFT — PROVIDER APPROVAL REQUIRED.'\n\n"
              + prompt_text)
    try:
        body = json.dumps({"model": "med42", "prompt": prompt, "stream": False,
                           "options": {"num_predict": 700, "temperature": 0.2}}).encode()
        req = urllib.request.Request("http://127.0.0.1:11434/api/generate", data=body,
                                     headers={"Content-Type": "application/json"})
        return json.loads(urllib.request.urlopen(req, timeout=1500).read()).get("response", "").strip()
    except Exception as e:
        return f"[guidance unavailable: {str(e)[:60]}]"

if __name__ == "__main__":
    arg = " ".join(sys.argv[1:])
    out = {}
    if "--pathogen" in arg:
        out["guidance"] = med42_guidance(arg.replace("--pathogen", "").strip())
    else:
        name = arg.strip()
        rxcui = rxnav_rxcui(name)
        out["drug"] = name
        out["rxnorm_id"] = rxcui
        out["label"] = openfda_label(name)
        out["interactions"] = rxnav_interactions(rxcui) if rxcui else []
        out["guidance"] = med42_guidance(f"Drug: {name}. Summarize the standard indications, "
                                         f"the typical adult doses, and the key warnings.")
    out["label"] = out.get("label") or {}
    out["approval"] = "DRAFT — PROVIDER APPROVAL REQUIRED"
    print(json.dumps(out, indent=2))
