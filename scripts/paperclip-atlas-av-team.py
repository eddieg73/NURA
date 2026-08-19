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
    "title": "CEO DIRECTIVE (founder): HIRE AUTONOMOUS VEHICLE TEAM — 'Hermes is the brain, Comma AI is the driver' (openpilot integration, sim-first)",
    "description": ("FOUNDER 2026-08-02: 'Hire a team for Hermes to control the car like comma ai. Hermes is the "
                    "brain, comma ai is the driver.' + asked whether comma has MCP/CLI/API.\n"
                    "VERIFIED (08-02): comma API (api.commadotai.com, JWT) exposes devices/routes/clips/nav "
                    "destinations ONLY - NO actuation commands (safety by design). No official control CLI, no "
                    "MCP. CONTROL LIVES IN openpilot (MIT): controlsd -> panda (open CAN interface) -> car.\n"
                    "HIRE (Atlas): AUTONOMOUS VEHICLE INTEGRATION TEAM (AV eng, controls eng, safety eng):\n"
                    "1) RUN openpilot on OUR hardware (Jetson + panda - both open/MIT) - own the stack\n"
                    "2) BUILD the Hermes<->openpilot control lane: our MCP + CLI + API surfaces (universal "
                    "connector pattern): destination/task -> openpilot controlsd -> panda -> car\n"
                    "3) OBD2 telemetry lane (e234f58c) feeds the brain; openpilot executes; Hermes orchestrates\n"
                    "4) SAFETY ENVELOPE (non-negotiable): sim-first (openpilot PC simulator), then ONE supported "
                    "non-emergency test vehicle, supervised, human override + disengagement handling, no fleet "
                    "deployment until validated, every control action black-box logged\n"
                    "5) The ambulance lane stays HUMAN-driven (lights-and-sirens ADAS is not a product we ship "
                    "until proven safe - separate review gate)\n"
                    "DELIVERABLES: team hired by 2026-08-10 · openpilot simulator running + Hermes bridge PoC "
                    "(sim) by 2026-08-21 · test-vehicle integration plan by 2026-09-01 · supervised test-vehicle "
                    "pilot (gated) by 2026-09-30."),
    "assigneeAgentId": aid, "priority": "high", "status": "todo",
}
try:
    req = urllib.request.Request(base + f"/api/companies/{cid}/issues", data=json.dumps(issue).encode(),
                                 headers=hdr, method="POST")
    with urllib.request.urlopen(req, timeout=10) as r:
        d = json.loads(r.read())
        print("AV team directive ->", r.status, d.get("id", d.get("issueId", "?")))
except urllib.error.HTTPError as e:
    print("ERR", e.code, e.read().decode()[:300])
