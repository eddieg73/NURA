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
    "title": "CEO DIRECTIVE (founder): NURA INSIDE SAMSUNG HARDWARE — on-device install lane (phones/tablets/wearables/Knox)",
    "description": ("FOUNDER 2026-08-02: 'WE NEED TO DEVELOP A WAY TO INSTALL NURA INSIDE SAMSUNG HARDWARE.'\n"
                    "SCOPE: deploy NURA (app + Hermes edge profile + small on-device LLM + EMH voice + "
                    "NEWS2 + telemetry) on Samsung hardware: Galaxy phones/tablets (EMS field units, clinic "
                    "devices), Galaxy Watch (wearable telemetry lane - HR/SpO2 to NEWS2), Samsung Knox "
                    "(enterprise lockdown for PHI devices), DeX (desktop mode for clinic workstations).\n"
                    "KEY LANES:\n"
                    "1) SAMSUNG KNOX certified deployment - enterprise enrollment, kiosk/lockdown, per-device "
                    "provisioning (fleet of EMS/clinic devices)\n"
                    "2) ON-DEVICE LLM - small LM (Qwen3-4B/Phi-4/hummingbird-class GGUF/ONNX) on Galaxy "
                    "hardware (NPU via Samsung ENN/ONE API where available) - offline assist, no cloud\n"
                    "3) GALAXY WATCH lane - health sensors -> NEWS2 engine -> provider alerts (wearable "
                    "telemetry, BLE to phone)\n"
                    "4) DEX MODE - NURA desktop UI on DeX for clinic workstations (ties to desktop-app "
                    "lane dcbd8ccb)\n"
                    "5) TACTICAL lane - CIVTAK/ATAK companion on Samsung devices (field EMS/drone lanes; "
                    "ties to TAK directive)\n"
                    "TEAM: Atlas hires Samsung/Knox deployment engineer + on-device LLM mobile engineer "
                    "(works with desktop/edge LLM devs dcbd8ccb + SaaS team eee684d5).\n"
                    "GATES: Knox device study + deployment plan by 2026-08-12 · on-device LLM PoC on a "
                    "Galaxy (GGUF/Qwen3-4B) by 2026-08-20 · Galaxy Watch NEWS2 lane PoC by 2026-09-01 · "
                    "DeX clinic workstation pilot by 2026-09-15. Sim-first, PHI stays on device, "
                    "audit + black box everywhere."),
    "assigneeAgentId": aid, "priority": "high", "status": "todo",
}
try:
    req = urllib.request.Request(base + f"/api/companies/{cid}/issues", data=json.dumps(issue).encode(),
                                 headers=hdr, method="POST")
    with urllib.request.urlopen(req, timeout=10) as r:
        d = json.loads(r.read())
        print("Samsung directive ->", r.status, d.get("id", d.get("issueId", "?")))
except urllib.error.HTTPError as e:
    print("ERR", e.code, e.read().decode()[:300])
