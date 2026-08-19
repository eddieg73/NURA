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
ATLAS = "f2f6e8a6-0e6c-4f2e-9e5a-3d6f5a2b7c4d"

issue = {
    "title": "NUR-102: Platform build team — recruit 5-6 specialists (iOS-FIRST offline scribe prototype mandate)",
    "description": ("Founder 2026-08-02 hiring plan: complete the platform (Weave CRM + Doximity telecom + "
                    "offline on-device AI) in 6-9 months. Team split confirmed: Amrit = core systems + "
                    "Flutter architecture; Osama = CRM automations + clinical mapping. NEED 5-6 hires:\n"
                    "1) Senior Native/Flutter Bridge Engineer (Telecom) — CallKit (iOS) + ConnectionService "
                    "(Android), WebRTC/Twilio Voice, background audio\n"
                    "2) Edge AI/ML Engineer — on-device Whisper + quantized Llama (Core ML/NNAPI), "
                    "no-overheat/no-drain\n"
                    "3) Senior Backend/VoIP Engineer (Node/Go) — Twilio SIP + WS + Hermes + GHL routing, "
                    "24/7 AI receptionist\n"
                    "4) Healthcare Interop Dev (FHIR/HL7) — with Osama: JSON->HL7/FHIR via Mirth -> OpenEMR "
                    "charts\n"
                    "5) UI/UX Product Designer (healthcare) — RCM dashboards, surgical/aesthetic tools, low "
                    "cognitive load\n"
                    "PLATFORM DECISION (founder approved): iOS FIRST for the offline AI transcription "
                    "prototype — founder is iPad-only (dogfood on own device), Core ML/ANE maturity for "
                    "whisper.cpp quantization, FaceID biometric gate (spec), CallKit consistency vs OEM-"
                    "fragmented ConnectionService, single App Store path (M4 = iOS submission already). "
                    "Android follows after M4.\n"
                    "ATLAS EXECUTE: post the 5-6 roles (paperclip hiring lane or external recruit as "
                    "founder decides), owner-mapped; FIRST technical milestone = offline scribe prototype on "
                    "iPad (whisper.cpp quantized, Core ML) — it dictates memory/architecture for the rest."),
    "assigneeAgentId": ATLAS, "priority": "high", "status": "todo",
}
try:
    req = urllib.request.Request(base + f"/api/companies/{CID}/issues", data=json.dumps(issue).encode(),
                                 headers=hdr, method="POST")
    with urllib.request.urlopen(req, timeout=10) as r:
        d = json.loads(r.read())
        print("NUR-102 ->", r.status, d.get("id", d.get("issueId", "?")))
except urllib.error.HTTPError as e:
    print("ERR", e.code, e.read().decode()[:200])
