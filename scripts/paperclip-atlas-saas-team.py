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
    "title": "CEO DIRECTIVE (founder): HIRE SaaS CONNECTIVITY TEAM — multi-tenant app plumbing (payfac model) + Twilio FAX number + DOXIMITY-STYLE provider line",
    "description": ("FOUNDER 2026-08-02: 'Have Atlas hire a SaaS team to make sure the mobile app can connect — "
                    "sort of like we do with a payfac and different MID or phone company. I have TWILIO so we need "
                    "to spin up a FAX number and a number for the provider like Doximity.'\n"
                    "THE MODEL (payfac analogy): a payment facilitator runs ONE master MID serving many "
                    "sub-merchants. NURA runs ONE platform (Hermes gateway :8642, per-tenant profiles NUR-106) "
                    "serving many provider orgs + many roles (MD/PA/NP/RN/paramedic/lab). The SaaS team owns the "
                    "plumbing that makes 'one brain, many tenants' work.\n"
                    "HIRE (Atlas): (1) SAAS PLATFORM ENGINEER — tenant onboarding, isolation, metering/billing "
                    "(payfac-style per-tenant revenue), lifecycle; (2) BACKEND INTEGRATION ENGINEER — app "
                    "connectivity: auth (OpenEMR PKCE), role scoping, MCP lane fan-out, webhooks; (3) TELECOM/"
                    "CPaaS ENGINEER — Twilio lanes (below).\n"
                    "TWILIO LANES (we own Twilio — 727-477-3636 system number; creds currently 401/20003 — "
                    "re-drop SID+Auth required BEFORE provisioning):\n"
                    "1) FAX NUMBER: Twilio Fax (Elastic SIP trunk + fax) OR Documo (key pending) — decision: "
                    "Twilio Fax for immediate inbound/outbound clinical fax; Documo as the document pipeline when "
                    "key lands. Number to provision: dedicated FAX DID.\n"
                    "2) PROVIDER LINE (Doximity-style): verified provider voice/SMS number for clinicians — "
                    "provider identity verification flow (NPI-linked), HIPAA-conscious messaging lane, call "
                    "routing to the right role (on-call PA / lab / radiology), separate from the consumer line.\n"
                    "DELIVERABLES: SaaS team hired by 2026-08-10 · tenant onboarding v1 (payfac-style: signup -> "
                    "profile -> role scoping) by 2026-08-18 · FAX DID + provider DID provisioned (after cred "
                    "re-drop) by 2026-08-14 · provider-verification flow v1 by 2026-08-21."),
    "assigneeAgentId": aid, "priority": "high", "status": "todo",
}
try:
    req = urllib.request.Request(base + f"/api/companies/{cid}/issues", data=json.dumps(issue).encode(),
                                 headers=hdr, method="POST")
    with urllib.request.urlopen(req, timeout=10) as r:
        d = json.loads(r.read())
        print("SaaS connectivity team directive ->", r.status, d.get("id", d.get("issueId", "?")))
except urllib.error.HTTPError as e:
    print("ERR", e.code, e.read().decode()[:300])
