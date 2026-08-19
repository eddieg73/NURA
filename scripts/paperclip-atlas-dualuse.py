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
    "title": "CEO DIRECTIVE (founder): DUAL-USE WEARABLES (vision glasses + camera earbuds) — civilian blind/low-vision + military/LE · PJ device connectivity · DEFENSE CONTRACTING roadmap",
    "description": ("FOUNDER 2026-08-02 (board-reviewed, D4): build glasses like Meta + Bluetooth camera earbuds "
                    "that help blind people walk — civilian + military/LE deployment; connect to ALL devices a PJ "
                    "would use + research that environment; enter defense contracting + civilian EMS + "
                    "law-enforcement with our products.\n"
                    "MARKET VERIFIED [V] 2026-08-02:\n"
                    "- Glasses: Ray-Ban Meta Gen 2 (8h, Be My Eyes, Meta SDK for camera streaming), Oakley Meta, "
                    "Envision Ally, Solos AirGo V2, Agiga EchoVision (standalone Android, Transit API)\n"
                    "- EARBUDS = the untapped lane: VueBuds (UW CHI 2026) - binocular cameras in earbuds + "
                    "Qwen2.5-VL: VQA on par with Ray-Ban Meta (3.33 vs 3.32 MOS), OCR 94.3%, <3s latency; "
                    "earbud adoption 150-200x glasses\n"
                    "PRODUCT (dual-use):\n"
                    "CIVILIAN: NURA Vision glasses/earbuds - on-device small VLM (Qwen2.5-VL/Phi-4-vision "
                    "class), obstacle/text/scene audio cueing, offline-first, self-hosted remote assist "
                    "(Be My Eyes-class but ours), wayfinding (OSRM lane), Capsule/Glasses IP (claims 12-13 "
                    "embodiment)\n"
                    "MILITARY/LE: tactical awareness - heads-up threat cueing, CIVTAK/ATAK feed, drone feed "
                    "overlay, spatial audio (L/R cueing), PJ comms earpiece lane - dual-use design, export "
                    "control review (EAR civilian / ITAR variants)\n"
                    "PJ DEVICE CONNECTIVITY (research + integrate ALL PJ gear): TAK/CIVTAK, tactical comms + "
                    "earpieces, drone feeds, night vision, GPS/nav, biometrics, medical devices (LIFEPAK/"
                    "Hamilton/Siemens already), weapon-mounted sensors - everything on Lattice via the 4-"
                    "surface connector standard; PJ environment research dossier by 2026-08-20\n"
                    "DEFENSE CONTRACTING ROADMAP: CMMC 2.0 (Level 2), ITAR/EAR review, SBIR/STTR, GSA "
                    "schedule, prime/sub partnerships (Anduril-class), procurement gates; civilian lanes: FL "
                    "EMS agencies + LE departments (Manatee EMS, Lauderhill); dual-use = one product two "
                    "markets\n"
                    "TEAM: Atlas hires Wearables Product Dev (glasses/earbuds VLM), Defense/GovCon specialist "
                    "(CMMC/ITAR/SBIR), PJ integration dev (works with TAK directive + device lane e0ea841e)\n"
                    "GATES: wearables spec + VueBuds-class PoC plan 2026-08-14 · PJ device inventory + "
                    "research dossier 2026-08-20 · CMMC/ITAR assessment 2026-08-25 · defense roadmap v1 "
                    "2026-09-01 · glasses/earbuds prototype plan 2026-09-15."),
    "assigneeAgentId": aid, "priority": "critical", "status": "todo",
}
try:
    req = urllib.request.Request(base + f"/api/companies/{cid}/issues", data=json.dumps(issue).encode(),
                                 headers=hdr, method="POST")
    with urllib.request.urlopen(req, timeout=10) as r:
        d = json.loads(r.read())
        print("Dual-use wearables directive ->", r.status, d.get("id", d.get("issueId", "?")))
except urllib.error.HTTPError as e:
    print("ERR", e.code, e.read().decode()[:300])
