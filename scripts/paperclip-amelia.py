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
    "title": "NUR-107: Build Amelia — autonomous inbox agent (n8n loop + Hermes routing + ElevenLabs briefing)",
    "description": ("Founder 2026-08-02 Dan Martell blueprint (skill autonomous-inbox-agent): Soul/Identity/"
                    "User persona files; n8n 15-min loop: Gmail ingest -> Hermes categorize (Archive/Draft/"
                    "Urgent) -> switch -> drafts to Gmail Create Draft / archive / urgent summaries batched "
                    "08:00 -> ElevenLabs MP3 briefing -> secure channel.\n"
                    "CTO EXECUTE:\n"
                    "1) GMAIL: verify gws CLI OAuth for nura@nuratech.ai (automation email) — evidence "
                    "(unread fetch works) on this issue.\n"
                    "2) N8N WORKFLOW: build the loop per skill (3 nodes + switch; respond-to-webhook where "
                    "needed). Stage 1 = LABEL + DRAFT ONLY (never send).\n"
                    "3) HERMES ROUTING: system prompts per persona files (soul/identity/user) — categorize "
                    "into the 3 buckets + style-guided drafts.\n"
                    "4) ELEVENLABS: daily 08:00 urgent-summary MP3 (Sarah voice, LIVE) -> deliver to "
                    "Telegram/secure folder.\n"
                    "5) TRUST ROLLOUT: Stage 1 (observe) -> founder grades daily -> Stage 2 (refine soul "
                    "file) -> Stage 3 (auto-send low-risk ONLY after 95% accuracy; high-stakes always "
                    "draft+manual).\n"
                    "6) COST: 15-min LLM loop is expensive — batch cadence (15m script probe + 1h LLM) "
                    "per cost doctrine.\n"
                    "Evidence: first loop run + 3 categorized samples + draft outputs on this issue."),
    "assigneeAgentId": CTO, "priority": "high", "status": "todo",
}
try:
    req = urllib.request.Request(base + f"/api/companies/{CID}/issues", data=json.dumps(issue).encode(),
                                 headers=hdr, method="POST")
    with urllib.request.urlopen(req, timeout=10) as r:
        d = json.loads(r.read())
        print("NUR-107 ->", r.status, d.get("id", d.get("issueId", "?")))
except urllib.error.HTTPError as e:
    print("ERR", e.code, e.read().decode()[:200])
