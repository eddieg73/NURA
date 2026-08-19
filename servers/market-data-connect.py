#!/usr/bin/env python3
"""Market data layer registry — probe all free trading-data sources, record state.
Run: python3 scripts/market-data-connect.py   (writes data/market-data.json)"""
import json, os, time, urllib.request
from datetime import datetime, timezone

UA = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/126.0 Safari/537.36"}
ENV = "/opt/data/profiles/nura/.env"

def has_key(name):
    try:
        for line in open(ENV):
            if line.startswith(name + "=") and line.split("=", 1)[1].strip():
                return True
    except OSError:
        pass
    return False

def probe(name, url, ok_codes=(200,), timeout=12, headers=None, expect=None):
    try:
        req = urllib.request.Request(url, headers=headers or UA)
        with urllib.request.urlopen(req, timeout=timeout) as r:
            code = r.status
            body = r.read(200).decode("utf-8", "replace")
        status = "ok" if (code in ok_codes and (expect is None or expect in body)) else f"http{code}"
        return {"status": status, "note": (body[:80].replace("\n", " ") if status == "ok" else "")}
    except Exception as e:
        return {"status": "down", "note": str(e)[:80]}

SOURCES = {
    "yahoo_finance": {"type": "market", "key": None, "probe": lambda: probe(
        "yahoo_finance", "https://query1.finance.yahoo.com/v8/finance/chart/EURUSD%3DX?interval=1d&range=5d")},
    "stooq": {"type": "market", "key": None, "probe": lambda: probe(
        "stooq", "https://stooq.com/q/l/?s=eurusd&f=sd2t2ohlcv&h&e=csv", expect="EURUSD")},
    "coingecko": {"type": "crypto", "key": None, "probe": lambda: probe(
        "coingecko", "https://api.coingecko.com/api/v3/simple/price?ids=bitcoin&vs_currencies=usd", expect="btc")},
    "gdelt": {"type": "sentiment", "key": None, "probe": lambda: probe(
        "gdelt", "https://api.gdeltproject.org/api/v2/doc/doc?query=test&mode=ArtList&maxrecords=1&format=json")},
    "senate_efd": {"type": "congress", "key": None, "probe": lambda: probe(
        "senate_efd", "https://efdsearch.senate.gov/search/home/")},
    "house_disclosures": {"type": "congress", "key": None, "probe": lambda: probe(
        "house_disclosures", "https://disclosurespreview.house.gov/FinancialDisclosure")},
    "quiver": {"type": "congress_flow", "key": "QUIVER_API_KEY", "probe": lambda: probe(
        "quiver", "https://www.quiverquant.com/")},
    "alpha_vantage": {"type": "market", "key": "ALPHAVANTAGE_API_KEY", "probe": lambda: probe(
        "alpha_vantage", "https://www.alphavantage.co/query?function=TIME_SERIES_INTRADAY&symbol=IBM&interval=5min&apikey=demo")},
    "fred": {"type": "macro", "key": "FRED_API_KEY", "probe": lambda: probe(
        "fred", "https://api.stlouisfed.org/fred/series/observations?series_id=DGS10&api_key=demo&file_type=json")},
    "finnhub": {"type": "market", "key": "FINNHUB_API_KEY", "probe": lambda: probe(
        "finnhub", "https://finnhub.io/api/v1/quote?symbol=AAPL&token=demo")},
}

report = {"ts": datetime.now(timezone.utc).isoformat(), "sources": {}}
for name, s in SOURCES.items():
    res = s["probe"]()
    res["key_needed"] = bool(s["key"])
    report["sources"][name] = res
    time.sleep(0.4)

with open("/opt/data/profiles/nura/data/market-data.json", "w") as f:
    json.dump(report, f, indent=1)

for name, s in report["sources"].items():
    key = f" [KEY DROP]" if s["key_needed"] else ""
    print(f"{name:20} {s['status']:<8} {s.get('note','')[:60]}{key}")
