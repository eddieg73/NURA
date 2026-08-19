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

comment = {
    "body": ("FOUNDER APP SPEC ATTACHED (2026-08-02, from spec images — THE build instructions). Full spec "
             "archived at /opt/data/Obsidian Vault/NURA-OS/App-Product-Spec.md. Summary: 5 screens (Instant AI "
             "Assistant, Clinical Dialer, AI Medical Scribe, Secure Fax, Fax Inbox); Practice-OS scope = AI Voice "
             "Phone System (VoIP/recording/missed-call text back/call pop-ups), Two-Way Text (SMS/group/reminders/"
             "recalls), Online Scheduling (self-booking/waitlists/calendar sync), Patient Comms Hub, Reputation "
             "Management (Google/FB/RealSelf), Payments (deposits/plans/financing/memberships), NURA AI Assistant "
             "(copilot), Clinical Documentation (AI SOAP, eRx, labs, imaging, FHIR, eSign/eFax), Surgical & "
             "Aesthetic Tools (before-after, consents, treatment plans, inventory), RCM (auth/claims/denials/"
             "collections/forecast), Analytics (ops/financials/AI performance/provider metrics), Automation (lead "
             "nurturing, smart workflows, 70%+ admin reduction, patient journeys, 24/7), Integrations (OpenEMR, "
             "GoHighLevel, Twilio, GetFWD, WooCommerce, webhooks, API, data mapping). Store assets: icon 1024, "
             "iPhone 1290x2796, iPad 2048x2732, preview 1920x1080, marketing 1024x500. Sequence the Flutter team "
             "against THIS scope (NUR-81 remains the priority directive).")
}
try:
    req = urllib.request.Request("http://127.0.0.1:3101/api/issues/265a5af6-90c3-4352-8ec7-5d4b21f9bd9d/comments",
                                 data=json.dumps(comment).encode(), headers=hdr, method="POST")
    with urllib.request.urlopen(req, timeout=10) as r:
        print("COMMENT ->", r.status)
except urllib.error.HTTPError as e:
    print("ERR", e.code, e.read().decode()[:150])
