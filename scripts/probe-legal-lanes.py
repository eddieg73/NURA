#!/usr/bin/env python3
import urllib.request, urllib.error

UA = {"User-Agent": "NURA-Hermes/1.0 (Nuratech.ai)"}
def probe(name, url, check):
    try:
        req = urllib.request.Request(url, headers=UA)
        with urllib.request.urlopen(req, timeout=20) as r:
            body = r.read(2500).decode(errors="ignore")
            ok = check(body)
            print(("PASS " if ok else "FAIL ") + name + f" (HTTP {r.status})")
            if ok:
                print("     ", body[:120].replace("\n", " "))
            return ok
    except Exception as e:
        print("FAIL " + name + f" ({type(e).__name__}: {e})")
        return False

r = []
r.append(probe("eCFR API", "https://www.ecfr.gov/api/versioner/v1/titles.json",
               lambda b: '"title"' in b.lower() or '"cfr_title"' in b.lower()))
r.append(probe("FL Admin Code 64J", "https://www.flrules.org/gateway/ChapterHome.asp?Chapter=64J",
               lambda b: "64J" in b))
r.append(probe("FL DOH MQA lookup", "https://mqa-internet.doh.state.fl.us/MQASearchServices/HealthCareProviders",
               lambda b: "license" in b.lower() or "search" in b.lower() or "provider" in b.lower()))
r.append(probe("MyFLCourtAccess", "https://www.myflcourtaccess.com/",
               lambda b: "court" in b.lower() or "access" in b.lower() or "florida" in b.lower()))
r.append(probe("eCFR search API", "https://www.ecfr.gov/api/search/v1/?q=%22artificial%20intelligence%22",
               lambda b: '"results"' in b.lower() or "count" in b.lower()))
print("RESULT:", f"{sum(r)}/{len(r)} PASS")
