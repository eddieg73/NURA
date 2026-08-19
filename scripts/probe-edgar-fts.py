#!/usr/bin/env python3
import urllib.request, urllib.error, json

UA = {"User-Agent": "NURA-Hermes/1.0 research contact@nuratech.ai"}
candidates = [
    ("EDGAR-FTS-1", "https://efts.sec.gov/LATEST/search-index?q=%22artificial%20intelligence%22&forms=1-A"),
    ("EDGAR-FTS-2", "https://efts.sec.gov/LATEST/search-index?q=healthcare"),
    ("EDGAR-submissions-sf", "https://data.sec.gov/submissions/CIK0001895134.json"),
]
for name, url in candidates:
    try:
        req = urllib.request.Request(url, headers=UA)
        with urllib.request.urlopen(req, timeout=20) as r:
            body = r.read(1500).decode(errors="ignore")
            print(f"{name}: HTTP {r.status} -> {body[:200]!r}")
    except urllib.error.HTTPError as e:
        print(f"{name}: HTTP {e.code} {e.reason} -> {e.read()[:150]!r}")
    except Exception as e:
        print(f"{name}: {type(e).__name__}: {e}")
