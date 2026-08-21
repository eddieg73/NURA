#!/usr/bin/env python3
"""NURA local weather + lightning monitor — keyless (NWS + aviationweather.gov).
Silent when clean. Prints ALERT lines when: active NWS alert · METAR IFR/LIFR · TS in METAR/TAF · high gust.
Usage: python3 local-weather-monitor.py   (also: local-metar.py for the pretty read)"""
import json, urllib.request, urllib.error

UA = {"User-Agent": "NURA-weather-monitor/1.0 (nuratech.ai)"}
LOCS = {"Tampa": (27.95, -82.45), "Pompano": (26.23, -80.12), "Venice": (27.07, -82.44)}
FIELDS = ["KTPA", "KPIE", "KVNC", "KPMP", "KFXE", "KSPG"]

def get(url, timeout=20):
    req = urllib.request.Request(url, headers=UA)
    try:
        return json.loads(urllib.request.urlopen(req, timeout=timeout).read())
    except Exception as e:
        return {"_err": str(e)[:80]}

alerts = []
# 1) NWS active alerts per location
for name, (lat, lon) in LOCS.items():
    d = get(f"https://api.weather.gov/alerts/active?point={lat},{lon}")
    for f in d.get("features", []):
        p = f["properties"]
        alerts.append(f"⚠️ {p.get('event')} ({p.get('severity')}) — {name} — {p.get('headline')[:80]}")

# 2) Hourly forecast: TS probability + gusts (Tampa)
d = get(f"https://api.weather.gov/points/27.95,-82.45")
if "properties" in d:
    hurl = d["properties"].get("forecastHourly")
    if hurl:
        h = get(hurl)
        for per in h.get("properties", {}).get("periods", [])[:12]:
            short = per.get("shortForecast", "")
            gust = per.get("windGust", "")
            ts_prob = per.get("probabilityOfPrecipitation", {})
            # lightning proxy: thunderstorm in shortForecast or high CAPE-ish wording
            if "thunderstorm" in short.lower() or "showers and thunderstorms" in short.lower():
                alerts.append(f"⚡ TS forecast — Tampa {per.get('startTime','')[11:16]}Z: {short}")
            if isinstance(gust, str) and gust and int(gust.rstrip(' mph') or 0) >= 30:
                alerts.append(f"💨 Gust {gust} — Tampa {per.get('startTime','')[11:16]}Z")

# 3) METAR flags (IFR/LIFR or TS)
d = get(f"https://aviationweather.gov/api/data/metar?ids={','.join(FIELDS)}&format=json&hours=0")
for m in d if isinstance(d, list) else []:
    cat = m.get("fltCat")
    raw = m.get("rawOb", "")
    if cat in ("IFR", "LIFR"):
        alerts.append(f"🟥 {m['icaoId']} {cat}! {raw[:80]}")
    if "TS" in raw.split("RMK")[0]:
        alerts.append(f"⚡ TS at {m['icaoId']}: {raw[:80]}")

# 4) TAF flight-category changes
d = get(f"https://aviationweather.gov/api/data/taf?ids={','.join(FIELDS[:3])}&format=json&hours=0")
for t in d if isinstance(d, list) else []:
    raw = t.get("rawTAF", "") or t.get("rawOb", "")
    if any(k in raw for k in ("TS", "TSRA", "-TSRA", "IFR", "LIFR", "BECMG")):
        alerts.append(f"📋 TAF {t.get('icaoId')}: {raw[:100]}")

# The de-dupe: the alert only fires on the CHANGE (the new alert or the cleared) — the anti-flood law.
import os
STATE = "/opt/data/profiles/nura/cron/weather-alerts.state"
sig = "\n".join(sorted(set(alerts)))
prev = open(STATE).read().strip() if os.path.exists(STATE) else ""
if sig:
    if sig != prev:
        print("WEATHER ALERT: " + " | ".join(alerts[:4]))
        open(STATE, "w").write(sig)
    # the same alert set as the last run → the SILENT (the never re-alert)
else:
    if prev:
        os.remove(STATE)  # the cleared — the next alert is the new
# silent when clean
