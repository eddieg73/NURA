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
ATLAS = "f2f6e8a6-6d99-4113-9604-1e8259fc1d83"
IRIS = "084cd44f-6570-4370-b8f0-fe66ec8b8baf"

issues = [
    {
        "title": "NUR-89: CEO — build product marketing company (top-30 catalog) + meal-plan product line",
        "description": ("Founder 2026-08-02: build a marketing company to sell the top 30 products on 'Roc "
                        "Tonic' (founder to confirm what Roc Tonic is — catalog/list pending; treat as the "
                        "anchor product line for now).\n"
                        "SCOPE:\n"
                        "1) MARKETING COMPANY (division): product pages, funnels, affiliate-ready, CRM "
                        "(Perfex), payments (NMI), analytics — Atlas builds like NURA Capital Markets.\n"
                        "2) VIDEO PRODUCTION COMPANY (ties NUR-88 studio): product videos for all top-30 "
                        "items — script -> 11Labs -> HeyGen/Higgsfield -> CapCut -> publish (video-studio-"
                        "stack skill); CMO creative team + CTO production engineers.\n"
                        "3) MEAL-PLAN PRODUCT LINE (founder's ask: meal plans + grocery lists from food "
                        "likes): NO nutrition app exists in Docker (verified — saas/behive stacks have "
                        "none); the machinery is the skill set: meal-recommendation-shopping-list + "
                        "hrt-house-meal-plan-generator (PDFMonkey JSON->PDF) + nutrition-analyzer + "
                        "instacart-order-ops + weightloss-analyzer + workout-schedule. Wire these into a "
                        "'NURA Meal Studio' product: user food-likes profile -> meal plan PDF + grocery "
                        "list + Instacart order. (Founder to confirm the 'receptive' app reference.)\n"
                        "4) COMPLIANCE: product claims + meal-plan health claims pass "
                        "healthtech-marketing-claims-review; no medical claims on supplements/peptides "
                        "beyond evidence.\n"
                        "DELIVER: division + catalog plan + meal-studio MVP on this issue."},
        "assigneeAgentId": ATLAS,
    },
    {
        "title": "NUR-90: CMO — peptide content engine (reels + blogs): BPC-157, CJC-1295, Retatrutide, Tesamorelin, MOTS-c, Melanotan, PT-141, Oxytocin, Enclomiphene, TRT",
        "description": ("Founder 2026-08-02: create reels and blogs on the latest peptides + TRT.\n"
                        "LIST: BPC-157, CJC-1295, Retatrutide, Tesamorelin, MOTS-c, Melanotan, PT-141, "
                        "Oxytocin, Enclomiphene, TRT + emerging (GLP-1 family).\n"
                        "CMO ACTIONS:\n"
                        "1) CONTENT: weekly blog + 2-3 reels per peptide — educational framing (mechanism, "
                        "evidence, clinical context), NEVER dosing/prescribing claims; every claim "
                        "evidence-linked (PubMed/openFDA lanes — hermes-clinical-evidence-retrieval); "
                        "disclaimers (not FDA-approved for these uses; consult clinician).\n"
                        "2) COMPLIANCE GATE: healthtech-marketing-claims-review BEFORE publish; physician/"
                        "PA review (founder is PA-C — his review = the clinical gate).\n"
                        "3) MACHINERY: extend the Weekly Medical Blog cron (peptides/HRT/GLP-1) + studio "
                        "pipeline (NUR-88) for reels; SEO per video-ai-production.\n"
                        "4) CADENCE: 1 peptide deep-dive/week + 3 reels/week; archive to vault "
                        "(NURA-OS/Peptide-Library.md).\n"
                        "DELIVER: editorial calendar + first peptide deep-dive (evidence-linked) on this "
                        "issue."},
        "assigneeAgentId": IRIS,
    },
]

for it in issues:
    try:
        req = urllib.request.Request(base + f"/api/companies/{CID}/issues", data=json.dumps(it).encode(),
                                     headers=hdr, method="POST")
        with urllib.request.urlopen(req, timeout=10) as r:
            d = json.loads(r.read())
            print(it["title"][:30], "->", r.status, d.get("id", d.get("issueId", "?")))
    except urllib.error.HTTPError as e:
        print("ERR", e.code, e.read().decode()[:150])
