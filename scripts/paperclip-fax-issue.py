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
    "name": "Documo & Fax Engineer",
    "role": "general",
    "title": "Documo Fax Engineer — eFax inbox, OCR, chart auto-filing",
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
    "title": "NUR-51: CEO DIRECTIVE — hire Documo & Fax Engineer (done by Hermes on CEO behalf) + fax build",
    "description": ("CEO confirmed hire: Documo & Fax Engineer (created, hermes_gateway). Scope (founder 2026-08-02):\n\n"
                    "1) DOCUMO LANE LIVE: MCP lane built (documo_send_fax/get_fax/list_faxes/fax_status, wrapper reads "
                    "DOCUMO_API_KEY from .env) — complete wiring when key drops; webhook receiver for INBOUND faxes "
                    "(status callbacks + delivery notifications).\n"
                    "2) eFAX INBOX (manifest M1): inbound fax OCR + AI summarization + auto-filing into OpenEMR patient "
                    "charts (documents API / Mirth MDM channel); unassigned fax queue with clinician triage.\n"
                    "3) OUTBOUND FAX AUTOMATION: lab orders, referrals, prior-auth packets, HIPAA cover sheets; "
                    "sanitized content, delivery confirmations.\n"
                    "4) NUMBER PROVISIONING: Documo DIDs, HIPAA compliance (TRS/PHI-safe), fax quality + delivery "
                    "monitoring.\n"
                    "5) DECISION: Documo = canonical fax lane (resolves Documo-vs-native); Twilio fax not used.\n"
                    "GATES: PHI fax content only to OpenEMR charts (never Perfex/Chatwoot), cover-sheet consent policy, "
                    "test fax round-trip before go-live."),
    "assigneeAgentId": CEO,
    "priority": "high",
    "status": "todo",
}
try:
    req = urllib.request.Request(base + f"/api/companies/{CID}/issues", data=json.dumps(issue).encode(),
                                 headers=hdr, method="POST")
    with urllib.request.urlopen(req, timeout=8) as r:
        d = json.loads(r.read())
        print("NUR-51 ->", r.status, d.get("id", d.get("issueId", "?")))
except urllib.error.HTTPError as e:
    print("ISSUE ERR", e.code, e.read().decode()[:200])
