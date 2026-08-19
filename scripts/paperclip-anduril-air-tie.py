import json, re, urllib.request, urllib.error

def envval(name):
    env = open("/opt/data/profiles/nura/.env").read()
    m = re.search(rf"^{name}=(.+)$", env, re.M)
    return m.group(1).strip().strip('"').strip("'") if m else ""

key = envval("API_SERVER_KEY")
base = "http://127.0.0.1:3101"
hdr = {"User-Agent": "NURA-Hermes/1.0", "Content-Type": "application/json",
       "x-api-key": key, "Authorization": "Bearer " + key}
issue_id = "fa0f9bb7-c478-4ee8-945f-e80c824a91a2"

body = ("FOUNDER TIE-IN (2026-08-02): THE AIR-OPS DOMAIN TIES WITH ANDURIL/LATTICE — the aircraft joins the mesh:\n"
        "1) Aircraft = Lattice node: the PA-46/aircraft carries the mesh link (Starlink-class) — the plane, drones, "
        "trucks, and PJ operator all on ONE operating picture (the Anduril play, aviation edition).\n"
        "2) TAK/CIVTAK: aircraft position + drone feeds + casualty pins on the same tactical map — air support "
        "coordinates with the PJ team in-ear.\n"
        "3) Lattice mesh extends: drones relay to the aircraft; the aircraft relays beyond line-of-sight for the "
        "operator (long-range comms relay).\n"
        "4) Medevac chain: PJ on the ground → drone delivers meds → aircraft extracts → EMS ground leg (REVA tie) — "
        "one Lattice chain, no handoff gaps.\n"
        "5) Doctrine unchanged: clean original implementation (Lattice concepts only, IP-safe), military-grade "
        "hardening applies to the air nodes.\n"
        "This completes the founder's tie: AVIATION + DRONES + ANDURIL/LATTICE = one air-ops mesh on the COP.")
try:
    req = urllib.request.Request(base + f"/api/issues/{issue_id}/comments",
                                 data=json.dumps({"body": body}).encode(), headers=hdr, method="POST")
    with urllib.request.urlopen(req, timeout=10) as r:
        print("anduril air tie comment ->", r.status)
except urllib.error.HTTPError as e:
    print("ERR", e.code, e.read().decode()[:200])
