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
    "title": "CEO DIRECTIVE (founder): DEPLOY FULL DOXIMITY + WEAVE FEATURE SUITES ON THE NURA APP — Documo fax · provider dialer · patient comms — connected to everything",
    "description": ("FOUNDER 2026-08-02 (expands eee684d5): deploy ALL Doximity app features + ALL Weave features "
                    "on the NURA mobile app, with Documo fax setup, Twilio provider number, authorized caller-ID "
                    "presentation, connected to everything.\n"
                    "DOXIMITY FEATURE SUITE (provider layer):\n"
                    "1) VERIFIED PROVIDER IDENTITY: NPI-linked profiles, credential verification, directory "
                    "(clinician lookup by name/specialty)\n"
                    "2) DOXIMITY-STYLE DIALER: outbound calls from the app present the PRACTICE'S OWN number on "
                    "caller ID (legal model — Truth in Caller ID Act 47 USC 227(e): authorized numbers only, "
                    "practice-owned/verified caller IDs; NEVER arbitrary spoofing — compliance note filed)\n"
                    "3) HIPAA-SECURE MESSAGING: encrypted text/photo between providers + care teams\n"
                    "4) FAX: Documo e-fax (key pending) + Twilio Fax DID — in-app fax send/receive, fax-to-chart "
                    "pipeline (existing lane)\n"
                    "5) SECURE VIDEO: telehealth consults (provider-to-provider + patient)\n"
                    "6) CLINICAL NEWS + CME + DRUG LOOKUP (RxNorm/OpenFDA lanes live)\n"
                    "WEAVE FEATURE SUITE (patient layer):\n"
                    "1) TWO-WAY PATIENT TEXTING (SMS via Twilio 727) — threaded, auto-replies, opt-out\n"
                    "2) APPOINTMENT REMINDERS (SMS/email, confirm/cancel)\n"
                    "3) MISSED-CALL TEXT-BACK (call -> SMS follow-up)\n"
                    "4) ONLINE SCHEDULING + INT AKE FORMS (digital forms)\n"
                    "5) REVIEWS MANAGEMENT (Google/FB tie)\n"
                    "6) PAYMENT LINKS (NMI lane)\n"
                    "7) AI ANSWERING ASSISTANT (VERONICA lane — reception agent)\n"
                    "8) UNIFIED INBOX: voice/SMS/email/fax in one queue (Chatwoot tie)\n"
                    "CONNECTED TO EVERYTHING: OpenEMR (appointments/charts), Perfex (tickets/tasks), Chatwoot "
                    "(omnichannel), Documo (fax), Twilio (SMS/voice), NMI (payments), Google Workspace, n8n "
                    "(orchestration) — ONE gateway, role-scoped (App-Role-Matrix.md).\n"
                    "CRED GATES (must drop before provisioning): Twilio SID+Auth (401/20003) · Documo key · "
                    "Meta tokens (reviews lane).\n"
                    "DELIVERABLES: feature map + tenant model by 2026-08-08 · dialer PoC (authorized caller ID) "
                    "by 2026-08-15 · fax live by 2026-08-21 · patient messaging v1 by 2026-08-21 · full "
                    "Doximity+Weave core in app by 2026-09-15 (TestFlight 08-20 ships core app first)."),
    "assigneeAgentId": aid, "priority": "high", "status": "todo",
}
try:
    req = urllib.request.Request(base + f"/api/companies/{cid}/issues", data=json.dumps(issue).encode(),
                                 headers=hdr, method="POST")
    with urllib.request.urlopen(req, timeout=10) as r:
        d = json.loads(r.read())
        print("Doximity+Weave directive ->", r.status, d.get("id", d.get("issueId", "?")))
except urllib.error.HTTPError as e:
    print("ERR", e.code, e.read().decode()[:300])
