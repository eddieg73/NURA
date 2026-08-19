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
ECHO = "32bdda92-e393-4311-bdf2-3a4d4346ee2c"

issue = {
    "title": "NUR-77: TWILIO → OpenEMR + Perfex — SMS wiring (blocked on creds, build ready)",
    "description": ("Founder 2026-08-02: connect Twilio to OpenEMR and Perfex. VERIFIED CURRENT STATE: Twilio "
                    "401 (every pair tested — console refresh required); PERFEX_API_TOKEN absent; OpenEMR OAuth "
                    "absent. Architecture is ready — drops are the only gate.\n"
                    "WIRING PLAN:\n"
                    "1) TWILIO→OPENEMR (patient comms): OpenEMR SMS/notifications via Twilio (appointment "
                    "reminders, recalls) — configure Twilio sender +17274773636 in OpenEMR notification config "
                    "(or bridge script reading patient mobile from OpenEMR API → Twilio API); Mirth keeps PHI "
                    "inbound. Echo owns.\n"
                    "2) TWILIO→PERFEX (staff/lead SMS): Perfex SMS module — Twilio gateway config (SID/token/"
                    "sender) in Perfex settings; leads/customers/staff notifications; verify with a test SMS "
                    "(NUR-43 Phase 1 completion). Tally owns.\n"
                    "3) HERMES SMS CHANNEL as the shared bridge: gateway sms channel enabled (reads the same "
                    ".env pair) — once valid, Hermes itself can send practice SMS.\n"
                    "4) Verification evidence required on this issue (message SID from Twilio API; Perfex "
                    "SMS log; OpenEMR reminder fired).\n"
                    "BLOCKERS (drops): TWILIO_ACCOUNT_SID+AUTH_TOKEN (matching pair from console), "
                    "PERFEX_API_TOKEN, OPENEMR_OAUTH_CLIENT_ID/SECRET. Echo leads; Tally + Florence support."),
    "assigneeAgentId": ECHO, "priority": "high", "status": "todo",
}
try:
    req = urllib.request.Request(base + f"/api/companies/{CID}/issues", data=json.dumps(issue).encode(),
                                 headers=hdr, method="POST")
    with urllib.request.urlopen(req, timeout=10) as r:
        d = json.loads(r.read())
        print("NUR-77 ->", r.status, d.get("id", d.get("issueId", "?")))
except urllib.error.HTTPError as e:
    print("ERR", e.code, e.read().decode()[:200])
