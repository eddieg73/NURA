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
CMO = "084cd44f-6570-4370-b8f0-fe66ec8b8baf"

issue = {
    "title": "NUR-57: CMO DIRECTIVE — enforce NURA proprietary branding (product lineup)",
    "description": ("Founder 2026-08-02: corrected proprietary lineup is CANON. Doc: "
                    "docs/manuals/NURA-PRODUCT-LINEUP.md + skill nura-product-lineup.\n\n"
                    "EXTERNAL NAMES ONLY: NURA CRM (healthcare/med-spa CRM) · NURA ERP (ops/accounting/inventory/"
                    "multi-location) · Nura Claw (autonomous agent orchestration) · Nura Tron (clinical NLP/medical AI "
                    "intelligence — competitive advantage) · NURA MCP (integration framework) · Long-Term Memory "
                    "Framework (conversational continuity).\n\n"
                    "CMO OWNERSHIP:\n"
                    "1) Audit all external surfaces (apex site, carepilot, app store copy, media assets, patient "
                    "facing docs) — strip vendor/infra names (Perfex, Paperclip, OpenEMR, Mirth, Mem0, Qdrant, "
                    "OpenRouter, Twilio, Documo, Hostinger, bundle.social, HeyGen, ElevenLabs, Firebase); replace "
                    "with NURA names only.\n"
                    "2) Positioning: NuraTech.ai = integrated provider of medical intelligence + clinical automation "
                    "+ business operations 'powered by proprietary NURA technology'.\n"
                    "3) Claims gate: no unsupported clinical claims, no FDA language (review via "
                    "healthtech-marketing-claims-review skill).\n"
                    "4) Coordinate with Reel (media) + Beacon (store copy) + Pixel/Canvas (app surfaces).\n"
                    "Report audit + replacements on this issue."),
    "assigneeAgentId": CMO,
    "priority": "high",
    "status": "todo",
}
try:
    req = urllib.request.Request(base + f"/api/companies/{CID}/issues", data=json.dumps(issue).encode(),
                                 headers=hdr, method="POST")
    with urllib.request.urlopen(req, timeout=8) as r:
        d = json.loads(r.read())
        print("NUR-57 ->", r.status, d.get("id", d.get("issueId", "?")))
except urllib.error.HTTPError as e:
    print("ERR", e.code, e.read().decode()[:200])
