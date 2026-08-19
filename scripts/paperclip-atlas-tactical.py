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
    "title": "CEO DIRECTIVE (founder + board [D3]): EXECUTE — Axon body-cam lane + ATAK/CIVTAK setup (tactical sensor stack)",
    "description": ("FOUNDER 2026-08-02: 'Embedding Nura in Axon body cam for EMS/first response/tactical medicine. "
                    "I want the atak and civ tak setup. Research all possibilities, seat analysis, execute. Explain "
                    "it to the board and have them improve it. I have given you everything I have been working on.'\n"
                    "BOARD DECISION [D3] banked (vault Advisory-Board.md). EXECUTE:\n\n"
                    "=== 1) DRAFT-ONE-EQUIVALENT (build — fastest proof) ===\n"
                    "BWC audio → whisper transcription → Hermes clinical scribe (SOAP/narrative) → officer/provider "
                    "in-the-loop review → RMS/chart. Own the lane: zero per-seat Axon AI fees. PoC by 2026-08-15.\n"
                    "=== 2) FUSUS PARTNER LANE (integrate, never rebuild) ===\n"
                    "Axon Evidence Partner API (developers.axon.com): read feeds, export evidence, case sync. Partner "
                    "application by 2026-08-31. Fusus = Axon's COP (body/drone/fleet/third-party + CAD) — our feeds "
                    "plug in; Hermes stays the brain.\n"
                    "=== 3) ATAK/CIVTAK SETUP (build — seat analysis done) ===\n"
                    "ATK plugin SDK: casualty pins (MIST/9-line MEDEVAC), telemetry overlays, NURA guidance in-ear. "
                    "CIVTAK for first responders. Plugin scaffold by 2026-08-22; PJ earpiece lane ties (directive "
                    "fa0f9bb7 — currently BLOCKED on CTO canvas; unblock at Monday scrum).\n"
                    "=== 4) BODY CAM = NURA SENSOR NODE ===\n"
                    "Audio→scribe · video→vision cascade (scene/trauma assessment, suggestive only) · livestream→COP "
                    "· tactical medicine guidance (TCCC doctrine).\n\n"
                    "=== OWNERS ===\n"
                    "Hermes: PoC lanes (scribe + whisper pipeline) · Bridge: ATAK plugin + Fusus API wiring · Aero: "
                    "Axon Air drone tie · EMS: agency field rollout (Lauderhill unit = first body-cam deployment) · "
                    "QA: test suite. Atlas: coordination + founder reporting. No Axon hardware spend without founder "
                    "sign-off.\n"
                    "Evidence per milestone on this issue."),
    "assigneeAgentId": aid, "priority": "critical", "status": "todo",
}
try:
    req = urllib.request.Request(base + f"/api/companies/{cid}/issues", data=json.dumps(issue).encode(),
                                 headers=hdr, method="POST")
    with urllib.request.urlopen(req, timeout=10) as r:
        d = json.loads(r.read())
        print("Tactical stack directive ->", r.status, d.get("id", d.get("issueId", "?")))
except urllib.error.HTTPError as e:
    print("ERR", e.code, e.read().decode()[:300])
