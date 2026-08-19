#!/usr/bin/env python3
import urllib.request, urllib.error

UA = {"User-Agent": "NURA-Hermes/1.0"}
def probe(name, url, check, note=""):
    try:
        req = urllib.request.Request(url, headers=UA)
        with urllib.request.urlopen(req, timeout=20) as r:
            body = r.read(2000).decode(errors="ignore")
            ok = check(body)
            print(("PASS " if ok else "FAIL ") + name + (f" {note}" if note else ""))
            if ok:
                print("     ", body[:110].replace("\n", " "))
            return ok
    except Exception as e:
        print("FAIL " + name + f" ({type(e).__name__}: {e})")
        return False

r = []
r.append(probe("SEC EDGAR", "https://data.sec.gov/submissions/CIK0000001750.json",
               lambda b: "cik" in b.lower() or "name" in b.lower(), "(1750 = Nuratech CIK placeholder)"))
r.append(probe("USPTO PatentsView", "https://search.patentsview.org/api/v1/patent/?q=%7B%22_and%22%3A%5B%7B%22patent_id%22%3A%2212562543%22%7D%5D%7D",
               lambda b: "patent_id" in b.lower() or "total_patent_count" in b.lower()))
r.append(probe("OpenAlex", "https://api.openalex.org/works?search=cardiac%20arrest&per-page=1",
               lambda b: '"results"' in b))
r.append(probe("Europe PMC", "https://www.ebi.ac.uk/europepmc/webservices/rest/search?query=cardiac%20arrest&format=json&pageSize=1",
               lambda b: '"resultList"' in b))
r.append(probe("Open-Meteo", "https://api.open-meteo.com/v1/forecast?latitude=27.96&longitude=-82.45&current_weather=true",
               lambda b: "current_weather" in b))
r.append(probe("Semantic Scholar", "https://api.semanticscholar.org/graph/v1/paper/search?query=cardiac&limit=1",
               lambda b: '"data"' in b))
r.append(probe("PubChem", "https://pubchem.ncbi.nlm.nih.gov/rest/pug/compound/name/aspirin/property/MolecularFormula,CanonicalSMILES/json",
               lambda b: "MolecularFormula" in b))
r.append(probe("GDELT", "https://api.gdeltproject.org/api/v2/doc/doc?query=healthcare%20AI&mode=artlist&maxrecords=1&format=json",
               lambda b: "articles" in b or "artlist" in b))
r.append(probe("CoinGecko", "https://api.coingecko.com/api/v3/ping",
               lambda b: "gecko" in b.lower()))
r.append(probe("Crossref", "https://api.crossref.org/works?query=ventilator&rows=1",
               lambda b: '"message"' in b))
print("RESULT:", f"{sum(r)}/{len(r)} PASS")
