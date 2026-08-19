#!/usr/bin/env python3
import json, urllib.request, urllib.parse

UA = {"User-Agent": "NURA-Hermes/1.0 research contact@nuratech.ai"}
def fts(q, extra=""):
    url = f"https://efts.sec.gov/LATEST/search-index?q={urllib.parse.quote(q)}&forms=1-A{extra}"
    req = urllib.request.Request(url, headers=UA)
    with urllib.request.urlopen(req, timeout=30) as r:
        return json.loads(r.read().decode())

for query in ["artificial intelligence healthcare", "digital health", "medical AI diagnostics"]:
    try:
        d = fts(query)
        total = d["hits"]["total"]["value"]
        print(f"=== '{query}' -> {total} filings ===")
        for h in d["hits"]["hits"][:8]:
            s = h.get("_source", {})
            print(f"  {s.get('file_date','?')} | {s.get('display_names', s.get('entity_name','?'))} | {s.get('form','?')} | CIK {s.get('ciks', s.get('cik','?'))} | {s.get('file_name','?')[:70]}")
    except Exception as e:
        print(f"query '{query}' failed: {e}")
