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
CTO = "0f81f292-5eea-4c6d-b64b-10b3345d29dd"

issue = {
    "title": "NUR-76: CTO EXECUTE — WENO EPCS for OpenEMR (selected), install in Docker",
    "description": ("Founder 2026-08-02: select + install EPCS for OpenEMR. SELECTED: WENO Exchange EZ Integration "
                    "(WENO Online module) — verified: $119/yr/prescriber base, EPCS add-on with Identity Proofing "
                    "+ 6-digit OTP, DEA 1311.120-compliant, no-code for OpenEMR v7.0.2+, minutes setup, direct "
                    "network (Surescripts alternative). Alternatives rejected: Ensora/NewCrop (higher cost flow), "
                    "Surescripts native (requires EHR certification + third-party DEA audit — overkill).\n"
                    "EXECUTE (CTO):\n"
                    "1) OpenEMR Docker (1441409): install WENO Online (WOL) module via OpenEMR Modules admin; "
                    "PERSIST module files in the openemr volume (survives container recreation);\n"
                    "2) Register WENO account (online.wenoexchange.com, EZ Integration service type); map "
                    "prescribers (Eddie PA-C, NPI 1154381580, DEA MG5963296) + clinics;\n"
                    "3) EPCS add-on: Identity Proofing (IDP) of the prescriber + OTP 2FA workflow for Schedule "
                    "II-V orders;\n"
                    "4) Test with test patient + test pharmacy before ANY live order; document the config in "
                    "docs/manuals (EPCS section);\n"
                    "5) Verification evidence on this issue (module enabled, prescriber mapped, EPCS flagged).\n"
                    "FOUNDER STEPS (parallel): WENO registration + IDP with OTP token; DEA renewal by 2026-09-30 "
                    "(EPCS requires active DEA).\n"
                    "Sequence: after Docker access ruling (NUR-68) for host-side OpenEMR container access."),
    "assigneeAgentId": CTO, "priority": "high", "status": "todo",
}
try:
    req = urllib.request.Request(base + f"/api/companies/{CID}/issues", data=json.dumps(issue).encode(),
                                 headers=hdr, method="POST")
    with urllib.request.urlopen(req, timeout=10) as r:
        d = json.loads(r.read())
        print("NUR-76 ->", r.status, d.get("id", d.get("issueId", "?")))
except urllib.error.HTTPError as e:
    print("ERR", e.code, e.read().decode()[:200])
