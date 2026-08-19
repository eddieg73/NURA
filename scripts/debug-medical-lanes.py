#!/usr/bin/env python3
import urllib.request, urllib.error

urls = {
    "DailyMed": "https://dailymed.nlm.nih.gov/dailymed/services/v2/spls.json?drug_name=naloxone",
    "DailyMed-v2": "https://dailymed.nlm.nih.gov/dailymed/services/v2/spls.json?drug_name=naloxone&pagesize=1",
    "RxNorm": "https://rxnav.nlm.nih.gov/REST/rxcui.json?name=epinephrine",
    "RxNorm-approximate": "https://rxnav.nlm.nih.gov/REST/approximateTerm.json?term=epinephrine",
    "MedlinePlus": "https://apps.nlm.nih.gov/medlineplus/services/mpconnect_service.json?mainSearchCriteria.cs=v3.CONCEPTCODE&mainSearchCriteria.c=v3.409586006",
    "MedlinePlus-v2": "https://apps.nlm.nih.gov/medlineplus/services/mpconnect_service.json?mainSearchCriteria.cs=v2.09&mainSearchCriteria.c=40202858",
}
for name, url in urls.items():
    try:
        req = urllib.request.Request(url, headers={"User-Agent": "NURA-Hermes/1.0"})
        with urllib.request.urlopen(req, timeout=20) as r:
            body = r.read(600).decode(errors="ignore")
            print(f"{name}: HTTP {r.status} -> {body[:120]!r}")
    except urllib.error.HTTPError as e:
        print(f"{name}: HTTP {e.code} {e.reason}")
    except Exception as e:
        print(f"{name}: {type(e).__name__}: {e}")
