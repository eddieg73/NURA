#!/usr/bin/env python3
"""NURA lightning + weather alert monitor — keyless (NWS + aviationweather.gov).
Silent when clean. Fires a cute, plain-English alert line when: an NWS alert
mentions lightning/severe weather near the founder, a METAR/TAF shows a
thunderstorm, or a thunderstorm is in the hourly forecast. De-dupes on state
change (the anti-flood law)."""
import json
import os
import datetime
import urllib.request
from zoneinfo import ZoneInfo

UA = {"User-Agent": "NURA-weather-monitor/1.0 (nuratech.ai)"}
ET = ZoneInfo("America/New_York")

LOCS = {"Tampa": (27.95, -82.45), "Pompano": (26.23, -80.12), "Venice": (27.07, -82.44)}
FIELDS = ["KTPA", "KPIE", "KVNC", "KPMP", "KFXE", "KSPG"]

def get(url, timeout=20):
    req = urllib.request.Request(url, headers=UA)
    try:
        return json.loads(urllib.request.urlopen(req, timeout=timeout).read())
    except Exception as e:
        return {"_err": str(e)[:80]}

def to_et(val):
    """Epoch int, ISO string, or METAR ddhhmmZ -> '4:30 pm ET'. '' on failure."""
    if not val:
        return ""
    try:
        if isinstance(val, (int, float)):
            dt = datetime.datetime.fromtimestamp(int(val), tz=datetime.timezone.utc)
        else:
            s = str(val)
            if s.isdigit():
                dt = datetime.datetime.fromtimestamp(int(s), tz=datetime.timezone.utc)
            elif s.endswith("Z") and len(s) == 7 and s[:2].isdigit():
                now_utc = datetime.datetime.now(datetime.timezone.utc)
                dt = now_utc.replace(day=int(s[0:2]), hour=int(s[2:4]),
                                     minute=int(s[4:6]), second=0, microsecond=0)
            else:
                dt = datetime.datetime.fromisoformat(s.replace("Z", "+00:00"))
        return dt.astimezone(ET).strftime("%-I:%M %p").lower() + " ET"
    except Exception:
        return ""

