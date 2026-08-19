#!/usr/bin/env python3
"""Travel Vaccine Planner — recommended vaccines by destination (CDC Traveler's Health).
Fetches the CDC destination page and extracts the vaccine/medicine section.
CLI: travel-vaccine-planner.py <destination>  (e.g., thailand, drc, brazil, costa-rica)
"""
import re, sys, urllib.request

def fetch(dest):
    dest = dest.lower().replace(" ", "-")
    url = f"https://wwwnc.cdc.gov/travel/destinations/traveler/none/{dest}"
    req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
    with urllib.request.urlopen(req, timeout=30) as r:
        return r.read().decode("utf-8", "replace")

VACCINE_PAT = re.compile(r'(Hepatitis [AB]|Yellow Fever|Typhoid|Japanese Encephalitis|Rabies|Cholera|Meningococcal|Polio|Malaria|Measles|Tetanus|Influenza|COVID-19|Dengue)[^<]{0,60}', re.I)

def main():
    dest = sys.argv[1] if len(sys.argv) > 1 else "thailand"
    try:
        html = fetch(dest)
    except Exception as e:
        print(f"ERR fetching {dest}: {e}")
        return
    hits = [m.group(1) for m in VACCINE_PAT.finditer(html)]
    seen, out = set(), []
    for h in hits:
        k = h.lower()
        if k not in seen:
            seen.add(k)
            out.append(h)
    print(f"=== Recommended vaccines/medicines for {dest.upper()} (CDC, {fetch.__name__ and 'live page'}) ===")
    print(", ".join(out) if out else "No standard vaccines listed on page — check CDC destination page directly.")
    print("NOTE: verify entry requirements (yellow fever certificate countries) + personalization on the CDC page.")

if __name__ == "__main__":
    main()
