import json, re, urllib.request, urllib.error

def envval(name):
    env = open("/opt/data/profiles/nura/.env").read()
    m = re.search(rf"^{name}=(.+)$", env, re.M)
    return m.group(1).strip().strip('"').strip("'") if m else ""

key = envval("API_SERVER_KEY")
base = "http://127.0.0.1:3101"
hdr = {"User-Agent": "NURA-Hermes/1.0", "Content-Type": "application/json",
       "x-api-key": key, "Authorization": "Bearer " + key}
issue_id = "92ef029b-0dab-4b1a-862d-93465cefd965"

body = ("FOUNDER ADDITION (2026-08-02): hire ANOTHER CHATWOOT DEVELOPER to work with the Perfex and OpenEMR "
        "developers — Chatwoot is the omnichannel support/patient-communication surface of the stack (core CRM "
        "lane, self-hosted).\n"
        "Scope: Chatwoot <-> Perfex (customer/contact sync, ticket-to-deal), Chatwoot <-> OpenEMR (patient "
        "message intake, appointment comms), webhook/API integration, widget + channels (email/SMS/Telegram/WhatsApp).\n"
        "Roster note: Loom covers Chatwoot workflows (n8n) — the hire is the dedicated Chatwoot DEVELOPER (true gap, "
        "no existing owner).\n"
        "Add to the squad: Tally (Perfex) · Florence (OpenEMR) · Meridian (Mirth) · Loom (n8n) · QA · + NEW Chatwoot "
        "Developer. Squad deliverable date stands: integration spec + test suite by 2026-08-10.")
try:
    req = urllib.request.Request(base + f"/api/issues/{issue_id}/comments",
                                 data=json.dumps({"body": body}).encode(), headers=hdr, method="POST")
    with urllib.request.urlopen(req, timeout=10) as r:
        print("Chatwoot dev addition ->", r.status)
except urllib.error.HTTPError as e:
    print("ERR", e.code, e.read().decode()[:200])
