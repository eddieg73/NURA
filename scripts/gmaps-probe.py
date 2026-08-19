#!/usr/bin/env python3
"""Google Maps lane: probe + ready-to-wire. Run on key drop:
python3 gmaps-probe.py <KEY>
Probes: Geocoding, Directions, Places — then the key is registered + wired."""
import sys, json, urllib.request, urllib.error

def probe(url):
    try:
        r = urllib.request.urlopen(url, timeout=15)
        d = json.loads(r.read())
        return f"OK {r.status} — {str(d.get('status', d.get('results', '')))[:80]}"
    except urllib.error.HTTPError as e:
        return f"ERR {e.code}: {e.read()[:100]}"
    except Exception as e:
        return f"ERR {str(e)[:80]}"

if __name__ == "__main__":
    key = sys.argv[1] if len(sys.argv) > 1 else ""
    if not key:
        print("usage: gmaps-probe.py <KEY>"); sys.exit(1)
    print("Geocoding :", probe(f"https://maps.googleapis.com/maps/api/geocode/json?address=Tampa+FL&key={key}"))
    print("Directions:", probe(f"https://maps.googleapis.com/maps/api/directions/json?origin=Tampa&destination=Miami&key={key}"))
    print("Places    :", probe(f"https://maps.googleapis.com/maps/api/place/textsearch/json?query=hospitals+in+Tampa&key={key}"))
