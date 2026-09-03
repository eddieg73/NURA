#!/usr/bin/env python3
"""NURA weather ALERT monitor — signal-only, severity-laddered, location-locked.

SIGNAL (fires to chat, de-duped on change):
  - NWS WARNING-grade events over the founder's zones: tornado warning,
    severe thunderstorm warning, flash flood warning, hurricane warning,
    tropical storm warning, heat warning / excessive heat warning.
  - Lightning risk (NWS lightning-specific alert) near the founder.
  - METAR/TAF thunderstorm at an ACTIVE founder field (KTPA, KPMP, KMCI).

REFERENCE (never fires — dashboard only): Watch, Advisory, Statement, forecast
thunderstorms "chance", AQ/UV, zones far from the founder, non-founder fields.

De-dupe: content-hash on a time-stripped signature; emits ONLY on change.
Silent when clean (no output = no delivery). All sources keyless.
"""
import json
import os
import re
import datetime
import urllib.request
from zoneinfo import ZoneInfo

UA = {"User-Agent": "NURA-weather-monitor/1.1 (nuratech.ai)"}
ET = ZoneInfo("America/New_York")

LOCS = {"Tampa": (27.95, -82.45), "Pompano": (26.23, -80.12)}
FIELDS = ["KTPA", "KPMP", "KMCI"]  # active founder fields only

def get(url, timeout=20):
    req = urllib.request.Request(url, headers=UA)
    try:
        return json.loads(urllib.request.urlopen(req, timeout=timeout).read())
    except Exception as e:
        return {"_err": str(e)[:80]}

def to_et(val):
    if not val:
        return ""
    try:
        if isinstance(val, (int, float)):
            dt = datetime.datetime.fromtimestamp(int(val), tz=datetime.timezone.utc)
        else:
            s = str(val)
            if s.isdigit():
                dt = datetime.datetime.fromtimestamp(int(s), tz=datetime.timezone.utc)
            else:
                dt = datetime.datetime.fromisoformat(s.replace("Z", "+00:00"))
        return dt.astimezone(ET).strftime("%-I:%M %p").lower() + " et"
    except Exception:
        return ""

# ---- severity ladder: only WARNING-grade events are signal ----
def event_severity(event, headline):
    ev = (event or "").lower()
    blob = (ev + " " + (headline or "")).lower()
    def has(*words):
        return any(w in blob for w in words)
    if has("tornado warning", "severe thunderstorm warning", "flash flood warning"):
        return 3, "🔴"
    if has("hurricane warning", "tropical storm warning", "excessive heat warning", "heat warning"):
        return 3, "🔴"
    if has("flood warning"):
        return 2, "⚠️"
    if has("lightning", "frequent cloud"):
        return 2, "⚡"
    return 0, ""

def metar_english(raw):
    if not raw:
        return {}
    toks = raw.split()
    out = {}
    wx_map = {"+TSRA": "heavy thunderstorm", "TSRA": "thunderstorm rain", "-TSRA": "light thunderstorm rain",
              "TS": "thunderstorm", "VCTS": "thunderstorm nearby", "TSRAGR": "thunderstorm hail"}
    wx = [wx_map[t] for t in toks if t in wx_map]
    if wx:
        out["wx"] = ", ".join(wx)
    return out

alerts = []

# 1) NWS active alerts — WARNING-grade signal only, location-locked
for name, (lat, lon) in LOCS.items():
    d = get("https://api.weather.gov/alerts/active?point=%s,%s" % (lat, lon))
    for f in d.get("features", []):
        p = f["properties"]
        ev = str(p.get("event", ""))
        head = str(p.get("headline", ""))
        sev, icon = event_severity(ev, head)
        if sev >= 2:  # only WARNING-grade (or lightning) fires
            alerts.append("%s %s — %s (%s)" % (icon, name, ev, head[:60]))

# 2) METAR thunderstorm at an ACTIVE founder field (signal: real storm, not forecast)
d = get("https://aviationweather.gov/api/data/metar?ids=%s&format=json&hours=0" % ",".join(FIELDS))
for m in d if isinstance(d, list) else []:
    me = metar_english(m.get("rawOb", ""))
    if "thunderstorm" in me.get("wx", "").lower():
        t = to_et(m.get("obsTime", ""))
        alerts.append("⚡ %s — %s observed%s" % (m.get("icaoId", ""), me["wx"], (", " + t) if t else ""))

# 3) TAF thunderstorm forecast (heads-up, medium priority) — active fields only
d = get("https://aviationweather.gov/api/data/taf?ids=%s&format=json&hours=0" % ",".join(FIELDS))
for t in d if isinstance(d, list) else []:
    raw = t.get("rawTAF", "") or ""
    if any(k in raw for k in (" TS", "TSRA", "-TSRA")):
        alerts.append("📋 %s — thunderstorms expected" % t.get("icaoId", ""))

# ---- de-dupe on state change (anti-flood) ----
STATE = "/opt/data/profiles/nura/cron/weather-alerts.state"

def _stable(s):
    s = re.sub(r"\b\d{1,2}:\d{2}\s*[ap]m\s*et\b", "[TIME]", s)
    s = re.sub(r"\d{4}-\d{2}-\d{2}[T ][\d:]+Z?", "[DATETIME]", s)
    return re.sub(r"\s+", " ", s).strip()

sig = "\n".join(_stable(x) for x in sorted(set(alerts)))
prev = open(STATE).read().strip() if os.path.exists(STATE) else ""

if sig:
    if sig != prev:
        print("\n".join([a for a in sorted(set(alerts))][:8]))
        open(STATE, "w").write(sig)
else:
    if prev:
        os.remove(STATE)
# silently no output when clean or unchanged
