#!/usr/bin/env python3
"""Seed the peer-files store from the founder profile — scored honestly.
Self-reported = high conf. Observed behavior = mid. Inferred = low.
Health/psych = unknown/low. No fabrication, no confidence inflation."""
import sys, subprocess

sys.path.insert(0, "/opt/data/scripts")
from peer_files import add

SEED = [
    # --- self-reported / established (high confidence) ---
    ("Eddie is a PA-C (physician assistant, certified)", "self_report", 0.98,
     "stated directly; PA-C credential + clinical faculty roles", "no valid/active PA-C license found"),
    ("Eddie is an EMT-P / flight-paramedic", "self_report", 0.97,
     "stated; EMS/paramedic career + Key Largo Fire Rescue leadership", "credential registry shows no paramedic license"),
    ("Eddie is a private pilot (Part 91) + Part 107 UAV", "self_report", 0.95,
     "stated; aviation + drone work", "no pilot certificate in registry"),
    ("Eddie operates as entrepreneur/portfolio operator (Medisun, Nuratech, Rescue Health, multiple entities)", "self_report", 0.92,
     "stated; multi-entity leadership across profile", "single-employer career documented instead"),
    ("Eddie runs Medisun Health Group as Chief Population Health Officer / Associate Medical Director", "self_report", 0.90,
     "stated; Medisun MA/pop-health work", "no Medisun leadership role found"),
    ("Eddie's professional base is Florida (Tampa Bay/Clearwater + Miami-Dade/Broward)", "observed", 0.85,
     "repeatedly referenced locations across many topics", "documented residence in another state"),
    ("Eddie has an adult son (~22) in nursing school, Navy Nurse Corps pathway", "self_report", 0.88,
     "stated; extensive son logistics/fitness/ODS planning", "no son / different situation"),

    # --- observed behavioral (mid confidence, actively monitored) ---
    ("Eddie prefers dense, implementation-ready, smoke-tested deliverables over advisory prose", "observed", 0.85,
     "repeatedly requested PDFs, SOPs, tables, checklists, verified deploys; rejected abstract/theoretical output", "accepts abstract advisory output as final"),
    ("Eddie rapidly converts uncertainty into investigation + action + correction", "observed", 0.80,
     "repeated pattern in crisis, tech, legal, operations", "frequently waits for certainty before acting"),
    ("Eddie tends to expand scope as more capability becomes visible", "observed", 0.78,
     "repeated expansion: CarePilot, Hermes/MCP, Notion, MIH, radiology, fleet", "consistently kills adjacent initiatives early"),
    ("Eddie uses 'fix everything'-type closure language that expands the surface", "observed", 0.75,
     "many 'fix everything / button it up / last iteration' requests that broadened", "closure requests consistently tighten scope"),

    # --- inferred (low confidence — speculative, do NOT rely on) ---
    ("Eddie is likely ~50-57 (early-to-mid 50s)", "inferred", 0.55,
     "1993 career start + >30 yrs practice + adult son ~22", "documented younger/older age"),
    ("Eddie's income/net worth is high-resource", "inferred", 0.35,
     "multi-entity, capital-intensive healthcare projects", "verified financials show otherwise"),
    ("Eddie is likely single/unmarried", "inferred", 0.20,
     "no reliable evidence either way", "relationship status verified"),

    # --- health/psych (unknown — sensitive, excluded from trusted set) ---
    ("Personal endocrine/labs (cortisol, ACTH, prolactin) results apply to Eddie", "unknown", 0.10,
     "may refer to another person; ambiguous attribution", "verified as Eddie's own results"),
    ("No DSM-5-TR diagnosis is established from conversation", "verified", 0.92,
     "explicitly not a diagnostic interview; the profile itself states no diagnosis", "a formal psychiatric diagnosis is documented"),
]

for claim, src, conf, basis, fals in SEED:
    pf = add(claim, src, conf, basis, fals)
    print(f"{pf['id']}  conf={conf:.2f}  {src:11}  {claim[:55]}")
print("\nDONE")
