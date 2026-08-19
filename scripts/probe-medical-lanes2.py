#!/usr/bin/env python3
import json, urllib.request

def probe(name, url, check):
    try:
        req = urllib.request.Request(url, headers={"User-Agent": "NURA-Hermes/1.0"})
        with urllib.request.urlopen(req, timeout=25) as r:
            body = r.read(3000).decode(errors="ignore")
            ok = check(body)
            print(("PASS " if ok else "FAIL ") + name)
            if ok:
                print("     sample:", body[:150].replace("\n", " "))
            return ok
    except Exception as e:
        print("FAIL " + name + f" ({type(e).__name__})")
        return False

r = []
r.append(probe("DailyMed (corrected check)",
    "https://dailymed.nlm.nih.gov/dailymed/services/v2/spls.json?drug_name=naloxone",
    lambda b: '"data"' in b))
r.append(probe("RxNorm (corrected check)",
    "https://rxnav.nlm.nih.gov/REST/rxcui.json?name=epinephrine",
    lambda b: 'rxnormId' in b))
r.append(probe("ClinicalTrials v2",
    "https://clinicaltrials.gov/api/v2/studies?query.term=cardiac%20arrest&pageSize=1",
    lambda b: '"studies"' in b))
r.append(probe("ChEMBL (EBI, keyless)",
    "https://www.ebi.ac.uk/chembl/api/data/molecule/drug.json?limit=1",
    lambda b: 'molecules' in b))
r.append(probe("ClinVar (eutils, keyless)",
    "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esearch.fcgi?db=clinvar&term=BRCA1&retmax=1",
    lambda b: 'Count' in b or 'IdList' in b))
print("RESULT:", f"{sum(r)}/5 PASS")
