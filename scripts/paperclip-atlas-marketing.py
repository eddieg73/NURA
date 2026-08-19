import json, re, urllib.request, urllib.error

def envval(name):
    env = open("/opt/data/profiles/nura/.env").read()
    m = re.search(rf"^{name}=(.+)$", env, re.M)
    return m.group(1).strip().strip('"').strip("'") if m else ""

key = envval("API_SERVER_KEY")
base = "http://127.0.0.1:3101"
hdr = {"User-Agent": "NURA-Hermes/1.0", "Content-Type": "application/json",
       "x-api-key": key, "Authorization": "Bearer " + key}
cid = "999ff375-6128-41cf-b6c8-06b98673a29b"

req = urllib.request.Request(base + f"/api/companies/{cid}/agents", headers=hdr)
d = json.loads(urllib.request.urlopen(req, timeout=10).read())
agents = d if isinstance(d, list) else d.get("agents", [])
atlas = next((a for a in agents if (a.get("name") or "").lower() == "atlas"), None)
aid = atlas["id"] if atlas else None
if not aid:
    print("ATLAS NOT FOUND"); raise SystemExit(1)

issue = {
    "title": "CEO DIRECTIVE (founder): BUILD INTERNAL FB/IG MARKETING ENGINE (Manus-style — Meta acquired Manus Dec 2025)",
    "description": ("FOUNDER 2026-08-02: 'The AI is called Manus. Look how they deployed inside Meta and how it does "
                    "Facebook and Instagram marketing. Copy those skills and build them internally with our team.'\n"
                    "VERIFIED (2026-08-02): Meta acquired Manus (Dec) — Manus connectors on Instagram, Ads Manager, "
                    "WhatsApp Business: content automation, campaign reporting, ad insights Q&A, weekly auto-reports, "
                    "IG ads generator, FB Page → landing page. We replicate CAPABILITIES with OUR stack (clean "
                    "implementation, no copied code). Skill banked: social-media-marketing-ops.\n\n"
                    "=== BUILD SCOPE (Iris CMO owns; Hermes lanes execute) ===\n"
                    "1) Meta Graph API lane: FB Page + IG Business + Ad Account tokens (founder drop, sealed .env "
                    "0600) — insights (spend/CTR/ROAS/top campaigns), posting, IG media\n"
                    "2) Weekly reporting digest (Monday 07:00 EDT cron candidate) — verdict-first\n"
                    "3) Content calendar: 3-5 posts/division/week (clinical claims gate)\n"
                    "4) Creative pipeline: briefs → FLUX3/HeyGen variants → A/B (founder-approved budgets only)\n"
                    "5) Community: IG/FB DMs via Chatwoot (Chatwoot dev's lane)\n"
                    "6) Landing: FB Page → landing tie with the web rebuild (f0d1b461)\n\n"
                    "=== GATES ===\n"
                    "No auto-spend without founder sign-off · healthtech claims gate on every clinical post · tokens "
                    "sealed · FTC disclosure\n"
                    "Evidence: token wiring + first insights pull by 2026-08-06; first weekly digest live by 2026-08-11."),
    "assigneeAgentId": aid, "priority": "high", "status": "todo",
}
try:
    req = urllib.request.Request(base + f"/api/companies/{cid}/issues", data=json.dumps(issue).encode(),
                                 headers=hdr, method="POST")
    with urllib.request.urlopen(req, timeout=10) as r:
        d = json.loads(r.read())
        print("FB/IG marketing directive ->", r.status, d.get("id", d.get("issueId", "?")))
except urllib.error.HTTPError as e:
    print("ERR", e.code, e.read().decode()[:300])
