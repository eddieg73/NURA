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
    "body": ("FOUNDER DIRECTIVE 2026-08-02 (clear direction + on-time): DATED MILESTONES for the app build. "
             "Clock starts at the Docker access ruling (NUR-68) — target dates are +weeks from ruling:\n"
             "M1 (Wk 2): scaffold + Core Router (auth, offline-first, audit) — DONE means CI green + demo "
             "build\n"
             "M2 (Wk 4): Scribe + Fax vertical slice (clinical value first) — test patient end-to-end\n"
             "M3 (Wk 6): Dialer + Comms (Twilio lane) — call test evidence\n"
             "M4 (Wk 8): Store submission (iOS first — compliance skill ready) — asset pack per App-Product-"
             "Spec\n"
             "TRACKING: weekly status in Monday scrum (owner: Canvas/Flutter lead reports vs milestones); "
             "ANY slip >1 week = escalate to founder with a recovery plan. Scope freeze per App-Product-Spec "
             "(no feature adds until M4)."),
}
try:
    req = urllib.request.Request("http://127.0.0.1:3101/api/issues/265a5af6-90c3-4352-8ec7-5d4b21f9bd9d/comments",
                                 data=json.dumps(comment).encode(), headers=hdr, method="POST")
    with urllib.request.urlopen(req, timeout=10) as r:
        print("COMMENT ->", r.status)
except urllib.error.HTTPError as e:
    print("ERR", e.code, e.read().decode()[:150])
