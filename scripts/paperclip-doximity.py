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
    "title": "NUR-101: Adopt Doximity blueprint into app (Directory/NPPES live, SQLCipher, masked push, ephemeral AI, BAA register)",
    "description": ("Founder 2026-08-02 blueprint archived: /opt/data/Obsidian Vault/NURA-OS/Doximity-"
                    "Blueprint.md. BUILT + VERIFIED: scripts/provider-verify.py (NPPES v2.1) — LIVE TEST "
                    "NPI 1154381580 = verified (A, PA-C, Surgical PA).\n"
                    "ADOPT (CTO/Flutter team):\n"
                    "1) DIRECTORY trust wall: provider signup -> NPPES verify (provider-verify.py) + state "
                    "board + MFA handshake; no public self-registration.\n"
                    "2) OFFLINE STORE: SQLCipher-encrypted SQLite (PendingNotes etc.) — wipe on logout/expiry "
                    "(upgrade the FlutterFlow SQLite layer).\n"
                    "3) MASKED NOTIFICATIONS: Firebase FCM payloads NEVER contain PHI — 'New secure message "
                    "received' + in-app fetch after biometric (policy, enforced in the app).\n"
                    "4) EPHEMERAL AI: drafts processed in-memory; purge on copy; no PHI in logs (matches "
                    "draft-only doctrine).\n"
                    "5) BAA REGISTER: data/vendor-baa.json — Twilio/Documo/FCM tiers pending; self-hosted = "
                    "isolated; DeepSeek/Gemini/OpenRouter = NON-PHI only. Golden rule: no BAA + not "
                    "self-hosted = no patient data.\n"
                    "Evidence: NPPES verify output + BAA register on this issue."),
    "assigneeAgentId": CTO, "priority": "high", "status": "todo",
}
try:
    req = urllib.request.Request(base + f"/api/companies/{CID}/issues", data=json.dumps(issue).encode(),
                                 headers=hdr, method="POST")
    with urllib.request.urlopen(req, timeout=10) as r:
        d = json.loads(r.read())
        print("NUR-101 ->", r.status, d.get("id", d.get("issueId", "?")))
except urllib.error.HTTPError as e:
    print("ERR", e.code, e.read().decode()[:200])
