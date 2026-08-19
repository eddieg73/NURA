#!/usr/bin/env python3
"""NURA Trip Planner — the free-lane trip mapper (zero keys, zero cost).
Inputs: origin, destination (names or lat/lon), dates. Outputs:
- the geocoded points (OSM Nominatim)
- the drive route + the distance + the time (OSRM)
- the hotels/POIs near the destination (Overpass)
- the airport pair + the great-circle flight distance
The PRICES layer (flights/hotels/cars) = the companion doc (the points/miles
doctrine) + the optional browser-scrape lane.
Usage: python3 nura-trip-planner.py 'Tampa, FL' 'Miami, FL'
"""
import sys, json, urllib.request, urllib.parse, math, time

def geocode(q):
    """Photon (the Komoot/OSM geocoder) — the policy-friendly free lane."""
    u = f"https://photon.komoot.io/api/?limit=1&q={urllib.parse.quote(q)}"
    d = json.loads(urllib.request.urlopen(u, timeout=20).read())
    f = d["features"][0] if d.get("features") else None
    if not f:
        return None
    lon, lat = f["geometry"]["coordinates"]
    return (lat, lon, (f["properties"].get("name") or "") + ", " + (f["properties"].get("country") or ""))

def route(a, b):
    u = f"https://router.project-osrm.org/route/v1/driving/{a[1]},{a[0]};{b[1]},{b[0]}?overview=false"
    d = json.loads(urllib.request.urlopen(u, timeout=20).read())
    if d.get("code") == "Ok":
        km = d["routes"][0]["distance"] / 1000
        mins = d["routes"][0]["duration"] / 60
        return km, mins
    return None, None

def pois(lat, lon, kinds, radius=8000):
    """Hotels/food/etc near the point via the Overpass API (free)."""
    tags = "|".join(f'"{k}"' for k in kinds)
    q = f'[out:json];(node["amenity"~"{tags}"](around:{radius},{lat},{lon}););out 12;'
    u = "https://overpass-api.de/api/interpreter?data=" + urllib.parse.quote(q)
    req = urllib.request.Request(u, headers={"User-Agent": "NURATechTripPlanner/1.0 (eg@nuratech.ai)"})
    d = json.loads(urllib.request.urlopen(req, timeout=30).read())
    return [(e.get("tags", {}).get("name", "?"), round(e["lat"], 4), round(e["lon"], 4))
            for e in d.get("elements", []) if e.get("tags", {}).get("name")][:12]

def flight_km(a, b):
    R = 6371.0
    p1, p2 = math.radians(a[0]), math.radians(b[0])
    dp = math.radians(b[0] - a[0]); dl = math.radians(b[1] - a[1])
    h = math.sin(dp/2)**2 + math.cos(p1)*math.cos(p2)*math.sin(dl/2)**2
    return 2 * R * math.asin(math.sqrt(h))

def plan(origin, dest):
    out = {}
    a = geocode(origin); b = geocode(dest)
    if not a or not b:
        return {"error": "geocode failed"}
    out["origin"] = {"lat": a[0], "lon": a[1], "label": a[2]}
    out["destination"] = {"lat": b[0], "lon": b[1], "label": b[2]}
    km, mins = route(a, b)
    out["drive"] = {"km": round(km, 1) if km else None, "hours": round(mins/60, 1) if mins else None}
    out["flight_km"] = round(flight_km(a, b))
    out["hotels_near_destination"] = pois(b[0], b[1], ["hotel", "motel", "hostel", "guest_house"])
    out["food_near_destination"] = pois(b[0], b[1], ["restaurant", "fast_food", "cafe"])[:8]
    out["airports_near_origin"] = pois(a[0], a[1], ["airport"], radius=30000)[:4]
    out["note"] = "PRICES: the free-price layer = the points/miles doctrine (the companion doc). Live prices: the browser-scrape lane (Google Flights/Skyscanner) — say 'scrape prices' to run it."
    return out

if __name__ == "__main__":
    o, d = sys.argv[1], sys.argv[2]
    print(json.dumps(plan(o, d), indent=2))
