#!/usr/bin/env python3
"""Morning weather (9am ET): METAR for the six fields + NWS forecast brief for Tampa.
Keyless (aviationweather.gov + api.weather.gov). Prints the full report."""
import json, urllib.request, subprocess

print("🌤 GOOD MORNING WEATHER\n")
# METAR
r = subprocess.run(["python3", "/opt/data/scripts/local-metar.py"], capture_output=True, text=True, timeout=60)
print(r.stdout.strip())

# NWS forecast brief for Tampa (27.95,-82.45)
try:
    req = urllib.request.Request("https://api.weather.gov/points/27.95,-82.45",
                                 headers={"User-Agent": "NURA/1.0 (ops@nuratech.ai)"})
    p = json.loads(urllib.request.urlopen(req, timeout=30).read())
    f = json.loads(urllib.request.urlopen(urllib.request.Request(
        p["properties"]["forecast"], headers={"User-Agent": "NURA/1.0"}), timeout=30).read())
    periods = f["properties"]["periods"]
    print("\n📋 TAMPA FORECAST:")
    for pe in periods[:4]:
        print(f"  {pe['name']}: {pe['shortForecast']} · {pe['temperature']}°{pe['temperatureUnit']}")
except Exception as e:
    print(f"\n(forecast unavailable: {str(e)[:80]})")
