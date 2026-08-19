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
    "body": ("FOUNDER FULL SPEC ATTACHED (2026-08-02): Clinical & Business Command Center (Doximity x NURA "
             "Practice OS). Archived: /opt/data/Obsidian Vault/NURA-OS/App-Product-Spec-v2.md — THE SCOPE "
             "FREEZE reference (with FlutterFlow-Implementation-Guide.md + v1 spec).\n"
             "SUMMARY: 5 bottom-nav modules (News/Ask/Dialer/Scribe/Fax) + 3x4 Practice OS hub (phone, "
             "inbox, schedule, patients, team chat, payments, reputation, analytics, eFax, forms, settings) "
             "+ 6 feature modules (ambient scribe w/ waveform + SOAP/FHIR mapping, clinical copilot w/ RAG "
             "+ RxNorm + ICD/CPT, omnichannel dialer w/ WebRTC/Twilio + AI voice receptionist, eFax hub w/ "
             "AI fax summarizer, surgical/aesthetic suite w/ before-after vault + consents + inventory "
             "decrement, RCM w/ CPT auto-suggest + Stripe/Plaid native payments) + offline SLM cascade "
             "(MedGemma-4B/Qwen3-8B quantized via llama.cpp/mlc_llm -> SQLite queue -> sync) + UI tokens "
             "(#007AFF/#00E5FF accents, #0A0E1A dark / #F8FAFC light, Inter/SF Pro).\n"
             "AUTH DECISION (Hermes rec, founder reviewing): OpenEMR OAuth2 (PKCE) as PRIMARY provider "
             "identity; app session = secure storage + biometric; offline = local session + queued sync + "
             "re-auth on reconnect; Supabase deferred (NUR-58 ruling pending; no second PHI surface). "
             "Flutter team builds auth against OpenEMR OAuth per this decision.\n"
             "MILESTONE MAP: M2 scribe = Module 1+2 · M3 dialer/comms = Module 3+4 · M4 store = Module "
             "5+6 polished; offline SLM = M1 Core Router extension. Scope freeze enforced from now."),
}
try:
    req = urllib.request.Request("http://127.0.0.1:3101/api/issues/265a5af6-90c3-4352-8ec7-5d4b21f9bd9d/comments",
                                 data=json.dumps(comment).encode(), headers=hdr, method="POST")
    with urllib.request.urlopen(req, timeout=10) as r:
        print("COMMENT ->", r.status)
except urllib.error.HTTPError as e:
    print("ERR", e.code, e.read().decode()[:150])
