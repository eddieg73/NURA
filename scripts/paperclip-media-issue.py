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
    "name": "NURA Media Agent",
    "role": "general",
    "title": "Content-Lead — AI video production & social syndication (HeyGen/Higgsfield/CapCut/Socialmonials)",
    "adapter": "hermes_gateway",
    "adapterConfig": {"apiBaseUrl": "http://127.0.0.1:8642/v1"},
    "reportsTo": CTO,
}
try:
    req = urllib.request.Request(base + f"/api/companies/{CID}/agents", data=json.dumps(agent).encode(),
                                 headers=hdr, method="POST")
    with urllib.request.urlopen(req, timeout=8) as r:
        d = json.loads(r.read())
        media_id = d.get("id")
        print("AGENT ->", r.status, media_id, d.get("name", "?"))
except urllib.error.HTTPError as e:
    print("AGENT ERR", e.code, e.read().decode()[:250])
    raise SystemExit

issue = {
    "title": "NUR-53: CEO DIRECTIVE — hire NURA Media Agent (done by Hermes) + AI Media Suite build (SOP-5/6/7)",
    "description": ("CEO confirmed hire: NURA Media Agent (created, hermes_gateway, $150/mo, 4h heartbeat). Scope "
                    "(manifest v2 Module 4 + SOP-5/6/7, founder 2026-08-02):\n\n"
                    "PIPELINE: 1) Script: blog/review -> 45s vertical script 2) HeyGen avatar clip (nuratech avatar + "
                    "voice clone) 3) Higgsfield/FLUX3 B-roll 4) CapCut assembly (branded captions) 5) syndication to "
                    "@nuratech.ai + @garrido.eddie (IG/FB/LinkedIn) with UTM -> Perfex.\n"
                    "SOP-5: blog-to-reel (auto) · SOP-6: 5-star testimonial + before/after syndication · SOP-7: "
                    "post-op aftercare video -> Twilio SMS to patient (clinician avatar/voice, 30s).\n"
                    "STACK MAPPING: syndication = bundle.social lane (68 tools, WIRED); video gen = FLUX3 tools "
                    "(available) + HeyGen/Higgsfield/CapCut packages (verify live before wiring — media MCP packages "
                    "mostly E404; use official APIs via wrappers); voice = ElevenLabs (VALID).\n"
                    "GATES: patient-consent for before/after + care videos; no PHI in media; approval before "
                    "publishing; UTM tracking audit; brand voice review by founder."),
    "assigneeAgentId": CEO,
    "priority": "medium",
    "status": "todo",
}
try:
    req = urllib.request.Request(base + f"/api/companies/{CID}/issues", data=json.dumps(issue).encode(),
                                 headers=hdr, method="POST")
    with urllib.request.urlopen(req, timeout=8) as r:
        d = json.loads(r.read())
        print("NUR-53 ->", r.status, d.get("id", d.get("issueId", "?")))
except urllib.error.HTTPError as e:
    print("ISSUE ERR", e.code, e.read().decode()[:200])
