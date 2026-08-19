import json, re, urllib.request, urllib.error

def envval(name):
    env = open("/opt/data/profiles/nura/.env").read()
    m = re.search(rf"^{name}=(.+)$", env, re.M)
    return m.group(1).strip().strip('"').strip("'") if m else ""

key = envval("API_SERVER_KEY")
base = "http://127.0.0.1:3101"
hdr = {"User-Agent": "NURA-Hermes/1.0", "Content-Type": "application/json",
       "x-api-key": key, "Authorization": "Bearer " + key}
issue_id = "fe997964-f356-417b-8b64-46160a17374b"

body = ("TRUCK TECH SPEC (founder 2026-08-02 — input to the org design; full spec in vault EMSAgency-Spec.md):\n"
        "- Jetson ONE (Orin-class edge AI) PER TRUCK: onboard vision, telemetry CDS (NEWS2 offline), BLE device "
        "ingestion — the truck is an edge node, works in dead zones.\n"
        "- Starlink: sat backhaul (rural 911 coverage).\n"
        "- WiFi: truck AP (scene hotspot, clinic dock, crew tablets).\n"
        "- Bluetooth: BLE patient monitors/devices (11073/IHE PCD lane), stethoscope/otoscope pods.\n"
        "- Mesh phone: Lattice-style vehicle-to-vehicle mesh, no carrier needed (drone-swarm relay tie).\n"
        "- Cellular eSIM: KORE Super SIM (KORE acquired Twilio IoT 2023 — the 'Twilio eSIM partner' = KORE; eSIM "
        "profiles SM-DP+, 400+ networks, multi-IMSI failover, fleet APIs). Issue per device: Jetson modem, mesh "
        "phone, telemetry pods.\n"
        "- Link hierarchy: Starlink → cellular → mesh → BLE; AES everywhere.\n"
        "Ops implication: Fleet/Facilities lead owns the truck stack; Ops owns link failover drills; IT/edge design "
        "feeds the President's 90-day plan.")
try:
    req = urllib.request.Request(base + f"/api/issues/{issue_id}/comments",
                                 data=json.dumps({"body": body}).encode(), headers=hdr, method="POST")
    with urllib.request.urlopen(req, timeout=10) as r:
        print("truck spec comment ->", r.status)
except urllib.error.HTTPError as e:
    print("ERR", e.code, e.read().decode()[:200])
