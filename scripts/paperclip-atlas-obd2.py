import json, re, urllib.request, urllib.error

def envval(name):
    env = open("/opt/data/profiles/nura/.env").read()
    m = re.search(rf"^{name}=(.+)$", env, re.M)
    return m.group(1).strip().strip('"').strip("'") if m else ""

key = envval("API_SERVER_KEY")
base = "http://127.0.0.1:3101"
hdr = {"User-Agent": "NURA-Hermes/1.0", "Content-Type": "application/json",
       "x-api-key": key, "Authorization": "Bearer " + key}
cid = "999ff375-6128-41cf-b6c8-06b98673a29b"

req = urllib.request.Request(base + f"/api/companies/{cid}/agents", headers=hdr)
d = json.loads(urllib.request.urlopen(req, timeout=10).read())
agents = d if isinstance(d, list) else d.get("agents", [])
atlas = next((a for a in agents if (a.get("name") or "").lower() == "atlas"), None)
aid = atlas["id"] if atlas else None
if not aid:
    print("ATLAS NOT FOUND"); raise SystemExit(1)

issue = {
    "title": "CEO DIRECTIVE (founder): OBD2 VEHICLE TELEMETRY LANE — truck/fly-car CAN comms via OBD-II (Comma AI tech scanned, organic build, READ-ONLY)",
    "description": ("FOUNDER 2026-08-02: look at Comma AI — do they have an API for navigation, can they integrate "
                    "with OBD2; scan their technology and see if we can implement communication via OBD2.\n"
                    "COMMA AI SCAN (verified 08-02):\n"
                    "- Navigation API: YES — api.commadotai.com /v1/navigation/{dongleId}/set_destination, /next, "
                    "/locations (CRUD) — requires comma prime subscription + their device; JWT auth; Mapbox token "
                    "endpoint. Their route/segment API (routes, coords, clips, athena real-time) = good REFERENCE "
                    "pattern for our own fleet telemetry API (4-surface standard).\n"
                    "- OBD2/CAN: openpilot taps CAN via OBD-II port (panda/comma hardware); opendbc = MIT open "
                    "'Python API for your car': DBC file library + CAN parse + high-level car interface "
                    "(carstate: speed/steering/etc.) + functional safety. visiond (their ADAS brain) = closed — "
                    "NOT our lane anyway (we never touch gas/brake/steer).\n"
                    "OUR IMPLEMENTATION (organic, read-only doctrine):\n"
                    "1) PATH A (start): ELM327/STN1110 OBD-II dongle (BT/WiFi/USB) + python-obd -> standard PIDs "
                    "(speed, RPM, coolant, fuel, battery, DTCs) on the truck Jetson\n"
                    "2) PATH B (full): USB-CAN adapter (CANable/gs_usb) -> socketcan on Linux -> python-can + "
                    "opendbc DBC files (MIT; study-open-refs doctrine) -> full CAN telemetry + fault codes\n"
                    "3) PATH C: OpenXC (Ford) if fleet is Ford-based (E-350/Transit ambulances)\n"
                    "LANES: vehicle health watchdogs (check-engine, battery, DEF, fuel, mileage) -> Hermes fleet "
                    "dashboard + silent-OK alerts; trip logging (odometer) = ground-side Avionics Connect "
                    "pattern; dispatch nav via our maps lane (NOT comma nav API).\n"
                    "HARD RULES: READ-ONLY on vehicle bus — no actuation, ever; vehicle data never merges with "
                    "PHI; per-unit sealed config.\n"
                    "DELIVERABLES: OBD2 dongle PoC on a test vehicle (python-obd PID stream -> Hermes) by "
                    "2026-08-14 · CAN bus path (socketcan + DBC) by 2026-08-28 · fleet vehicle-health watchdog "
                    "live by 2026-09-04."),
    "assigneeAgentId": aid, "priority": "medium", "status": "todo",
}
try:
    req = urllib.request.Request(base + f"/api/companies/{cid}/issues", data=json.dumps(issue).encode(),
                                 headers=hdr, method="POST")
    with urllib.request.urlopen(req, timeout=10) as r:
        d = json.loads(r.read())
        print("OBD2 telemetry directive ->", r.status, d.get("id", d.get("issueId", "?")))
except urllib.error.HTTPError as e:
    print("ERR", e.code, e.read().decode()[:300])
