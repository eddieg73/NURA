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
CTO = "0f81f292-5eea-4c6d-b64b-10b3345d29dd"

agent = {
    "name": "App Integrator (NURA Core Router)",
    "role": "general",
    "title": "App-Backend Integrator — NURA AI Core Router between Flutter and the software stack",
    "adapter": "hermes_gateway",
    "adapterConfig": {"apiBaseUrl": "http://127.0.0.1:8642/v1"},
    "reportsTo": CTO,
}
try:
    req = urllib.request.Request(base + f"/api/companies/{CID}/agents", data=json.dumps(agent).encode(),
                                 headers=hdr, method="POST")
    with urllib.request.urlopen(req, timeout=8) as r:
        d = json.loads(r.read())
        int_id = d.get("id")
        print("AGENT ->", r.status, int_id, d.get("name", "?"))
except urllib.error.HTTPError as e:
    print("AGENT ERR", e.code, e.read().decode()[:250])
    raise SystemExit

issue = {
    "title": "NUR-52: CEO DIRECTIVE — mobilize Flutter leads + hire App Integrator (done by Hermes) for the NURA app build",
    "description": ("CEO action (founder 2026-08-02). STATUS: Flutter leads already on the board and now LIVE on the "
                    "Hermes gateway (adapter fix 2026-08-02): Flutter Mobile Lead, Doximity App Flutter Lead, Doximity "
                    "App Backend Lead, Mobile Release & Store Lead. NEW HIRE: App Integrator (NURA Core Router) — "
                    "created by Hermes on CEO behalf.\n\n"
                    "DIRECTIVE: 1) Flutter leads: scaffold per manifest V (nuratech_ai, lib/ modules dialer/scribe/fax/"
                    "communication/scheduling/rcm_analytics, deps flutter_bloc/record/flutter_webrtc/web_socket_channel/"
                    "pdfview/camera/secure_storage) — resolve app naming (nura-mobile vs nura_health_communications) "
                    "with founder. 2) App Integrator: build the NURA AI Core Router (manifest II) — WebSockets/gRPC/REST "
                    "API layer connecting the app to OpenEMR (REST/FHIR), Perfex (API), Mirth (HL7/FHIR), Chatwoot, "
                    "Firebase (FCM), Twilio (telephony); auth (biometric/secure storage), offline-first sync "
                    "(nura-offline-first-clinician-sync skill), audit logging.\n"
                    "3) INTEGRATION CONTRACTS: swagger/OpenAPI for the /v1 switchboard, tokenized viewer links (SOP-3), "
                    "sanitized payloads (no PHI in app analytics), approval-gated mutations.\n"
                    "GATES: PHI transport encrypted + audited; provider review before clinical feature enablement."),
    "assigneeAgentId": CEO,
    "priority": "high",
    "status": "todo",
}
try:
    req = urllib.request.Request(base + f"/api/companies/{CID}/issues", data=json.dumps(issue).encode(),
                                 headers=hdr, method="POST")
    with urllib.request.urlopen(req, timeout=8) as r:
        d = json.loads(r.read())
        print("NUR-52 ->", r.status, d.get("id", d.get("issueId", "?")))
except urllib.error.HTTPError as e:
    print("ISSUE ERR", e.code, e.read().decode()[:200])
