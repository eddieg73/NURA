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
    "title": "CEO DIRECTIVE (founder): EMS PROTOCOL SAAS — separate EMS mobile app + glasses link + hummingbird-class on-device LLM + DYNAMIC protocol editor (medical directors/company officers)",
    "description": ("FOUNDER 2026-08-02: 'Separate EMS mobile app connected to the glasses with a small LLM "
                    "(light hummingbird-class) with the EMS protocols already built out. Make the field "
                    "dynamic for EMS medical directors and company officers for that document. We need to "
                    "SaaS this.'\n"
                    "PRODUCT: EMS Protocol SaaS - per-agency tenant (NUR-106), digital protocol library that "
                    "LIVES on the device.\n"
                    "1) SEPARATE EMS APP (mobile, Flutter): field-facing - protocol lookup, EMD trees, "
                    "checklists, voice (EMH lane), device telemetry (NEWS2), drone/glasses links\n"
                    "2) GLASSES CONNECTION: app <- BLE/network -> NURA glasses (Android-native lane) + "
                    "Oakley Tac lane - hands-free protocol prompts + scene audio\n"
                    "3) ON-DEVICE LLM: hummingbird-class (Qwen3-4B/Phi-4/GLM-class GGUF, 1-3GB) - RAG over "
                    "the agency's protocol corpus, OFFLINE-FIRST (protocols must work with zero signal); "
                    "LLM presents the deterministic protocol tree - it never improvises clinical content; "
                    "content = medical-director-approved versions only\n"
                    "4) DYNAMIC PROTOCOL DOCUMENT: role-gated live editor - MEDICAL DIRECTOR (edit + "
                    "approve protocol content, clinical authority), COMPANY OFFICER (admin: versions, "
                    "push, members, audit), FIELD CREW (read-only latest). Versioned (semver), diff-visible, "
                    "approval workflow, signed/audited, push-to-device on approval; device keeps last-good "
                    "version offline\n"
                    "5) SAAS PACKAGE: per-agency tenant (NUR-106), subscription (founder SaaS scheme), "
                    "onboarding = import existing protocol PDFs (OCR lane) -> structured protocol library; "
                    "Medisun/EMS agency = lighthouse; FL 631/COPCN compliance framing\n"
                    "TEAM: Atlas hires EMS App Dev (Flutter), Protocol Platform Dev (editor/versioning/roles), "
                    "Edge LLM Packager (GGUF/RAG on-device) - works with wearables lane 3137a5ab + desktop "
                    "LLM lane dcbd8ccb + SaaS team eee684d5 + EMH skill\n"
                    "GATES: protocol corpus structured + role model spec 2026-08-14 · editor v0 (medical "
                    "director edit/approve/push) 2026-08-28 · on-device LLM PoC (protocol RAG, offline) "
                    "2026-09-01 · app v0 with glasses link 2026-09-15 · lighthouse agency pilot 2026-09-30."),
    "assigneeAgentId": aid, "priority": "critical", "status": "todo",
}
try:
    req = urllib.request.Request(base + f"/api/companies/{cid}/issues", data=json.dumps(issue).encode(),
                                 headers=hdr, method="POST")
    with urllib.request.urlopen(req, timeout=10) as r:
        d = json.loads(r.read())
        print("EMS Protocol SaaS directive ->", r.status, d.get("id", d.get("issueId", "?")))
except urllib.error.HTTPError as e:
    print("ERR", e.code, e.read().decode()[:300])
