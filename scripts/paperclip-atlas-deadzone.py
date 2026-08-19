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
    "title": "CEO DIRECTIVE (founder + board): DEAD-ZONE AGENT — Colibrì + GLM-5.2 sovereign offline tier (D1 synthesis)",
    "description": ("GO from founder (2026-08-02). Advisory Board synthesis [D1, vault Advisory-Board.md]: ship the "
                    "dead-zone agent as the product's signature — GLM-5.2 via Colibrì on an existing computer + "
                    "on-device model in the app + deterministic CDS. Atlas owns; Orion CTO + Helm + Hermes execute.\n\n"
                    "=== WHAT WE HAVE (verified) ===\n"
                    "- Colibrì (JustVugg): pure-C engine, runs GLM-5.2 744B on 25GB RAM + NVMe, NO GPU. MIT.\n"
                    "- GLM-5.2-int4 package: ~370GB on disk (HF: mastouri/GLM-5.2-colibri-int4-g64-with-int8-mtp).\n"
                    "- OLMoE 7B/1B via Colibrì = small-box test (~15GB) — DO THIS FIRST.\n"
                    "- Edge models: Phi-4-mini-flash 3.8B / Qwen3-4B / Gemma 3 (in-app, claims 12-13).\n"
                    "- NEWS2 engine + provider gate already built (telemetry-cds-engine.py).\n\n"
                    "=== EXECUTE (this week, evidence on this issue) ===\n"
                    "1) SMOKE: deploy Colibrì + OLMoE on the cheapest available box (clinic laptop or Lab CPU) — "
                    "'coli chat' + 'coli serve' (OpenAI-compatible) — POST the smoke output. (D-flag: Lab disk = 400GB, "
                    "GLM-5.2-int4 needs ~370GB + datasets — tight; OLMoE first, GLM-5.2 after disk plan.)\n"
                    "2) WIRE: point Hermes at 'coli serve' as a sovereign lane (base_url swap, offline/batch tier).\n"
                    "3) DEMO SPEC (the signature): airplane mode → app voice → on-device STT → edge model or Colibrì "
                    "→ NEWS2 + Ddx → provider gate. Target: demo evidence by Friday 2026-08-08.\n"
                    "4) NUR filing: sovereign tier SKU + pricing model (Midas input; near-zero marginal inference = "
                    "margin moat).\n"
                    "5) PATENT: continuation notes — disk-streaming offline execution as claims 12-13 embodiment "
                    "(attorney package via CTO).\n"
                    "6) HARDWARE ASK: identify the clinic's oldest usable computer (remote-device-control skill can "
                    "inventory it) — that's the demo box.\n\n"
                    "=== RULES ===\n"
                    "- Vendor benchmarks ≠ our validation — smoke evidence required before 'works' claims.\n"
                    "- PHI stays local; sovereign tier = offline/batch + warm-cache, NOT real-time chat.\n"
                    "- No GPU purchases without founder sign-off (Musk: prove the lane for $0 first).\n"
                    "- Acknowledge + assign owners by Monday scrum; first smoke evidence by Thu 2026-08-06."),
    "assigneeAgentId": aid, "priority": "critical", "status": "todo",
}
try:
    req = urllib.request.Request(base + f"/api/companies/{cid}/issues", data=json.dumps(issue).encode(),
                                 headers=hdr, method="POST")
    with urllib.request.urlopen(req, timeout=10) as r:
        d = json.loads(r.read())
        print("Atlas dead-zone directive ->", r.status, d.get("id", d.get("issueId", "?")))
except urllib.error.HTTPError as e:
    print("ERR", e.code, e.read().decode()[:300])
