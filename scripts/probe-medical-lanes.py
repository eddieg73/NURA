#!/usr/bin/env python3
"""Probe the four free medical lanes (2026-08-02) — evidence before wiring."""
import json, urllib.request, urllib.error

def probe(name, url, check, label=None):
    try:
        req = urllib.request.Request(url, headers={"User-Agent": "NURA-Hermes/1.0"})
        with urllib.request.urlopen(req, timeout=25) as r:
            body = r.read(4000).decode(errors="ignore")
            ok = check(body)
            print(("PASS " if ok else "FAIL ") + name + (f" ({label})" if label else ""))
            if ok:
                print("     sample:", body[:160].replace("\n", " "))
            return ok
    except Exception as e:
        print("FAIL " + name + f" ({type(e).__name__}: {e})")
        return False

results = []
# 1. DailyMed — official drug labels (SPL)
results.append(probe("DailyMed",
    "https://dailymed.nlm.nih.gov/dailymed/services/v2/spls.json?drug_name=naloxone",
    lambda b: '"spls"' in b or 'setId' in b or 'total' in b))
# 2. RxNorm — drug names/rxcui
results.append(probe("RxNorm",
    "https://rxnav.nlm.nih.gov/REST/rxcui.json?name=epinephrine",
    lambda b: '"rxcui"' in b))
# 3. ClinicalTrials.gov API v2
results.append(probe("ClinicalTrials v2",
    "https://clinicaltrials.gov/api/v2/studies?query.term=cardiac%20arrest&pageSize=1",
    lambda b: '"protocolSection"' in b or '"totalCount"' in b))
# 4. MedlinePlus Connect — patient handouts
results.append(probe("MedlinePlus Connect",
    "https://apps.nlm.nih.gov/medlineplus/services/mpconnect_service.json?mainSearchCriteria.cs=v3.CONCEPTCODE&mainSearchCriteria.c=v3.409586006&informationRecipient=HCP",
    lambda b: 'feed' in b.lower() or 'entry' in b.lower()))
print("RESULT:", "ALL PASS" if all(results) else f"{sum(results)}/4 PASS")
