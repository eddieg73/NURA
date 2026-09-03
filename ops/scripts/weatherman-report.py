#!/usr/bin/env python3
"""NURA weather card — plain English, one-glance readable.

Scheduled 8am / noon / 5pm ET. Speaks plain words, no METAR code, no raw
tokens. Groups: HEADLINE → now → today → tonight/tomorrow → marine + tides.
Zulu shown once for the pilot. All sources keyless (NWS + aviationweather +
Open-Meteo + NOAA tides). Verified 2026-09-02.
"""
import json
import re
import urllib.request
import datetime
from zoneinfo import ZoneInfo

UA = {"User-Agent": "NURA-Exec-Brief/1.0 (eg@nuratech.ai)"}
ET = ZoneInfo("America/New_York")

def get(url, timeout=25):
    try:
        req = urllib.request.Request(url, headers=UA)
        return json.loads(urllib.request.urlopen(req, timeout=timeout).read())
    except Exception:
        return {}

def get_text(url, timeout=25):
    try:
        req = urllib.request.Request(url, headers=UA)
        return urllib.request.urlopen(req, timeout=timeout).read().decode("utf-8", "replace")
    except Exception:
        return ""

def epoch_to_zulu(ts):
    try:
        return datetime.datetime.fromtimestamp(int(ts), tz=datetime.timezone.utc).strftime("%H%MZ")
    except Exception:
        return ""

def c_to_f(c):
    try:
        return round(int(c) * 9 / 5 + 32)
    except Exception:
        return None

# --- plain-English translators (the readability fix) ---
DIRS = ["N", "NNE", "NE", "ENE", "E", "ESE", "SE", "SSE",
        "S", "SSW", "SW", "WSW", "W", "WNW", "NW", "NNW"]

