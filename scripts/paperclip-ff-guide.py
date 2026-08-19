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

comment = {
    "body": ("FOUNDER BUILD GUIDE ATTACHED (2026-08-02): FlutterFlow implementation guide — archived at "
             "/opt/data/Obsidian Vault/NURA-OS/FlutterFlow-Implementation-Guide.md. Layers: (1) SQLite offline "
             "failsafe (PendingNotes table, 0=queued/1=synced), (2) API routing engine (Mirth_Router HL7 SIU/"
             "ADT + Documo_Fax + Twilio_Voice groups with [variable] substitution), (3) custom Dart for local "
             "SLM + audio (Future-based actions, flutter_sound/FFI), (4) native revenue cycle via GHL API (no "
             "external checkout), (5) Sign-Note webhook: SQLite flip -> n8n -> OpenEMR via Mirth + Perfex "
             "billing trigger.\n"
             "AUTH DECISION (Hermes recommendation, founder reviewing): PRIMARY = OpenEMR OAuth2 (PKCE) — "
             "provider identity = OpenEMR user; app session via secure storage + biometric; offline = local "
             "session + queued sync, re-auth on reconnect. Supabase = deferred (NUR-58 ruling pending; avoid "
             "a second PHI surface). Build the auth layer against OpenEMR OAuth per this decision; revisit "
             "only if non-EMR users are required. Flutter team: implement per guide + milestones M1-M4."),
}
try:
    req = urllib.request.Request("http://127.0.0.1:3101/api/issues/265a5af6-90c3-4352-8ec7-5d4b21f9bd9d/comments",
                                 data=json.dumps(comment).encode(), headers=hdr, method="POST")
    with urllib.request.urlopen(req, timeout=10) as r:
        print("COMMENT ->", r.status)
except urllib.error.HTTPError as e:
    print("ERR", e.code, e.read().decode()[:150])
