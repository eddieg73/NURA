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
TALLY = "fa200fb7-6520-4553-ad62-701b6c0febd5"

issue = {
    "title": "NUR-64: TALLY — build the multi-Gmail -> Perfex email pipeline",
    "description": ("Founder 2026-08-02: ALL practice Gmail accounts must flow into Perfex CRM. Skill: "
                    "multi-gmail-perfex-integration (account registry + app-password pattern + probe).\n"
                    "BUILD:\n"
                    "1) Perfex Email Integration: one mailbox per Gmail account (IMAP imap.gmail.com:993, app "
                    "password) -> Leads (new inquiries) + Tickets (support); sender -> existing contact or "
                    "auto-create with dedupe by email.\n"
                    "2) Hermes mail-triage -> Perfex API: classified emails -> perfex_create_lead/ticket via the "
                    "183-tool lane; idempotency external_ref = gmail:{account}:{message_id}; lead source = "
                    "account name; priority/category from classification.\n"
                    "3) PHI rule: clinical content NEVER in Perfex (scrub before write).\n"
                    "VERIFY per account: IMAP probe OK + test email -> lead/ticket created (paste evidence).\n"
                    "Credential drops needed: Google App Password per account (GMAIL_APP_PW_<NAME> in .env 0600) "
                    "+ Perfex admin access for mailbox config."),
    "assigneeAgentId": TALLY, "priority": "high", "status": "todo",
}
try:
    req = urllib.request.Request(base + f"/api/companies/{CID}/issues", data=json.dumps(issue).encode(),
                                 headers=hdr, method="POST")
    with urllib.request.urlopen(req, timeout=10) as r:
        d = json.loads(r.read())
        print("NUR-64 ->", r.status, d.get("id", d.get("issueId", "?")))
except urllib.error.HTTPError as e:
    print("ERR", e.code, e.read().decode()[:200])
