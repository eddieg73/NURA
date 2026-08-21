#!/usr/bin/env python3
"""The EXECUTIVE weather brief — the multi-site, the pilot-grade, the data only. The Musk lens: the dense, the scannable, the decisions."""
import json
import re
import urllib.request

UA = {"User-Agent": "NURA-Exec-Brief/1.0 (eg@nuratech.ai)"}

def get(url, timeout=20):
    try:
        req = urllib.request.Request(url, headers=UA)
        return json.loads(urllib.request.urlopen(req, timeout=timeout).read())
    except Exception:
        return {}

def dec(raw):
    parts = raw.split()
    out = []
    for p in parts[1:]:
        if p.endswith("KT") and "/" not in p:
            w = p.replace("KT", "")
            out.append("calm" if w == "00000" else f"{w[:3]}°/{w[3:5]}kt")
        elif p.endswith("SM"):
            out.append(p)
        elif p.startswith(("FEW", "SCT", "BKN", "OVC")):
            h = p[3:6]
            out.append(f"{p[:3]}{int(h) * 100 if h.isdigit() else ''}")
        elif p.startswith(("CLR", "SKC")):
            out.append(p[:3])
        elif len(p) == 5 and p[2] == "/" and "/" in p:
            out.append(f"{p[:2]}/{p[3:]}")
        elif p.startswith("A") and len(p) == 5:
            out.append(f"A{p[1:3]}.{p[3:5]}")
        elif p == "TS":
            out.append("TS")
    return " ".join(out)

SITES = [("TAMPA-HQ", 28.02, -82.42, "KTPA", "TBW", "72,101"),
         ("SOUTH-FL", 26.23, -80.12, "KPMP", "MFL", "110,71"),
         ("KANSAS-CITY", 39.30, -94.71, "KMCI", "EAX", "39,60")]

print("WEATHER | FL EXEC")
p0 = None
for name, lat, lon, icao, wfo, grid in SITES:
    fc = get(f"https://api.weather.gov/gridpoints/{wfo}/{grid}/forecast")
    per = fc.get("properties", {}).get("periods", [])
    p = per[0] if per else {}
    if name == "TAMPA-HQ":
        p0 = p
        p1 = per[1] if len(per) > 1 else {}
    m = get(f"https://aviationweather.gov/api/data/metar?ids={icao}&format=json&hours=0")
    met = dec(m[0].get("rawOb", "")) if isinstance(m, list) and m else "n/a"
    aq = get(f"https://air-quality-api.open-meteo.com/v1/air-quality?latitude={lat}&longitude={lon}&current=us_aqi,pm2_5&hourly=uv_index&forecast_days=1")
    cur = aq.get("current", {})
    uv = aq.get("hourly", {}).get("uv_index", [None])[-1]
    print(f"{name}: {p.get('temperature','?')}° {p.get('shortForecast','')} | {icao} {met} | AQ{cur.get('us_aqi','?')} UV{uv}")

# The advisory BLUF + the tomorrow
advisories = []
for name, lat, lon, icao, wfo, grid in SITES[:2]:
    al = get(f"https://api.weather.gov/alerts/active?point={lat},{lon}")
    for f in al.get("features", [])[:2]:
        pr = f["properties"]
        if any(k in str(pr.get("event")).lower() for k in ["heat", "thunderstorm", "tornado", "flood", "tropical", "hurricane"]):
            advisories.append(f"⚠ {pr.get('event')} {pr.get('severity')} — {name}")

nhc = get("https://www.nhc.noaa.gov/CurrentStorms.json")
for s in nhc.get("activeStorms", []):
    if s.get("basin") == "AL":
        advisories.append(f"HURRICANE {s.get('name')} {s.get('classification')} {s.get('latitude')}N {s.get('longitude')}W")

if advisories:
    print("PRIORITY: " + " | ".join(advisories))
else:
    print("PRIORITY: clear — no ops impact")
if p1:
    print(f"TOMORROW: {p1.get('temperature','?')}° {p1.get('shortForecast','')}")