def compass(deg):
    try:
        return DIRS[int((int(deg) + 11.25) // 22.5) % 16]
    except Exception:
        return ""

def wind_words(kt, gust=None, deg=None):
    """'calm' | '12 mph from the NW' | '15 mph from the S, gusting 28'"""
    try:
        kt = int(kt)
    except Exception:
        return ""
    if kt == 0:
        return "calm"
    mph = round(kt * 1.151)
    d = compass(deg)
    base = "%d mph%s" % (mph, (" from the " + d) if d else "")
    if gust:
        try:
            g = round(int(gust) * 1.151)
            base += ", gusting %d" % g
        except Exception:
            pass
    return base

def wx_words(short):
    """NWS shortForecast -> short plain phrase: 'Partly Sunny' -> 'partly sunny';
    'Chance of showers and thunderstorms' -> 'showers/storms possible'."""
    s = (short or "").lower()
    s = s.replace("then ", "").replace(" likely", "").replace("chance of", "possible")
    s = s.replace("t-storms", "storms").replace("thunderstorms", "storms")
    s = s.replace("t-storm", "storm")
    s = s.replace("showers and storms", "showers/storms")
    s = s.replace("showers and thunderstorm", "showers/storms")
    s = s.replace("and showers", "showers")
    s = s.replace("showers", "showers/storms").replace("storms/storms", "storms").replace("stormss", "storms")
    s = re.sub(r"\s+", " ", s).strip().rstrip(",")
    return s

def sky_words(short):
    s = (short or "").lower()
    if "t-storm" in s or "thunderstorm" in s:
        return "storms"
    if "rain" in s:
        return "rain"
    if "shower" in s:
        return "showers"
    if "cloudy" in s or "overcast" in s:
        return "mostly cloudy"
    if "partly" in s or "mostly sunny" in s or "scattered" in s:
        return "partly sunny"
    if "sunny" in s or "clear" in s:
        return "sunny"
    return s.strip() or ""

def metar_now(raw):
    """Return a plain-English dict for the current obs from a raw METAR."""
    if not raw:
        return {}
    toks = raw.split()
    out = {}
    for i, t in enumerate(toks):
        if t.endswith("KT"):
            w = t[:-2]
            out["wind"] = wind_words(int(w[3:5]) if len(w) >= 5 and w[3:5].isdigit() else 0,
                                     int(w[6:8]) if len(w) >= 8 and w[6:8].isdigit() else None,
                                     int(w[:3]) if len(w) >= 3 and w[:3].isdigit() else None)
            break
    for t in toks:
        if t.endswith("SM"):
            v = t[:-2]
            out["vis"] = "10+ miles" if v == "P6" else ("%s mi" % v)
            break
    wx = {"TSRA": "thunderstorm", "+TSRA": "heavy thunderstorm", "-TSRA": "light thunderstorm",
          "VCTS": "storm nearby", "+RA": "heavy rain", "RA": "rain", "-RA": "light rain",
          "BR": "mist", "FG": "fog", "HZ": "haze", "-DZ": "light drizzle", "SHRA": "rain showers"}
    wxx = [wx[t] for t in toks if t in wx]
    if wxx:
        out["wx"] = ", ".join(wxx)
    for t in toks:
        if "/" in t and len(t) == 5 and t.count("/") == 1:
            f = c_to_f(t.split("/")[0])
            if f is not None:
                out["temp"] = "%d\u00b0" % f
            break
    return out

def sky_emoji(short):
    s = (short or "").lower()
    if "storm" in s or "t-storm" in s:
        return "⛈️"
    if "rain" in s or "shower" in s:
        return "🌧️"
    if "cloudy" in s or "overcast" in s:
        return "☁️"
    if "partly" in s or "scattered" in s:
        return "⛅"
    if "sunny" in s or "clear" in s:
        return "☀️"
    return "🌡️"

def aqi_words(aqi):
    try:
        a = int(aqi)
    except Exception:
        return "n/a", ""
    if a <= 50:
        return a, "good"
    if a <= 100:
        return a, "moderate"
    if a <= 150:
        return a, "unhealthy for sensitive groups"
    if a <= 200:
        return a, "unhealthy"
    return a, "very unhealthy"

def uv_words(uv):
    try:
        u = float(uv)
    except Exception:
        return "n/a"
    if u < 3:
        return "low"
    if u < 6:
        return "moderate"
    if u < 8:
        return "high"
    if u < 11:
        return "very high"
    return "extreme"

# --- marine (Pompano Beach / AMZ651) — plain English ---
def marine_amz651():
    html = get_text("https://forecast.weather.gov/shmrn.php?mz=AMZ651")
    txt = re.sub(r"<[^>]+>", "\n", html)
    txt = txt.replace("&nbsp;", " ")
    txt = re.sub(r"[ \t]+", " ", txt)
    txt = re.sub(r"\n\s*\n+", "\n", txt)
    i = txt.find("TODAY")
    j = txt.find("TONIGHT", i + 5) if i >= 0 else -1
    if i < 0:
        return ""
    seg = txt[i + 5: j if j > i else i + 450]
    seg = re.sub(r"\s+", " ", seg).strip()
    s = seg
    s = s.replace("tstms", "storms").replace("tstorms", "storms").replace("tstms and showers", "storms & showers")
    s = s.replace("Winds", "wind").replace("winds", "wind").replace(" and seas", " · seas")
    s = s.replace("Seas less than", "seas under").replace(" or less", "")
    s = s.replace("Intracoastal waters light chop", "light chop")
    s = s.replace("Intracoastal waters smooth", "smooth")
    s = re.sub(r"(?<=\d)\s+to\s+(?=\d)", " to ", s)
    s = re.sub(r"\.\s*Wave Detail:.*?\.", ".", s)
    # fold "chance of showers and thunderstorms" into short form
    if "chance of" in s.lower():
        s = s[:s.lower().find("chance of")].rstrip(". ") + " — a shower/storm chance"
    s = re.sub(r"\s+", " ", s).strip().rstrip(".")
    return s

def tides_hillsboro():
    today = datetime.date.today()
    tomorrow = today + datetime.timedelta(days=1)
    url = ("https://api.tidesandcurrents.noaa.gov/api/prod/datagetter"
           "?begin_date=%s&end_date=%s&station=8722859&product=predictions"
           "&datum=MLLW&time_zone=lst_ldt&units=english&interval=hilo&format=json"
           % (today.strftime("%Y%m%d"), tomorrow.strftime("%Y%m%d")))
    d = get(url)
    preds = d.get("predictions", []) if isinstance(d, dict) else []
    out = []
    for p in preds[:4]:
        typ = p.get("type", "")
        try:
            vstr = "%.1fft" % float(p.get("v", 0))
        except Exception:
            vstr = p.get("v", "")
        try:
            tm = datetime.datetime.fromisoformat(p.get("t", "")).strftime("%-I:%M%p").lower()
        except Exception:
            tm = p.get("t", "")
        out.append("%s %s %s" % ("▲" if typ == "H" else "▼", vstr, tm))
    return " · ".join(out) if out else ""

def sigmets():
    SE = {"FL", "GA", "AL", "SC"}
    d = get("https://aviationweather.gov/api/data/sigmet?format=json")
    out = []
    for s in d if isinstance(d, list) else []:
        raw = s.get("rawAirSigmet", "") or ""
        sid = s.get("seriesId", "?")
        lines = raw.split("\n")
        states_line = ""
        for i, ln in enumerate(lines):
            if "VALID UNTIL" in ln and i + 1 < len(lines):
                states_line = lines[i + 1].strip()
                break
        st = [w for w in states_line.split() if len(w) == 2 and w.isalpha() and w.isupper()]
        if not (set(st) & SE):
            continue
        m = re.search(r"VALID UNTIL (\d{4}Z)", raw)
        until = m.group(1) if m else ""
        out.append("%s over %s%s" % (sid, "+".join(sorted(set(st) & SE) or st),
                                     (" until " + until) if until else ""))
    return out

SITES = [
    ("Tampa",        28.02, -82.42, "KTPA", "TBW", "72,101"),
    ("Pompano Beach",26.23, -80.12, "KPMP", "MFL", "110,71"),
    ("Kansas City",  39.30, -94.71, "KMCI", "EAX", "39,60"),
]

zulu = datetime.datetime.now(datetime.timezone.utc).strftime("%H%MZ")
now_local = datetime.datetime.now(ET).strftime("%-I:%M %p").lower()
date_str = datetime.datetime.now(ET).strftime("%A, %B %d")
print("🌤️  Nura Wx — %s · %s (local) · %s Z" % (date_str, now_local, zulu))

tomorrow = None
priority = []
for name, lat, lon, icao, wfo, grid in SITES:
    # NWS forecast (today + tonight)
    fc = get("https://api.weather.gov/gridpoints/%s/%s/forecast" % (wfo, grid))
    per = fc.get("properties", {}).get("periods", [])
    today_p = per[0] if per else {}
    tonight_p = per[1] if len(per) > 1 else {}
    if name == "Tampa" and len(per) > 1:
        tomorrow = per[2] if len(per) > 2 else per[1]

    # live METAR -> plain words
    m = get("https://aviationweather.gov/api/data/metar?ids=%s&format=json&hours=0" % icao)
    me = metar_now(m[0].get("rawOb", "")) if isinstance(m, list) and m else {}
    zt = epoch_to_zulu(m[0].get("obsTime", "")) if isinstance(m, list) and m else ""

    # AQ + UV
    aq = get("https://air-quality-api.open-meteo.com/v1/air-quality?latitude=%s&longitude=%s&current=us_aqi,pm2_5&hourly=uv_index&forecast_days=1" % (lat, lon))
    cur = aq.get("current", {})
    uv = aq.get("hourly", {}).get("uv_index", [None])[-1]

    # --- the one-glance block ---
    print("\n%s  %s — %s, %s°" % (sky_emoji(today_p.get("shortForecast", "")), name,
          sky_words(today_p.get("shortForecast", "")), today_p.get("temperature", "?")))
    now_bits = []
    if me.get("wind"):
        now_bits.append(me["wind"])
    if me.get("vis"):
        now_bits.append(me["vis"])
    if me.get("wx"):
        now_bits.append(me["wx"])
    if now_bits:
        print("  now:  " + " · ".join(now_bits) + ("  (" + zt + ")" if zt else ""))
    else:
        print("  now:  " + (today_p.get("shortForecast", "").lower() or "n/a"))
    print("  next: %s, %s°" % (wx_words(tonight_p.get("shortForecast", "")), tonight_p.get("temperature", "?")))
    print("  air:  %s (%s)   uv: %s" % (cur.get("us_aqi", "n/a"), aqi_words(cur.get("us_aqi"))[1], uv_words(uv)))

    if name == "Pompano Beach":
        tides = tides_hillsboro()
        if tides:
            print("  tides: " + tides)
        marine = marine_amz651()
        if marine:
            print("  ocean: " + marine)

    # SIGNAL only: actual severe/weather warnings (heat/storm/tornado/flood/tropical/hurricane)
    al = get("https://api.weather.gov/alerts/active?point=%s,%s" % (lat, lon))
    for f in al.get("features", []):
        pr = f["properties"]
        ev = str(pr.get("event", ""))
        evl = ev.lower()
        # severity ladder: Warning = real signal; Watch/Advisory = reference (dashboard only)
        if any(k in evl for k in ("tornado warning", "severe thunderstorm warning", "flash flood warning",
                                  "hurricane warning", "tropical storm warning", "flood warning",
                                  "heat warning", "excessive heat warning")):
            sev = "🔴 " if "warning" in evl else "⚠️ "
            priority.append("%s%s — %s" % (sev, ev, name))

nhc = get("https://www.nhc.noaa.gov/CurrentStorms.json")
for s in nhc.get("activeStorms", []):
    if s.get("basin") == "AL":
        priority.append("🌀 %s — %s" % (s.get("name"), s.get("classification")))

if priority:
    print("\n" + "\n".join(priority))
else:
    print("\n✨  no active severe-weather alerts")

sig = sigmets()
if sig:
    print("\n🛫  storm cells over: " + "; ".join(sig))

if tomorrow:
    print("\n🌅  Tomorrow (Tampa): %s, %s°" % (wx_words(tomorrow.get("shortForecast", "")), tomorrow.get("temperature", "?")))
