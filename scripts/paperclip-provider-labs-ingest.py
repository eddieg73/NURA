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
    "title": "NUR-92: Provider Labs ingestion BUILT (Documo fax + email -> OCR -> review queue) — keys to wire",
    "description": ("Founder 2026-08-02: build Provider Labs ingestion with Documo + email (API/CLI/MCP).\n"
                    "BUILT + VERIFIED (Hermes box):\n"
                    "- scripts/provider-labs-ingest.py — CLI: --check-documo (Documo API Bearer, received "
                    "faxes), --check-email (gws mail search, PDF attachments), --queue (review queue "
                    "data/provider-labs/queue.json), --review <id> (provider-review gate); silent-when-clean "
                    "(watchdog pattern)\n"
                    "- MCP lane provider-labs (mcp-installs/provider-labs/server.py): 4 tools (documo_ingest, "
                    "email_ingest, queue_status, review_item) — initialize/tools/list smoke OK; registered in "
                    "config (mcp_servers.provider_labs)\n"
                    "- OCR stage: pymupdf NOT installed yet (uv install pending) — extraction lands when "
                    "installed; queue/ingest lanes already functional\n"
                    "GATES (drops): DOCUMO_API_KEY (fax lane) · gws Gmail OAuth for nura@nuratech.ai (email "
                    "lane) — both probed gracefully, lane shows the exact missing-key message\n"
                    "NEXT (CTO/Florence): install pymupdf into python-packages; wire queue -> NUR-91 pipeline "
                    "modules (OCR -> extraction -> interpretation -> provider review); cron 6h ingest check "
                    "when keys land. Evidence on this issue."),
    "assigneeAgentId": CTO, "priority": "high", "status": "todo",
}
try:
    req = urllib.request.Request(base + f"/api/companies/{CID}/issues", data=json.dumps(issue).encode(),
                                 headers=hdr, method="POST")
    with urllib.request.urlopen(req, timeout=10) as r:
        d = json.loads(r.read())
        print("NUR-92 ->", r.status, d.get("id", d.get("issueId", "?")))
except urllib.error.HTTPError as e:
    print("ERR", e.code, e.read().decode()[:200])
