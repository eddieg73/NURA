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

# find NUR-102 by scanning all issues for the title
import urllib.parse
req = urllib.request.Request(base + "/api/companies/999ff375-6128-41cf-b6c8-06b98673a29b/issues?limit=200", headers=hdr)
with urllib.request.urlopen(req, timeout=20) as r:
    data = json.loads(r.read())
issues = data if isinstance(data, list) else data.get("issues", data.get("data", []))
target = None
for it in issues:
    t = (it.get("title") or "")
    if "NUR-102" in t or "5-6 specialists" in t or "offline scribe prototype" in t:
        target = it
        break
if not target:
    print("NUR-102 not found — issue list may be capped; skip nudge")
    raise SystemExit

print("found:", target.get("identifier"), target.get("status"))
comment = {
    "body": ("FOUNDER CHECK-IN (2026-08-02): has the 5-6 specialist hire plan executed? Verified: the "
             "current roster (64 agents) shows NO new specialist hires since this issue — Bridge/Healthcare "
             "UX Designer/Edge AI/ML Engineer/Mobile Telecom Bridge Engineer predate the issue (created "
             "07-31). All agents ARE keyed (gateway apiKeys present) — training status: OK. EXECUTE: post "
             "the 5-6 roles (hire lane or external recruit per founder) with owners + first milestone "
             "(offline scribe on iPad); report by Monday scrum."),
}
try:
    req = urllib.request.Request(base + f"/api/issues/{target['id']}/comments", data=json.dumps(comment).encode(),
                                 headers=hdr, method="POST")
    with urllib.request.urlopen(req, timeout=10) as r:
        print("NUDGE ->", r.status)
except urllib.error.HTTPError as e:
    print("ERR", e.code, e.read().decode()[:150])
