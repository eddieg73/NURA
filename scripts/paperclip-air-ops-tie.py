import json, re, urllib.request, urllib.error

def envval(name):
    env = open("/opt/data/profiles/nura/.env").read()
    m = re.search(rf"^{name}=(.+)$", env, re.M)
    return m.group(1).strip().strip('"').strip("'") if m else ""

key = envval("API_SERVER_KEY")
base = "http://127.0.0.1:3101"
hdr = {"User-Agent": "NURA-Hermes/1.0", "Content-Type": "application/json",
       "x-api-key": key, "Authorization": "Bearer " + key}
issue_id = "9feb77b5-5d50-4857-871f-cc5cc5556a65"

body = ("FOUNDER TIE-IN (2026-08-02): THE DRONES TIE WITH THE AVIATION DIVISION — one air-ops capability:\n"
        "1) Shared COP: aircraft + drone fleet + EMS trucks on ONE Lattice map.\n"
        "2) Drones support the pilot: preflight walk-around, aerial approach view, scouting.\n"
        "3) Deconfliction: Part 107 vs Part 91 — ADS-B In on drones (see the aircraft), geofences vs approach paths.\n"
        "4) Aircraft as mesh node: Lattice mesh extends to the plane (Starlink-class link) — drones relay to plane, "
        "plane relays to trucks.\n"
        "5) Emergency lane: drones deliver AED/meds to the aircraft's LZ; aircraft extends drone range.\n"
        "6) REVA tie: air ambulance + drone first-responder + EMS ground = full delivery chain.\n"
        "Skills updated: drone-swarm-division (air-ops tie section) + aviation-pilot-ops + foreflight-integration.\n"
        "Aero + Avionics leads coordinate under this doctrine; deliverables unchanged (08-10 scan / 08-22 sim).")
try:
    req = urllib.request.Request(base + f"/api/issues/{issue_id}/comments",
                                 data=json.dumps({"body": body}).encode(), headers=hdr, method="POST")
    with urllib.request.urlopen(req, timeout=10) as r:
        print("air-ops tie comment ->", r.status)
except urllib.error.HTTPError as e:
    print("ERR", e.code, e.read().decode()[:200])
