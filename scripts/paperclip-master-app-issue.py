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
CEO = "f2f6e8a6-6d99-4113-9604-1e8259fc1d83"

issue = {
    "title": "NUR-66: PRIME DIRECTIVE — ONE master agnostic app (all-EMR interface) + bundle reframe",
    "description": ("Founder 2026-08-02 reframe: (1) RIS/PACS = SOFTWARE BUNDLE component — imaging financials "
                    "REMOVED from NURA-IMAGING-MASTER-PLAN.md; imaging P&L = practice service-line, not capital "
                    "business. (2) THE PRODUCT = ONE master agnostic app serving providers across ALL EMRs.\n"
                    "Architecture (docs/projects/NURA-SYNTHETIC-CLINICIAN.md PRIME DIRECTIVE): single NURA app "
                    "(voice-first, 6 dashboards, agents, scribe, dialer, fax, imaging bundle) + agnostic interface "
                    "layer = NURA AI Core + Mirth/NextGen Connect per-EMR adapters (Epic, Cerner, eCW, Athena, "
                    "OpenEMR, eMedical) over FHIR R4 + SMART on FHIR + HL7 v2. EMR mapping isolated in adapters — "
                    "never in the app. Onboarding = plug-in adapter.\n"
                    "CTO (Orion): 1) own the master-app architecture (replaces scattered module-first plans); "
                    "2) sequence via the Synthetic-Clinician P0-P10 roadmap (NUR-66 reference); 3) adapter registry "
                    "with per-EMR build order (OpenEMR/eMedical first = our anchor EMRs). SaaS division (DIV-1) "
                    "packages CRM/EMR/RIS/PACS as bundle modules inside the app.\n"
                    "Hermes holds all docs + skills; report architecture + adapter registry on this issue."),
    "assigneeAgentId": CEO, "priority": "high", "status": "todo",
}
try:
    req = urllib.request.Request(base + f"/api/companies/{CID}/issues", data=json.dumps(issue).encode(),
                                 headers=hdr, method="POST")
    with urllib.request.urlopen(req, timeout=10) as r:
        d = json.loads(r.read())
        print("NUR-66 ->", r.status, d.get("id", d.get("issueId", "?")))
except urllib.error.HTTPError as e:
    print("ERR", e.code, e.read().decode()[:200])
