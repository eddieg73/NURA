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

issue = {
    "title": "CODE REVIEW + ATLAS DISCUSSION: eddieg73/NURA repo = BRAWLERZ BOX app (not the medical app) — TestFlight 08-20 implications",
    "description": ("HERMES CODE REVIEW (2026-08-02, founder: 'grab the repos, review the code, discuss with Atlas'):\n"
                    "REPO REVIEWED: github.com/eddieg73/NURA (cloned, branch artificial-medic-proposal).\n"
                    "FINDING #1: THE REPO IS BRAWLERZ BOX, NOT THE MEDICAL APP - pubspec name: brawlerz_box; "
                    "features: workouts, nutrition, supplements, classes, QR check-in, AI coach, progress, "
                    "admin dashboard, integrations, auth. Flutter + Riverpod + go_router + fl_chart. "
                    "STRUCTURE: clean features/shared split, repository pattern, 12 features, dark theme, "
                    "single merged PR (feature/brawlerz-box-mvp). QUALITY: solid v1 gym-app architecture - "
                    "good patterns, ~40 screens. This is the HISTORICAL Brawlerz asset (Reg A traction fact).\n"
                    "FINDING #2: THE EA + MEDICAL CLINICIAN APP (priority #1 SaaS-ify) HAS NO CODE ANYWHERE - "
                    "the app lane repo is empty of medical code. TestFlight 08-20 target is at RISK unless the "
                    "CTO desk unblocks (Monday scrum, directive 38dab4c7) AND we scaffold the medical app repo.\n"
                    "ATLAS DISCUSSION POINTS:\n"
                    "1) Brawlerz Box: keep as the fitness SKU (historical), park, or kill? It proves Flutter "
                    "capability for the Reg A + hiring (the app-team evidence).\n"
                    "2) MEDICAL APP: recommend NEW repo nura-medical under @Nuratech-ai - scaffold with the "
                    "App-Interface-Spec (29 slash commands, dual-mode EA/Medical, role matrix, offline LOM "
                    "lane, gateway :8642 wiring) - Hermes can scaffold the skeleton this week (MIT-style, "
                    "sim-first) so the CTO has something to build on instead of a blank page.\n"
                    "3) hermes-driver (MIT AV bridge) PUSHED to @Nuratech-ai - reviewed, tests 5/5 - reference "
                    "pattern for repo governance (internal visibility, deploy key, CI later).\n"
                    "4) CI: add GitHub Actions on NURA (flutter analyze + test) - proves the pipeline for "
                    "TestFlight builds.\n"
                    "ASK ATLAS: reply with (a) Brawlerz keep/park/kill decision, (b) nura-medical scaffold go "
                    "(Hermes builds skeleton by 08-07), (c) CI priority. Founder loop if any conflict."),
    "assigneeAgentId": aid, "priority": "high", "status": "todo",
}
try:
    req = urllib.request.Request(base + f"/api/companies/{cid}/issues", data=json.dumps(issue).encode(),
                                 headers=hdr, method="POST")
    with urllib.request.urlopen(req, timeout=10) as r:
        d = json.loads(r.read())
        print("Atlas discussion ->", r.status, d.get("id", d.get("issueId", "?")))
except urllib.error.HTTPError as e:
    print("ERR", e.code, e.read().decode()[:200])
