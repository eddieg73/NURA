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
    "title": "CEO DIRECTIVE (founder): Establish NURA AERO — separate drone swarm division (Verge Aero scale, Anduril doctrine)",
    "description": ("FOUNDER 2026-08-02: NEW SEPARATE DIVISION. Hundreds-of-drones swarm tech (Verge Aero model) with "
                    "Anduril-style autonomy. Skill built: drone-swarm-division (doctrine, tech stack, regulatory, "
                    "security). Atlas owns staffing + division P&L.\n\n"
                    "=== DIVISION MANDATE ===\n"
                    "1) Entertainment shows (Verge model): 100-500 drone light shows — choreography in sim (Gazebo/SITL) "
                    "→ validated → executed; mission file = the product.\n"
                    "2) Clinical logistics: defib/meds delivery pods, clinic-to-clinic transport, disaster mass-casualty "
                    "resupply (RATCHET/tactical-medicine tie).\n"
                    "3) Aerial monitoring + event coverage lanes.\n"
                    "4) Sky/UAP-adjacent monitoring at events (founder interest; [V]/[U] tags, no claims).\n\n"
                    "=== DOCTRINE (Anduril) ===\n"
                    "Lattice-style common operating picture · machine-speed autonomy, human-on-the-loop · mesh swarm "
                    "networking (no single point of failure) · any-sensor-any-effector payload swap · edge AI onboard · "
                    "failsafe hierarchy (geofence → RTL → avoidance → parachute).\n\n"
                    "=== STACK (verified standards) ===\n"
                    "MAVLink · PX4/ArduPilot (SITL first) · QGroundControl/MAVSDK · RTK GPS cm-precision · Boids/formation "
                    "algorithms · simulation before ANY real flight.\n\n"
                    "=== ATLAS ACTIONS ===\n"
                    "1) Hire Division Lead (hermes_gateway wired; name: Aero Lead) + assign under CEO.\n"
                    "2) File division directive issue with first deliverables: (a) SITL 100+ drone swarm sim proof "
                    "(b) FAA waiver roadmap (107.29/107.39/107.31 + Remote ID) (c) show-safety SOP (d) payload pod spec "
                    "(lights + defib).\n"
                    "3) Division P&L + revenue model: shows fund clinical logistics capability.\n"
                    "4) No hardware purchases without founder sign-off (sim-first doctrine).\n"
                    "Evidence: division established + lead hired + first sim milestone by 2026-08-22."),
    "assigneeAgentId": aid, "priority": "high", "status": "todo",
}
try:
    req = urllib.request.Request(base + f"/api/companies/{cid}/issues", data=json.dumps(issue).encode(),
                                 headers=hdr, method="POST")
    with urllib.request.urlopen(req, timeout=10) as r:
        d = json.loads(r.read())
        print("Aero division directive ->", r.status, d.get("id", d.get("issueId", "?")))
except urllib.error.HTTPError as e:
    print("ERR", e.code, e.read().decode()[:300])
