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
    "title": "CEO DIRECTIVE (founder): PRIORITY — BUILD THE APP (interface spec) + connector layer + hummingbird baked in",
    "description": ("FOUNDER 2026-08-02: build this as PRIORITY. Interface spec = vault App-Interface-Spec.md "
                    "(EA/MEDICAL dual-mode, 29 slash commands, shared thread). Apple Developer creds AVAILABLE "
                    "(Beacon lane ready).\n\n"
                    "=== BUILD SCOPE ===\n"
                    "1) APP (Flutter, iPhone-first): dual-mode interface per spec; Canvas (Mobile Engineering Lead) "
                    "owns; Beacon (Apple Developer) owns signing/TestFlight. Installable on founder's iPhone.\n"
                    "2) CONNECTOR LAYER (the nervous system between Hermes and everything):\n"
                    "   - Hermes API server (:8642 /v1) = the app's gateway (already live)\n"
                    "   - Perfex connector (CRM: clients/tickets/tasks — REST API lane)\n"
                    "   - OpenEMR connector (clinical: charts/labs/meds — openemr-clinical MCP)\n"
                    "   - Chatwoot connector (omnichannel inbox — webhooks/API)\n"
                    "   - ALL behind the interface layer: the app talks ONE protocol (Hermes /v1); the connectors "
                    "fan out to Perfex/OpenEMR/Chatwoot via their lanes. n8n = orchestration only (doctrine).\n"
                    "3) HUMMINGBIRD BAKED IN: Colibri (JustVugg) + GLM-5.2 = the sovereign inference endpoint inside "
                    "the interface layer (offline/batch tier; dead-zone capability in both EA and MEDICAL modes). "
                    "Edge fallback: on-device Phi/Gemma (offline-ai-agent).\n\n"
                    "=== OWNERS ===\n"
                    "- Canvas: app build + connector client code\n"
                    "- Beacon: Apple signing/TestFlight + App Store compliance (ios-app-store-compliance skill)\n"
                    "- Bridge: MCP lanes wiring (Perfex/OpenEMR/Chatwoot already registered)\n"
                    "- Hermes: API gateway + hummingbird endpoint integration\n"
                    "- QA & Test Engineering Lead: interface + connector test suite\n\n"
                    "=== DELIVERABLES ===\n"
                    "1) Connector architecture diagram + endpoint map (by 2026-08-06)\n"
                    "2) App skeleton with dual-mode UI + command palette (by 2026-08-13)\n"
                    "3) Hummingbird endpoint wired into the layer (by 2026-08-15)\n"
                    "4) TestFlight build for founder (by 2026-08-20)\n"
                    "Evidence on this issue per milestone. Founder reviews UI before TestFlight."),
    "assigneeAgentId": aid, "priority": "critical", "status": "todo",
}
try:
    req = urllib.request.Request(base + f"/api/companies/{cid}/issues", data=json.dumps(issue).encode(),
                                 headers=hdr, method="POST")
    with urllib.request.urlopen(req, timeout=10) as r:
        d = json.loads(r.read())
        print("App priority directive ->", r.status, d.get("id", d.get("issueId", "?")))
except urllib.error.HTTPError as e:
    print("ERR", e.code, e.read().decode()[:300])
