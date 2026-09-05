#!/usr/bin/env python3
"""Seed peer files from MY ACTUAL persistent memory (MEMORY.md/USER.md) — the verified
ground truth I hold. Then compare against the external profile's claims."""

import sys, json, os
sys.path.insert(0, "/opt/data/scripts")
import importlib.util
spec = importlib.util.spec_from_file_location("pf", "/opt/data/scripts/peer_files.py")
pf = importlib.util.module_from_spec(spec)
spec.loader.exec_module(pf)

# Clear old seeded files (rebuild from real data)
import glob
for f in glob.glob("/opt/data/peer-files/pf-*.json"):
    os.remove(f)
pf._load_index  # ensure dir exists
os.makedirs("/opt/data/peer-files", exist_ok=True)
with open(pf.INDEX, "w") as f:
    json.dump({"files": [], "seq": 0}, f)

# ---- SEED FROM MY ACTUAL MEMORY (verified / self-reported / operational) ----
# These are facts MY data actually holds. Not the external doc's guesses.
SEED = [
    # Verified via public registry / explicit
    ("Eddie is a PA-C, NPI 1154381580 (Eduardo Garrido PA)", "verified", 0.98,
     "NPI 1154381580 in public registry; USER.md; PA-C credential", "NPI registry shows different/no record"),
    ("Eddie is an EMT-P", "self_report", 0.97,
     "USER.md: 'PA-C, EMT-P'; clinical educator", "no paramedic credential"),
    ("Eddie is a private pilot, Part 91 (PPL+IR)", "self_report", 0.95,
     "MEMORY: 'Aviation: Part 91 pilot (PPL+IR)'; PA-32R-300 + PA-46", "no pilot certificate"),
    ("Eddie is a healthcare executive (Medisun/MA MSO, population health/RAF)", "self_report", 0.95,
     "USER.md: 'owns/operates Medisun MA MSO (Solis/Ensure + CarePilot/eMedical)'", "single-role non-exec documented"),
    ("Eddie's professional base is Florida (Medisun clinics: Little Haiti, North Miami, Broward; Tampa/Clearwater aviation/flight)", "observed", 0.90,
     "MEMORY: Medisun clinics, weather Tampa/Pompano, aviation fields, Mirth/medisun host map", "residence in another state"),
    ("Eddie has a son", "self_report", 0.90,
     "USER.md: 'Has a son'; MEMORY: son in nursing school, Navy Nurse Corps pathway", "no son"),
    ("Eddie is accountable for MA risk/RAF capture (job-critical, MRA 1.088/target 1.30)", "verified", 0.92,
     "MEMORY + USER: Solis MA ~70-79 members, MRA targets, CY2026 V28 phase-in; job-critical", "not accountable / different metric"),
    ("Eddie wants verification evidence before any 'done' — never declare complete untested", "self_report", 0.95,
     "USER.md lines 1,21; MEMORY: ACT-FIRST but evidence-first, verify-before-declare", "accepts unverified claims as done"),
    ("Eddie wants offline-first, approval-gated, auditable, human-controlled systems", "self_report", 0.95,
     "USER.md line 5-6; MEMORY: founder doctrine approval-queue, fail-closed", "wants unfettered autonomy"),
    ("Eddie's communication preference: direct, dense, implementation-ready, minimal noise (SILENT-OK, CRITICAL-ONLY-chat)", "self_report", 0.93,
     "MEMORY 'Founder: SILENT-OK... CRITICAL-ONLY-chat... anti-flood'; USER: CTO briefs preferred", "wants verbose/long-form updates"),
    ("Eddie has a DEA # (MG6963269, renew 09-30) + FL PA license (PA9103256) + NPI", "self_report", 0.90,
     "MEMORY line 'Licenses: DEA MG6963269... FL PA9103256... GA/TN Sept'", "no clinical license"),
    ("Eddie's tech doctrine: local+free-first; MOE; Hermes = one interchangeable runtime", "self_report", 0.92,
     "MEMORY: free-first, nura-free-llm-moe-lane, CTASO one-runtime thesis", "vendor-locked stack"),
    ("Eddie is Musk/Jobs first-principles, 'all signal rapid switching', OODA", "self_report", 0.85,
     "USER.md line 21: 'Musk/Jobs first-principles; all signal rapid switching'", "not a first-principles thinker"),
    # The operational reality my data holds (the external doc UNDERWEIGHTS these)
    ("Eddie operates a real technical stack: OpenEMR, Orthanc, Mirth/OIE, Qdrant, Redis, Docker, B2, n8n, Perfex, Telegram", "verified", 0.95,
     "MEMORY: full stack inventory across dozens of entries; live Mirth/OIE, B2 backups", "no active stack"),
    ("Eddie owns/operates Medisun with 2 EMRs (OpenEMR internal truth + eMedical 2nd), Perfex billing", "self_report", 0.90,
     "MEMORY: sidecar doctrine, Perfex=pay.nuratech.ai, eMedical 2nd EMR", "single-EMR practice"),
    ("Eddie runs CarePilot (population-health/RAF/HEDIS/Stars) — needs provider-approval clinical agents", "self_report", 0.92,
     "MEMORY + USER: CarePilot carepilot.nuratech.ai, provider-gated DRAFT", "non-clinical only"),
    ("Eddie is the founder of NURATECH.ai / NURA (Solis full-risk MA, RATCHET, One-App-All-EMRs)", "self_report", 0.90,
     "MEMORY: Nuratech full-risk MA, PRIME DIRECTIVE, RATCHET, CTASO", "employee of another company"),
    ("Eddie is clinically-licensed and ADVOCATES provider-gated AI (never auto-diagnosis)", "self_report", 0.95,
     "MEMORY: clinical gate NPI/paramedic only, EMR gate DRAFT→provider→final, RadIntel", "auto-final clinical AI"),
]

for claim, src, conf, basis, fals in SEED:
    p = pf.add(claim, src, conf, basis, fals)
    print(f"{p['id']}  {conf:.2f}  {src:11}  {claim[:55]}")
print("\nSEEDED", len(SEED), "from MY actual data")
