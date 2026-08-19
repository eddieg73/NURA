#!/usr/bin/env python3
"""Travel Risk Engine — annual measures + hot-zone comparison.
Parses CDC Travel Health Notices (HTML, verified 2026-08-02), compares against a patient travel profile,
outputs risk flags + recommended verification steps. CLI: travel-risk-engine.py [--profile travel.json] [--update]
"""
import json, re, sys, time, urllib.request
from pathlib import Path

NOTICES_URL = "https://wwwnc.cdc.gov/travel/notices"
OUT = Path("/opt/data/profiles/nura/data/travel-hotzones.json")

LEVELS = {"level1": "Level 1 — usual precautions", "level2": "Level 2 — enhanced precautions", "level3": "Level 3 — avoid nonessential travel", "level4": "Level 4 — avoid all travel"}

def fetch_notices():
    req = urllib.request.Request(NOTICES_URL, headers={"User-Agent": "Mozilla/5.0"})
    with urllib.request.urlopen(req, timeout=30) as r:
        html = r.read().decode("utf-8", "replace")
    pat = re.compile(r'/travel/notices/(level\d)/([a-z0-9\-]+)')
    found = {}
    for m in pat.findall(html):
        lvl, slug = m
        name = slug.replace("-", " ").title()
        found.setdefault(lvl, set()).add(name)
    return {lvl: sorted(list(names)) for lvl, names in found.items()}

def load_profile(path):
    try:
        return json.loads(Path(path).read_text())
    except Exception:
        return {"traveler": "unknown", "trips": []}

def main():
    args = sys.argv[1:]
    zones = fetch_notices()
    OUT.write_text(json.dumps({"ts": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()), "hotzones": zones}, indent=1))
    if "--update" in args:
        print(json.dumps(zones, indent=1))
        return
    prof = load_profile(args[args.index("--profile") + 1]) if "--profile" in args else {"trips": []}
    flags = []
    for trip in prof.get("trips", []):
        dest = (trip.get("destination") or "").lower()
        for lvl, names in zones.items():
            for n in names:
                if dest and any(w in n.lower() for w in dest.split()):
                    flags.append(f"{trip.get('destination')} ({trip.get('dates','?')}): {LEVELS[lvl]} — {n}")
    if flags:
        print("TRAVEL RISK FLAGS:")
        print("\n".join(" - " + f for f in flags))
    print("HOT ZONES NOW:", {lvl: len(ns) for lvl, ns in zones.items()}, "notices")
    if not flags:
        print("No destination overlap — no flags. Verify per CDC destination pages before travel.")

if __name__ == "__main__":
    main()
