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
ATLAS = "f2f6e8a6-6d99-4113-9604-1e8259fc1d83"

issue = {
    "title": "NUR-81: PRIORITY — Mobile app build (Flutter master app), sequence the team",
    "description": ("Founder 2026-08-02: BUILDING THE MOBILE APP IS A PRIORITY.\n"
                    "STATE: Flutter team exists — Flutter Mobile Lead, Doximity App Flutter Lead, Doximity App "
                    "Backend Lead, Mobile Release & Store Lead (live since adapter fix) + Nexus (App Integrator, "
                    "NUR-52) + App Store compliance skill (ios-app-store-compliance) ready. Scaffold spec = "
                    "manifest V (nuratech_ai: modules dialer/scribe/fax/communication/scheduling/rcm_analytics; "
                    "bloc/record/webrtc/pdfview/camera/secure-storage) + 5-screen map (Instant AI Assistant, "
                    "Clinical Dialer, AI Medical Scribe, Secure Fax, Fax Inbox) reviewed implementation-ready.\n"
                    "CEO ACTIONS:\n"
                    "1) DECIDE app name (nura-mobile vs nura_health_communications) — founder needs a ruling "
                    "(ask Eddie directly if needed).\n"
                    "2) SEQUENCE the build: scaffold -> Core Router (WebSockets/gRPC/REST -> OpenEMR/Perfex/"
                    "Mirth/Chatwoot/Firebase/Twilio; biometric auth; offline-first sync; audit) -> modules in "
                    "order (scribe first? dialer? — recommend scribe + fax for clinical value) -> screens -> "
                    "store prep.\n"
                    "3) UNBLOCK list: Twilio creds (dialer), Documo key (fax), OpenEMR OAuth (scribe/charting), "
                    "Firebase SA (push) — founder drops.\n"
                    "4) MILESTONES: M1 scaffold+Core Router, M2 scribe+fax vertical slice, M3 dialer+comms, M4 "
                    "store submission (iOS first — compliance skill ready).\n"
                    "Report the build plan + first milestone on this issue. Hermes holds the spec + skills."),
    "assigneeAgentId": ATLAS, "priority": "high", "status": "todo",
}
try:
    req = urllib.request.Request(base + f"/api/companies/{CID}/issues", data=json.dumps(issue).encode(),
                                 headers=hdr, method="POST")
    with urllib.request.urlopen(req, timeout=10) as r:
        d = json.loads(r.read())
        print("NUR-81 ->", r.status, d.get("id", d.get("issueId", "?")))
except urllib.error.HTTPError as e:
    print("ERR", e.code, e.read().decode()[:200])
