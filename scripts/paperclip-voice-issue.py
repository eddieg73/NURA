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
CTO = "0f81f292-5eea-4c6d-b64b-10b3345d29dd"

issue = {
    "title": "NUR-73: VOICE WORKFLOWS — fix ElevenLabs voice ID + audio briefing/media pipeline",
    "description": ("QUEUED (founder 2026-08-02): develop the audio-message stack.\n"
                    "1) FIX ElevenLabs: configured voice_id returns 404 voice_not_found (verified) — list voices "
                    "(GET /v1/voices), pick the executive persona voice, update config tts provider/voice; "
                    "re-verify with a probe. Edge = working fallback meanwhile.\n"
                    "2) VOICE BRIEFINGS: daily/weekly audio digests (scrum, CME, license, market) delivered as "
                    "Telegram voice bubbles (skill voice-message-ops; JARVIS cadence: status -> blocker -> next).\n"
                    "3) AUDIO MEDIA: podcast-style clips from NURA docs (two-voice) for Reel syndication — "
                    "scripted + founder-approved before publish.\n"
                    "4) EMH voice variant for clinical briefings (safety-first tone).\n"
                    "SKILL: voice-message-ops (built). OWNER: Orion schedules; Reel (media) implements 2-3; "
                    "Hermes holds provider state."),
    "assigneeAgentId": CTO, "priority": "medium", "status": "todo",
}
try:
    req = urllib.request.Request(base + f"/api/companies/{CID}/issues", data=json.dumps(issue).encode(),
                                 headers=hdr, method="POST")
    with urllib.request.urlopen(req, timeout=10) as r:
        d = json.loads(r.read())
        print("NUR-73 ->", r.status, d.get("id", d.get("issueId", "?")))
except urllib.error.HTTPError as e:
    print("ERR", e.code, e.read().decode()[:200])
