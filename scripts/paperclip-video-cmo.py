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
IRIS = "084cd44f-6570-4370-b8f0-fe66ec8b8baf"

issue = {
    "title": "NUR-88: CMO — video content engine: develop strategy + hire creative team (UGC + Insta-style)",
    "description": ("Founder 2026-08-02: produce videos like my Insta + UGC videos. Excel sheet with the "
                    "content plan coming from founder.\n"
                    "STACK READY (skill video-studio-stack): CapCut + HeyGen + Higgsfield + ElevenLabs "
                    "pipeline wired; ELEVENLABS key live (voice_id fix NUR-73); HEYGEN_API_KEY, "
                    "HIGGSFIELD_API_KEY, CAPCUT_API_KEY = drops pending; FLUX3 B-roll live; bundle.social "
                    "distribution wired; Reel agent on board.\n"
                    "CMO ACTIONS:\n"
                    "1) CONTENT STRATEGY: study founder's Insta (style, hooks, cadence, topics) + the Excel "
                    "sheet when attached; produce the editorial calendar (weekly cadence, platform-specific "
                    "cuts per video-ai-production + Goldie playbook).\n"
                    "2) HIRE the creative team (hermes_gateway, report to CMO): Video Content Strategist, "
                    "UGC Scriptwriter, Editor Lead (CapCut), Thumbnail/Designer. CTO hires the production "
                    "engineers (video devs + Reel) in parallel — coordinate.\n"
                    "3) PRODUCTION WORKFLOW: script -> 11Labs voice -> HeyGen avatar/Higgsfield clips -> "
                    "CapCut edit -> QC gate (founder/CMO) -> publish (manual on X; bundle.social elsewhere).\n"
                    "4) COMPLIANCE: health/marketing claims pass healthtech-marketing-claims-review BEFORE "
                    "publish; UGC honest-format; no deceptive claims.\n"
                    "5) KPIs: 8-12 pieces/week; engagement + follower growth tracked weekly in the CMO "
                    "report; iterate on hooks per analytics.\n"
                    "DELIVER: strategy + roster + calendar + first 3 videos (when keys drop) on this issue."),
    "assigneeAgentId": IRIS, "priority": "high", "status": "todo",
}
try:
    req = urllib.request.Request(base + f"/api/companies/{CID}/issues", data=json.dumps(issue).encode(),
                                 headers=hdr, method="POST")
    with urllib.request.urlopen(req, timeout=10) as r:
        d = json.loads(r.read())
        print("NUR-88 ->", r.status, d.get("id", d.get("issueId", "?")))
except urllib.error.HTTPError as e:
    print("ERR", e.code, e.read().decode()[:200])
