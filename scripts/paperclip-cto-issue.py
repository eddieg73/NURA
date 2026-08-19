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
CTO = "0f81f292-5eea-4c6d-b64b-10b3345d29dd"

issue = {
    "title": "NUR-56: CTO DIRECTIVE — Offline-AI Medical Companion build plan + ADR ruling",
    "description": ("Founder directive 2026-08-02: CTO owns the Offline-AI Medical Companion app build "
                    "(Doximity-feature set; ALL AI on-device; no PHI leaves the phone).\n"
                    "Full spec: docs/manuals/OFFLINE-AI-MEDICAL-COMPANION.md (Hermes repo) + skill "
                    "offline-ai-medical-companion.\n\n"
                    "CTO DELIVERABLES:\n"
                    "1) ADR RULING (blocking): spec = native Kotlin/Compose + SwiftUI; standing ADR = All-Flutter "
                    "(manifest V). Options: (a) All-Flutter, (b) native per-platform, (c) Flutter shell + native ML "
                    "engines. Recommend one with rationale by EOD; founder approves.\n"
                    "2) BUILD PLAN: phases P1 Scribe MVP (8-10wk) -> P2 Assistant -> P3 Fax -> P4 News+Dialer; "
                    "assign leads (Canvas/Pixel/Forge UI, Nexus app integration, Echo VoIP, Ink fax/Documo); "
                    "model packaging (Gemma E2B INT4, FunctionGemma 270m, whisper.cpp Q8, MiniLM) on Lab 1030183; "
                    "FHIR DocumentReference export format from day one.\n"
                    "3) OPEN QUESTIONS: specialty focus, single/multi-user vaults, Wi-Fi-only install default, "
                    "App Store positioning (attorney) — resolve with founder.\n"
                    "4) HARD REQUIREMENTS: offline airplane-mode CI test; encryption/audit log; BAA list "
                    "(Twilio/Bandwidth/Telnyx, Documo/Sfax, self-hosted Sentry); no PHI-touching analytics.\n"
                    "Hermes holds the skills/docs; report plan + ruling on this issue."),
    "assigneeAgentId": CTO,
    "priority": "high",
    "status": "todo",
}
try:
    req = urllib.request.Request(base + f"/api/companies/{CID}/issues", data=json.dumps(issue).encode(),
                                 headers=hdr, method="POST")
    with urllib.request.urlopen(req, timeout=8) as r:
        d = json.loads(r.read())
        print("NUR-56 ->", r.status, d.get("id", d.get("issueId", "?")))
except urllib.error.HTTPError as e:
    print("ERR", e.code, e.read().decode()[:200])
