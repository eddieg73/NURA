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
    "name": "Twilio & VoIP Engineer",
    "role": "general",
    "title": "Twilio Integration & VoIP Engineer — Grandstream PBX systems",
    "adapter": "hermes_gateway",
    "adapterConfig": {"apiBaseUrl": "http://127.0.0.1:8642/v1"},
    "reportsTo": CTO,
}
try:
    req = urllib.request.Request(base + f"/api/companies/{CID}/agents", data=json.dumps(agent).encode(),
                                 headers=hdr, method="POST")
    with urllib.request.urlopen(req, timeout=8) as r:
        d = json.loads(r.read())
        dev_id = d.get("id")
        print("AGENT ->", r.status, dev_id, d.get("name", "?"))
except urllib.error.HTTPError as e:
    print("AGENT ERR", e.code, e.read().decode()[:250])
    raise SystemExit

issue = {
    "title": "NUR-50: CEO DIRECTIVE — hire Twilio & VoIP Engineer (done by Hermes on CEO behalf) + Grandstream PBX build",
    "description": ("CEO confirmed hire: Twilio & VoIP Engineer (created, hermes_gateway). Scope (founder 2026-08-02):\n\n"
                    "1) TWILIO LANE COMPLETION: creds present in .env (3 vars) — wire SMS + voice MCP tools, webhooks "
                    "for inbound (missed-call text-back, appointment reminders, recall campaigns), verify all 9 "
                    "capabilities (SMS/voice/verify etc.).\n"
                    "2) GRANDSTREAM PBX: configure UCM IP-PBX (UCM63xx or equivalent), SIP trunking to Twilio Elastic "
                    "SIP Trunking, DID provisioning, extension/ring groups/call queues, IVR, voicemail-to-email, "
                    "auto-provisioning of GXP phones, failover paths.\n"
                    "3) MEDISUN CALL FLOW (NUR-36): patient call -> ElevenLabs AI receptionist -> Twilio/Grandstream -> "
                    "Chatwoot (transcript+intent) -> Hermes orchestrator; after-hours + 24/7 AI receptionist per "
                    "manifest M2.\n"
                    "4) APP VOIP: WebRTC dialer (flutter_webrtc) per manifest M1 — clinical dialer, caller-ID masking "
                    "(office line), direct-to-voicemail drop.\n"
                    "5) OPS: call quality monitoring, trunk usage/cost ledger, failover testing, PHI-safe call "
                    "recording policy (consent), numbers inventory (Twilio + DID).\n"
                    "GATES: consent before recording, no PHI in webhook payloads (sanitize), approval-gated trunk "
                    "changes, test calls before go-live."),
    "assigneeAgentId": CEO,
    "priority": "high",
    "status": "todo",
}
try:
    req = urllib.request.Request(base + f"/api/companies/{CID}/issues", data=json.dumps(issue).encode(),
                                 headers=hdr, method="POST")
    with urllib.request.urlopen(req, timeout=8) as r:
        d = json.loads(r.read())
        print("NUR-50 ->", r.status, d.get("id", d.get("issueId", "?")))
except urllib.error.HTTPError as e:
    print("ISSUE ERR", e.code, e.read().decode()[:200])
