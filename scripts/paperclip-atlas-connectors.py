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

issues = [
    {"title": "CEO DIRECTIVE (founder): HIRE PERSONAL TRAVEL AGENT + Google Flights/Maps/Calendar connectors",
     "description": ("FOUNDER 2026-08-02: hire a travel agent for me. Connect Google Flights API, Google Maps API, "
                     "Calendar API — full connector surfaces (universal-connector-pattern skill: API + MCP + CLI + "
                     "WEBHOOK for each).\n"
                     "SCOPE: personal + business travel (clinics, Bahamas/Costa Rica/SCA flights — aviation lane tie), "
                     "itineraries to calendar, hotel/rental, visa/entry docs, travel alerts.\n"
                     "HIRE: Travel Agent (hermes_gateway) reporting to founder-lane; CONNECTORS: assign Bridge to wire "
                     "Google Flights (verify current API access — affiliate/keyed), Google Maps (live lane), Google "
                     "Calendar (live lane) — all 4 surfaces each.\n"
                     "Evidence: agent hired + Flights connector status by 2026-08-06.")},
    {"title": "CEO DIRECTIVE (founder): ASSIGN DEVELOPER — CONNECT ALL AVAILABLE APIs (medicine · aviation · AI/AGI · infrastructure · C-suite) — build the data graph",
     "description": ("FOUNDER 2026-08-02: assign a developer to connect to ALL available APIs — medicine, aviation, "
                     "AI/AGI, infrastructure, C-suite MCP type — anything to build the data.\n"
                     "DOCTRINE: universal-connector-pattern — EVERY connection gets API + MCP + CLI + WEBHOOK (four "
                     "surfaces, no exceptions).\n"
                     "OWNER: Bridge (MCP Developer — build, wire & govern all integration lanes) assigned; Atlas "
                     "oversees; domain packs in the skill:\n"
                     "MEDICINE: openFDA/PubMed/CDC (done) · RxNorm · LOINC (key) · DailyMed · ClinicalTrials v2 (done) · "
                     "NIH ODS · Mirth (creds)\n"
                     "AVIATION: Aviation Weather (AWC/ADDS) · NOAA METAR/TAF · OpenSky/ADS-B · NOTAM · eAPIS\n"
                     "AI/AGI: OpenRouter · HF Inference · Gemini (done) · OpenEvidence (key)\n"
                     "INFRASTRUCTURE: Hostinger (done) · Docker · Redis (done) · Qdrant (done) · n8n (done) · Paperclip (done)\n"
                     "C-SUITE/MCP: Notion (token live, share pending) · GHL (403) · Zapier (creds) · Slack/Teams · board\n"
                     "TRAVEL: Google Flights · Maps · Calendar\n"
                     "EXECUTE: audit current lanes vs 4-surface standard (incomplete lanes = finish them) → wire new "
                     "lanes by domain → data flows into the unified data graph (registry: data/evidence-datasets.json "
                     "and lane registry).\n"
                     "Evidence: 4-surface audit + new lanes wired by 2026-08-10; monthly data-graph report.")},
]

for it in issues:
    it["assigneeAgentId"] = aid
    it["priority"] = "high"
    it["status"] = "todo"
    try:
        req = urllib.request.Request(base + f"/api/companies/{cid}/issues", data=json.dumps(it).encode(),
                                     headers=hdr, method="POST")
        with urllib.request.urlopen(req, timeout=10) as r:
            d = json.loads(r.read())
            print("->", r.status, d.get("id", "?"), "|", it["title"][:55])
    except urllib.error.HTTPError as e:
        print("ERR", e.code, e.read().decode()[:150], "|", it["title"][:55])
