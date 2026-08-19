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
    "title": "CEO DIRECTIVE (founder): NURA x LATTICE/ANDURIL — PJ Special Forces integration (TAK/CIVTAK + earpiece) + TIE ALL IDEAS",
    "description": ("FOUNDER 2026-08-02: combine NURA technology with Lattice mesh / Anduril technology FOR SPECIAL "
                    "FORCES PJ (Pararescue). An earpiece is ALREADY in place — NURA integrates into it. Integrate "
                    "with SAMSUNG ATAK (Android Tactical Assault Kit) and CIVTAK (civilian TAK for first responders). "
                    "Tie ALL founder ideas together into one system.\n\n"
                    "=== THE PJ LANE (tactical medicine) ===\n"
                    "- Earpiece AI: hands-free TCCC guidance (hemorrhage → airway → resp → circ → hypothermia), "
                    "med/telemetry prompts, drone + scene intel whispered in-ear (tactical-medicine-swat + RATCHET "
                    "doctrine)\n"
                    "- Telemetry: BLE patient monitors (11073/IHE PCD lane) → NURA CDS (NEWS2) → provider-gated "
                    "guidance, even offline\n"
                    "- Mesh: Lattice-style mesh (drone + truck + operator) — no carrier dependence, AES-encrypted "
                    "(military-grade-hardening)\n"
                    "- ATAK/CIVTAK PLUGIN: NURA as a TAK plugin — casualty pins (MIST/9-line MEDEVAC), live "
                    "telemetry overlays, drone feeds, Lattice COP inside the TAK map\n"
                    "- Drone tie: Aero swarm delivers AED/meds to the operator; landing/coordinates via TAK\n\n"
                    "=== TIE ALL IDEAS (synthesis — vault Ecosystem-Synergy-Map.md) ===\n"
                    "ONE nervous system: Hermes/MCP + Lattice mesh + TAK + glasses/Capsule + Jetson trucks + "
                    "hummingbird (GLM-5.2) + EMS + Aero + clinics + app. Every founder idea is a node on ONE graph: "
                    "the field operator (PJ), the ambulance, the drone, the clinic, and the board all share the same "
                    "operating picture.\n\n"
                    "=== ATLAS EXECUTE ===\n"
                    "1) Research lane: ATAK/CIVTAK plugin architecture + PJ earpiece integration paths (evidence-"
                    "first; no classified claims — [V]/[U] tags)\n"
                    "2) File build issues: (a) TAK plugin spec (b) earpiece integration spec (c) mesh overlay "
                    "architecture\n"
                    "3) Owners: Aero lead (mesh/drone) · EMS (telemetry) · Hermes (NURA CDS + TAK plugin dev) · "
                    "military-grade hardening applies\n"
                    "4) Partner lane: Anduril-adjacent capability mapping (Lattice concepts only — clean original "
                    "implementation, IP-safe)\n"
                    "5) Board: Bezos + Zuckerberg now lead the companies (10-advisor board; Zuck = platforms/"
                    "wearables lane)\n"
                    "Evidence: TAK plugin feasibility doc by 2026-08-10; earpiece integration plan by 2026-08-15."),
    "assigneeAgentId": aid, "priority": "critical", "status": "todo",
}
try:
    req = urllib.request.Request(base + f"/api/companies/{cid}/issues", data=json.dumps(issue).encode(),
                                 headers=hdr, method="POST")
    with urllib.request.urlopen(req, timeout=10) as r:
        d = json.loads(r.read())
        print("PJ/TAK directive ->", r.status, d.get("id", d.get("issueId", "?")))
except urllib.error.HTTPError as e:
    print("ERR", e.code, e.read().decode()[:300])