def wind_dir(deg):
    try:
        dirs = ["N", "NNE", "NE", "ENE", "E", "ESE", "SE", "SSE",
                "S", "SSW", "SW", "WSW", "W", "WNW", "NW", "NNW"]
        return dirs[int((int(deg) + 11.25) // 22.5) % 16]
    except Exception:
        return ""

def metar_english(raw):
    if not raw:
        return {}
    toks = raw.split()
    out = {}
    for t in toks:
        if t.endswith("KT"):
            w = t[:-2]
            if w == "00000":
                out["wind"] = "calm"
            elif w.startswith("VRB"):
                out["wind"] = "variable"
            else:
                base = "wind %s %s kt" % (wind_dir(w[:3]), int(w[3:5]))
                if len(w) >= 8 and w[5] == "G":
                    base += " gusting %s kt" % int(w[6:8])
                out["wind"] = base
            break
    for t in toks:
        if t.endswith("SM"):
            v = t[:-2]
            if v == "P6":
                out["vis"] = "10+ mi"
            elif "/" in v:
                out["vis"] = "%s mi" % v
            else:
                out["vis"] = "%s mi" % v
            break
    wx_map = {"+TSRA": "heavy thunderstorm rain", "TSRA": "thunderstorm rain",
              "-TSRA": "light thunderstorm rain", "TS": "thunderstorm",
              "VCTS": "thunderstorm nearby", "+RA": "heavy rain", "RA": "rain",
              "-RA": "light rain", "BR": "mist", "FG": "fog"}
    wx = [wx_map[t] for t in toks if t in wx_map]
    if wx:
        out["wx"] = ", ".join(wx)
    return out

alerts = []

# 1) NWS active alerts — lightning + severe weather only, plain English
for name, (lat, lon) in LOCS.items():
    d = get("https://api.weather.gov/alerts/active?point=%s,%s" % (lat, lon))
    for f in d.get("features", []):
        p = f["properties"]
        ev = str(p.get("event", ""))
        headline = str(p.get("headline", ""))
        desc = str(p.get("description", ""))
        blob = (ev + " " + headline + " " + desc).lower()
        if "lightning" in blob or "frequent cloud" in blob:
            alerts.append("⚡ %s — lightning risk: %s (%s)" % (name, headline[:70], ev))
        elif any(k in ev.lower() for k in ["thunderstorm", "tornado", "flash flood"]):
            alerts.append("⚠️ %s — %s" % (name, ev))

# 2) Hourly forecast thunderstorm (Tampa) — one stable heads-up line
d = get("https://api.weather.gov/points/27.95,-82.45")
if "properties" in d:
    hurl = d["properties"].get("forecastHourly")
    if hurl:
        h = get(hurl)
        ts = [p for p in h.get("properties", {}).get("periods", [])[:12]
              if "thunderstorm" in p.get("shortForecast", "").lower()]
        if ts:
            now = datetime.datetime.now(datetime.timezone.utc)
            try:
                first_dt = datetime.datetime.fromisoformat(ts[0].get("startTime", "").replace("Z", "+00:00"))
                ongoing = first_dt <= now
            except Exception:
                ongoing = False
            t0 = to_et(ts[0].get("startTime"))
            if ongoing:
                last = to_et(ts[-1].get("startTime"))
                alerts.append("⚡ Tampa — thunderstorms in the forecast (ongoing%s)" % (", through %s" % last if last else ""))
            else:
                alerts.append("⚡ Tampa — thunderstorms in the forecast%s" % (", starting %s" % t0 if t0 else ""))

# 3) METAR flags (thunderstorm observed, or IFR/LIFR pilot heads-up)
d = get("https://aviationweather.gov/api/data/metar?ids=%s&format=json&hours=0" % ",".join(FIELDS))
for m in d if isinstance(d, list) else []:
    cat = m.get("fltCat")
    raw = m.get("rawOb", "")
    icao = m.get("icaoId", "")
    me = metar_english(raw)
    if me.get("wx") and any(k in me["wx"] for k in ("thunderstorm",)):
        t = to_et(m.get("obsTime", ""))
        alerts.append("⚡ %s — %s%s" % (icao, me["wx"], (", %s" % t if t else "")))
    elif cat in ("IFR", "LIFR"):
        t = to_et(m.get("obsTime", ""))
        cond = "very low visibility" if cat == "LIFR" else "low ceiling"
        alerts.append("🟥 %s — %s%s" % (icao, cond, (", %s" % t if t else "")))

# 4) TAF thunderstorm
d = get("https://aviationweather.gov/api/data/taf?ids=%s&format=json&hours=0" % ",".join(FIELDS[:3]))
for t in d if isinstance(d, list) else []:
    raw = t.get("rawTAF", "") or t.get("rawOb", "")
    if any(k in raw for k in ("TS", "TSRA", "-TSRA")):
        alerts.append("📋 TAF %s — thunderstorm expected" % t.get("icaoId", ""))

# De-dupe on state change (anti-flood law)
STATE = "/opt/data/profiles/nura/cron/weather-alerts.state"
import re as _re

def _stable(s: str) -> str:
    """Signature-stable version of an alert line: strip time-varying tokens so the SAME
    event (a thunderstorm, a low-ceiling IFR) does NOT re-fire just because the METAR
    obs-time or a forecast 'starting/through 4:30 pm ET' string changed on the next tick.
    Without this, 'sig != prev' is true every run -> the anti-flood dedupe is silently
    defeated and the alert re-delivers every 10 minutes (the 19-message flood, 2026-08-29)."""
    # drop ET clock times like '4:30 pm ET'
    s = _re.sub(r"\b\d{1,2}:\d{2}\s*[ap]m\s*ET\b", "[TIME]", s)
    # drop 'starting/through <time ET>' clauses
    s = _re.sub(r"(starting|through)\s*\[TIME\]", r"\1 [TIME]", s)
    # drop ISO/datetime-ish tokens as a belt-and-suspenders
    s = _re.sub(r"\d{4}-\d{2}-\d{2}[T ][\d:]+Z?", "[DATETIME]", s)
    # collapse repeated spaces
    return _re.sub(r"\s+", " ", s).strip()

sig = "\n".join(_stable(x) for x in sorted(set(alerts)))
prev = open(STATE).read().strip() if os.path.exists(STATE) else ""
if sig:
    if sig != prev:
        print("\n".join(alerts[:8]))
        open(STATE, "w").write(sig)
else:
    if prev:
        os.remove(STATE)
