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
    "title": "NUR-103: Platform DB schema + offline sync protocol (PostgreSQL/JSONB + SQLCipher CRDT) — implement",
    "description": ("Founder 2026-08-02 Principal-Architect deliverables 1-3 archived: /opt/data/Obsidian "
                    "Vault/NURA-OS/System-Architecture-DeepSeek.md.\n"
                    "KEY DECISIONS:\n"
                    "1) NEW App Platform DB: PostgreSQL/JSONB (providers/patients/encounters/notes/outbox/"
                    "threads/messages/fax_logs/billing/audit WORM ledger) — PHI stays in OpenEMR; app DB = "
                    "sync + comm + billing + fax metadata + provider-reviewed drafts.\n"
                    "2) SYNC: SQLCipher local store, op-log + LWW CRDT (op_id idempotent, op_ts, base_rev); "
                    "pull-delta + push-outbox; CONFLICT on clinical fields = NEVER auto-resolve -> provider "
                    "review flag; retry 5 attempts -> circuit breaker; WORM hash-chain audit.\n"
                    "3) Deployment: app DB on Clinic 1441409 (localhost-only, post-NUR-68); Mirth v2/v3/FHIR "
                    "R4 lane per existing compose.\n"
                    "CTO: sequence schema migrations + sync engine (M2 scribe needs it), owner = Amrit/"
                    "Flutter; Mirth channel mapping per NUR-82. Deliverables 4-5 (frontend state plan + AI "
                    "pipelines) next.\n"
                    "Evidence: schema applied + first offline->sync test on this issue."),
    "assigneeAgentId": CTO, "priority": "high", "status": "todo",
}
try:
    req = urllib.request.Request(base + f"/api/companies/{CID}/issues", data=json.dumps(issue).encode(),
                                 headers=hdr, method="POST")
    with urllib.request.urlopen(req, timeout=10) as r:
        d = json.loads(r.read())
        print("NUR-103 ->", r.status, d.get("id", d.get("issueId", "?")))
except urllib.error.HTTPError as e:
    print("ERR", e.code, e.read().decode()[:200])
