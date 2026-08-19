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
    "title": "CEO DIRECTIVE (founder): HIRE MEDICAL DEVICE INTEGRATION SPECIALIST — MUST work with the Mirth Connect developer (joint device-data lane)",
    "description": ("FOUNDER 2026-08-02: hire a medical device integration specialist, and they must work with the "
                    "next-gen Mirth Connect developer.\n\n"
                    "=== ROLE: MEDICAL DEVICE INTEGRATION SPECIALIST (hermes_gateway) ===\n"
                    "1) DEVICE CONNECTIVITY: monitors, ventilators, BLE sensors, infusion pumps — standards ONLY "
                    "(IEEE 11073, IHE PCD-01, ISO/IEEE 11073-20601, HL7 v2 ORU) per the medical-device-connectivity "
                    "skill\n"
                    "2) TELEMETRY FEED: device waveforms/vitals → NEWS2 deterministic CDS (telemetry-cds-engine) → "
                    "provider-gated alerts — device data NEVER scored by an LLM\n"
                    "3) DEVICE INVENTORY: clinic + EMS truck devices (remote-device-control lane), BLE pod map "
                    "(steth/otoscope/glucose), 11073 agent/manager stack\n"
                    "4) CONNECTOR STANDARD: universal-connector-pattern (API + MCP + CLI + webhook) for every device "
                    "lane\n\n"
                    "=== MANDATORY JOINT WORKSTREAM (non-negotiable) ===\n"
                    "Work WITH the next-gen Mirth Connect developer (interop squad — Meridian):\n"
                    "- Device messages (IHE PCD-01 → HL7 v2 → FHIR R4 observation bundles) routed through Mirth "
                    "channels into OpenEMR/EHR\n"
                    "- Channel design: device lane → Mirth (validation, translation, ACK) → FHIR endpoint\n"
                    "- Joint deliverables below carry BOTH owners' evidence\n"
                    "- PITFALL: device data is high-volume/low-latency — channel throttling + dead-letter handling "
                    "required (hermes-hl7-simulator for testing)\n\n"
                    "=== DELIVERABLES ===\n"
                    "1) Device inventory + connectivity plan (clinic + truck) — by 2026-08-10\n"
                    "2) 11073/PCD-01 → Mirth channel PoC (simulated devices) — by 2026-08-20\n"
                    "3) First live device feed → NEWS2 → provider gate — by 2026-08-31\n"
                    "Evidence from BOTH specialists on each deliverable."),
    "assigneeAgentId": aid, "priority": "high", "status": "todo",
}
try:
    req = urllib.request.Request(base + f"/api/companies/{cid}/issues", data=json.dumps(issue).encode(),
                                 headers=hdr, method="POST")
    with urllib.request.urlopen(req, timeout=10) as r:
        d = json.loads(r.read())
        print("Device specialist directive ->", r.status, d.get("id", d.get("issueId", "?")))
except urllib.error.HTTPError as e:
    print("ERR", e.code, e.read().decode()[:300])
