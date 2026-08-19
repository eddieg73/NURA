import json, re, urllib.request, urllib.error

def envval(name):
    env = open("/opt/data/profiles/nura/.env").read()
    m = re.search(rf"^{name}=(.+)$", env, re.M)
    return m.group(1).strip().strip('"').strip("'") if m else ""

key = envval("API_SERVER_KEY")
base = "http://127.0.0.1:3101"
hdr = {"User-Agent": "NURA-Hermes/1.0", "Content-Type": "application/json",
       "x-api-key": key, "Authorization": "Bearer " + key}
issue_id = "b5ca0fd1-39df-4a97-ae19-0cf47aa6db10"

body = ("ORG DOCTRINE (founder 2026-08-02) — MUSK MODEL + ANDURIL LATTICE:\n"
        "The five companies are ONE SYSTEM on one nervous system (Hermes + MCP + telemetry + Mission Control = our "
        "Lattice). Every company is both a CUSTOMER and a SUPPLIER to the others:\n"
        "- Nuratech core = the platform + the product (SaaS) every company dogfoods.\n"
        "- Assurance = one books for all five.\n"
        "- Capital Markets = cash park (funds Aero hardware, founder-gated).\n"
        "- Aero = AED/meds before the truck + scene intel + show cash.\n"
        "- EMS = MIH patients → Medisun → Solis quality/HCC → revenue.\n"
        "Partners (clinics/fire/hospitals/REVA/SaaS tenants) plug into ONE platform — the Lattice is the moat. "
        "Full map: vault Ecosystem-Synergy-Map.md. Atlas: reflect this in division charters; no company is a silo.")
try:
    req = urllib.request.Request(base + f"/api/issues/{issue_id}/comments",
                                 data=json.dumps({"body": body}).encode(), headers=hdr, method="POST")
    with urllib.request.urlopen(req, timeout=10) as r:
        print("ecosystem doctrine ->", r.status)
except urllib.error.HTTPError as e:
    print("ERR", e.code, e.read().decode()[:200])
