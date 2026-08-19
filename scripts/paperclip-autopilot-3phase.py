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
CTO = "c454a3cb-3516-4046-b60f-03e0b1bea002"

issue = {
    "title": "NUR-99: 3-PHASE AUTOPILOT GOAL — sequence into existing NURs (comm/dialer, core pipes, RAF analytics)",
    "description": ("Founder 2026-08-02 (/autopilot goal, archived: /opt/data/Obsidian Vault/NURA-OS/"
                    "Autopilot-3Phase-Goal.md). NOT new work — DEDUPE into existing NURs:\n"
                    "PHASE 1 (comms): Flutter Doximity-style dialer = NUR-81 M3 + App-Product-Spec-v2 Module "
                    "3; Twilio caller-ID proxy bridge = NUR-77 (Echo); Zoom Video SDK telehealth = M3 "
                    "extension — FLAG: Zoom licensing/BAA; Twilio WebRTC alternative evaluated.\n"
                    "PHASE 2 (core): Perfex<->OpenEMR SMART-on-FHIR pipe = NUR-82 + openemr-perfex-integration; "
                    "fax vision ingestion Qwen2-VL = NUR-92 (ride the vision cascade free-VL lane); ThaiRIS "
                    "MWL <-> Orthanc :4242 + OHIF-in-Flutter (WebView embed) = NUR-75 + imaging-stack.\n"
                    "PHASE 3 (PRIMARY - RAF analytics): cross-modal engine (LOINC + imaging + voice) = "
                    "NUR-91 + RATCHET + predictive-clinical-analytics; LangGraph/Ruflo AUDIT NODE before "
                    "OpenEMR commit — intercept vague docs vs severe labs -> real-time warning (exact text "
                    "in the goal); PROVIDER DECIDES (never auto-commit; compliant coding doctrine); WORM "
                    "ledger = hash-chain + R2 snapshots, Supabase deferred per NUR-58 (CTO rules on the "
                    "store).\n"
                    "CTO: produce the sequencing plan (which NUR owns which phase-3 piece + owners + dates) "
                    "on this issue; RAF panel = Solis MA (285 pts, RAF 1.27)."),
    "assigneeAgentId": CTO, "priority": "high", "status": "todo",
}
try:
    req = urllib.request.Request(base + f"/api/companies/{CID}/issues", data=json.dumps(issue).encode(),
                                 headers=hdr, method="POST")
    with urllib.request.urlopen(req, timeout=10) as r:
        d = json.loads(r.read())
        print("NUR-99 ->", r.status, d.get("id", d.get("issueId", "?")))
except urllib.error.HTTPError as e:
    print("ERR", e.code, e.read().decode()[:200])
