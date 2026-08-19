import json, urllib.request, urllib.error

def env_file(path, names):
    try:
        for line in open(path):
            for n in names:
                if line.startswith(n + "="):
                    return line.strip().split("=", 1)[1].strip("'\"")
    except OSError:
        pass
    return None

key = env_file("/opt/data/paperclip-runtime/mcp.env", ["PAPERCLIP_API_KEY", "API_KEY"])
base = "http://127.0.0.1:3101"
hdr = {"User-Agent": "NURA-Hermes/1.0", "Content-Type": "application/json",
       "x-api-key": key or "", "Authorization": "Bearer " + (key or "")}
CID = "999ff375-6128-41cf-b6c8-06b98673a29b"
CTO = "c454a3cb-3516-4046-b60f-03e0b1bea002"

issue = {
    "title": "NUR-112: Medical device connectivity — bedside (IHE PCD/11073 SDC) + Bluetooth/BLE layer",
    "description": ("Founder 2026-08-02: connect ALL medical devices — cardiac monitors, anesthesia machines, "
                    "ventilators + Bluetooth-enabled devices. Skill built: medical-device-connectivity "
                    "(standards-first + BLE layer).\n"
                    "CTO SEQUENCE:\n"
                    "1) INVENTORY: which devices the clinics actually run (N Miami / Little Haiti / Ft "
                    "Lauderdale): monitor vendors (Philips IntelliVue? GE CARESCAPE? Mindray?), anesthesia/"
                    "vent (Draeger SDC-capable?), BLE devices (CGMs, SpO2, BP cuffs) — evidence on this "
                    "issue BEFORE any gateway purchase.\n"
                    "2) PHASE 1 SIMULATE: hermes-hl7-simulator -> PCD-style ORU^R01 (MDC codes: HR/SpO2/BP/"
                    "RR/EtCO2/vent) -> Mirth -> OpenEMR observations (zero-risk).\n"
                    "3) PHASE 2: IEEE 11073 SDC / OpenICE evaluation for OR/ICU real-time (anesthesia + "
                    "vents).\n"
                    "4) PHASE 3: vendor connectors per inventory + BLE app layer (flutter_blue_plus, "
                    "offline-first -> FHIR Observation -> OpenEMR; vendor clouds secondary, BAA-checked).\n"
                    "5) SAFETY: no device auto-actions; validation before chart writes; device+timestamp in "
                    "record; clinical-grade vs wellness-grade labeling.\n"
                    "Evidence: inventory list + first simulated PCD message through Mirth on this issue."),
    "assigneeAgentId": CTO, "priority": "high", "status": "todo",
}
try:
    req = urllib.request.Request(base + f"/api/companies/{CID}/issues", data=json.dumps(issue).encode(),
                                 headers=hdr, method="POST")
    with urllib.request.urlopen(req, timeout=10) as r:
        d = json.loads(r.read())
        print("NUR-112 ->", r.status, d.get("id", d.get("issueId", "?")))
except urllib.error.HTTPError as e:
    print("ERR", e.code, e.read().decode()[:200])
