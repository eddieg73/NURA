#!/usr/bin/env python3
"""Local METAR — the founder's airports. Free aviationweather.gov API, no key.
Usage: python3 local-metar.py [ICAO ...]  (default: the NURA home-field list)"""
import sys, json, urllib.request, urllib.error

DEFAULT = ["KTPA", "KPIE", "KVNC", "KPMP", "KFXE", "KSPG"]
icaos = sys.argv[1:] or DEFAULT

def color(cat):
    return {"VFR": "🟢 VFR", "MVFR": "🔵 MVFR", "IFR": "🔴 IFR", "LIFR": "🟣 LIFR"}.get(cat, cat)

try:
    url = f"https://aviationweather.gov/api/data/metar?ids={','.join(icaos)}&format=json&hours=0"
    r = urllib.request.urlopen(url, timeout=20)
    for m in json.loads(r.read()):
        print(f"{m['icaoId']} {m['name'].split(',')[0]}: {m['fltCat'] and color(m['fltCat'])} "
              f"{m['temp']:.0f}°C dp {m['dewp']:.0f}°C · {m['wdir']:03d}°@{m['wspd']}kt · "
              f"alt {m['altim']:.0f}hPa · {m['clouds'][0]['cover'] if m.get('clouds') else 'CAVOK'} "
              f"{int(m['clouds'][0]['base']/100)}k" if m.get('clouds') else "")
        print(f"   {m['rawOb']}")
except Exception as e:
    print(f"METAR fetch failed: {e}")
