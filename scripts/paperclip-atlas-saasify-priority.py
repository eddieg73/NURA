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
    "title": "CEO DIRECTIVE (founder): PRIORITY #1 NEXT WEEK — SAAS-IFY THE EA + MEDICAL CLINICIAN (the dual-mode assistant = THE ONE OFFER)",
    "description": ("FOUNDER 2026-08-02: 'Priority number 1 next week is to get this EA and medical clinician "
                    "SaaSed.'\n"
                    "THE ONE OFFER (Martell review alignment): the dual-mode assistant — EA mode (ops) + Medical "
                    "Clinician mode (provider-gated clinical assist) — as a per-tenant SaaS for OTHER providers. "
                    "This is the headline product; everything else is support.\n"
                    "SCOPE (next week, 08-03 -> 08-09):\n"
                    "1) TENANT MODEL: per-tenant Hermes Profiles (NUR-106) — signup -> credentialing (NPI/cert "
                    "tiers, Provider-Credentialing-Process.md) -> profile + role scoping (App-Role-Matrix) -> "
                    "numbers issued (Twilio/Documo lanes)\n"
                    "2) APP: TestFlight 08-20 stands (Beacon + Apple creds); dual-mode UI is the product surface\n"
                    "3) GATEWAY/LANES: Hermes :8642 /v1 already live; MCP fan-out (OpenEMR/Perfex/Chatwoot) per "
                    "tenant; n8n orchestration only\n"
                    "4) PRICING + BILLING: per-clinic SaaS package ($1-3k/mo target) — payfac-style per-tenant "
                    "billing (NMI lane) — pricing pack by 08-06\n"
                    "5) LIGHTHOUSE: one clinic fully live on the stack (Medisun = the anchor) — the proof sale\n"
                    "6) MARKETING: quiet until lighthouse — then the acquisition lane (marketing directive "
                    "72e41c89 aligns after lighthouse)\n"
                    "WEEK GATES: Mon scrum = alignment + NUR-110 (RIS/PACS/EMR config) unblock · 08-06 pricing + "
                    "tenant onboarding v1 · 08-07 lighthouse demo ready · 08-09 Friday evidence: tenant "
                    "onboarding demo + lighthouse plan signed\n"
                    "RELATED: app directive a0054c6c · SaaS team eee684d5 · Doximity+Weave 1ed5d4a9 · "
                    "credentialing process · RCM 05943ac5 · fee schedules (Medisun $300/$60 PMPM)\n"
                    "OWNERS: Atlas (coordinator) · Canvas (app) · Bridge (tenant/gateway) · Beacon (Apple) · "
                    "Hermes (backend) · QA. Founder = final sign-off."),
    "assigneeAgentId": aid, "priority": "critical", "status": "todo",
}
try:
    req = urllib.request.Request(base + f"/api/companies/{cid}/issues", data=json.dumps(issue).encode(),
                                 headers=hdr, method="POST")
    with urllib.request.urlopen(req, timeout=10) as r:
        d = json.loads(r.read())
        print("SaaS-ify EA+Medical priority directive ->", r.status, d.get("id", d.get("issueId", "?")))
except urllib.error.HTTPError as e:
    print("ERR", e.code, e.read().decode()[:300])
