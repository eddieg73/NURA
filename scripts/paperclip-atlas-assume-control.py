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
    "title": "CEO DIRECTIVE (founder): ATLAS ASSUME CONTROL — finish SaaS-ify priority (turnkey provisioning + app + Medisun go-live) · hire plan + projected cost attached · Hermes does 99%",
    "description": ("FOUNDER 2026-08-02: 'Ask Atlas to assume control and finish this, including the humans "
                    "you will need to hire along with the projected cost. I'm hoping you can do 99% of it.'\n"
                    "SCOPE (assume control of priority 822ef26b + turnkey provisioning engine):\n"
                    "1) TURNKEY PROVISIONING ENGINE: per-tenant instantiation (Hermes profile + Qdrant "
                    "collection + sealed vault + allowlist, NUR-106), connector matrix auto-wiring (Perfex, "
                    "OpenEMR/any-EMR FHIR/SMART/HL7, Chatwoot, Twilio DID, NMI payfac, clinical MCP lanes, "
                    "devices/glasses), credential intake + live probes, 12-lane health board, metering->"
                    "billing. Gates: provisioning PoC 08-12, full matrix 08-28, MEDISUN GO-LIVE 09-15.\n"
                    "2) THE APP: iOS/Android (TestFlight 08-20 target - UNBLOCK the CTO desk), offline LOM "
                    "lane (Qwen 3B/7B GGUF + whisper + NEWS2 + protocol RAG), auth (OpenEMR PKCE).\n"
                    "3) ATLAS OWNS: coordination, vendor engagement, hire funnel, timelines, reporting. "
                    "Hermes executes the software (99% rule).\n"
                    "HUMAN HIRES + PROJECTED COST (contract, 90-day sprint):\n"
                    "- Flutter app devs x2 (app + offline lane): $60-90/hr -> $15-25k total\n"
                    "- SaaS Platform Engineer (tenant provisioning + billing): $50-90/hr -> $8-14k\n"
                    "- QA/test engineer (health board + regression): $30-50/hr -> $3-5k\n"
                    "- Backend Integration Engineer (connector matrix): $50-90/hr -> $8-14k\n"
                    "- Apple/Google account + TestFlight: founder-held creds, $0 (Hermes guides)\n"
                    "TOTAL PROJECTED: $34-58k contract spend for the 90-day SaaS-ify sprint (lighthouse "
                    "included). Radiology/device lanes keep their own budgets (44b5b4d6, e0ea841e).\n"
                    "RULE: humans ONLY where law/physics requires (licensed lanes, statutory, physical "
                    "device testing, app-store/platform accounts, payer phone calls). Everything else = "
                    "Hermes. Founder signs every contract (AI never signs).\n"
                    "REPORTING: Atlas status every Friday 17:00 EST (quiet-portfolio format); blockers "
                    "same-day."),
    "assigneeAgentId": aid, "priority": "critical", "status": "todo",
}
try:
    req = urllib.request.Request(base + f"/api/companies/{cid}/issues", data=json.dumps(issue).encode(),
                                 headers=hdr, method="POST")
    with urllib.request.urlopen(req, timeout=10) as r:
        d = json.loads(r.read())
        print("Atlas assume-control directive ->", r.status, d.get("id", d.get("issueId", "?")))
except urllib.error.HTTPError as e:
    print("ERR", e.code, e.read().decode()[:300])
