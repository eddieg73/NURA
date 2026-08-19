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
    "title": "NUR-86: CTO — build Tavus-like avatar video software (NURA Avatar Studio)",
    "description": ("Founder 2026-08-02: build software like tavus.io — photorealistic digital-twin avatars + "
                    "video personalization/scale for the NURA media engine.\n"
                    "REFERENCE: skill video-ai-production (Julian Goldie verified stack: HeyGen avatar from "
                    "30-sec clip, 11Labs voice from 5-min sample, LLM tone scripts, n8n pipeline, ~$1-3/video, "
                    "6+ platform distribution). Tavus differentiator to match: real-time conversational video "
                    "agents (Phase 3).\n"
                    "EXISTING ASSETS (use): HeyGen REST wrapper + CapCut wrapper (media suite), ElevenLabs key "
                    "(voice_id 404 — NUR-73 fix), FLUX3 B-roll (live), bundle.social syndication (wired), n8n "
                    "(deployed), Reel media agent (board), voice-message-ops + tts skills, FLUX3 tools.\n"
                    "BUILD PHASES (CTO + Reel + devs):\n"
                    "1) AVATAR STUDIO CORE: avatar training from short founder clip (HeyGen API lane; fallback "
                    "self-hosted: SadTalker/LivePortrait open-source), voice clone lane (11Labs), lip-sync "
                    "render service with polling.\n"
                    "2) SCRIPT ENGINE: LLM tone-matched scripts (from founder's transcript corpus — the "
                    "camcorder/reverse-engineer method), hook/3-point/CTA structure.\n"
                    "3) PIPELINE: n8n daily run — research (Firecrawl/Reddit/X/HN) -> topic rank -> script -> "
                    "voice -> render -> multi-platform distribution (bundle.social + manual-post guard on X).\n"
                    "4) QC GATE: human review before publish (founder/CMO lane) — Goldie's rule: manual beats "
                    "auto where throttling risk exists.\n"
                    "5) PHASE 3 (Tavus-level): real-time conversational video agent — voice lane + WebRTC "
                    "(founder avatar answers questions live on the site) — later milestone.\n"
                    "EVIDENCE on this issue: avatar trained + test clip rendered + first pipeline run. "
                    "Cost discipline: target <$3/video; free-first where possible."),
    "assigneeAgentId": CTO, "priority": "high", "status": "todo",
}
try:
    req = urllib.request.Request(base + f"/api/companies/{CID}/issues", data=json.dumps(issue).encode(),
                                 headers=hdr, method="POST")
    with urllib.request.urlopen(req, timeout=10) as r:
        d = json.loads(r.read())
        print("NUR-86 ->", r.status, d.get("id", d.get("issueId", "?")))
except urllib.error.HTTPError as e:
    print("ERR", e.code, e.read().decode()[:200])
