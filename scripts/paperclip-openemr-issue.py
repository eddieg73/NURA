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
DEV = "e073d73b-d8f0-4044-9b17-c96144ca18bf"

issue = {
    "title": "NUR-44: OpenEMR Concierge Medicine, HRT, Peptide & GLP-1 Program Build",
    "description": ("Build scope for OpenEMR (founder 2026-08-02). Program: concierge medicine + hormone replacement "
                    "therapy + peptides + GLP-1 programs.\n\n"
                    "CONCIERGE: membership tiers (annual/monthly retainer) · direct-pay/membership fee sheets · priority "
                    "scheduling rules · membership ledger synced to Perfex (sanitized billing per manifest).\n"
                    "HRT: protocol templates (testosterone, estrogen, thyroid) · encounter forms (LBF layout-based forms) · "
                    "baseline+monitoring lab panels with cadence (follow-up schedules) · dose titration templates · "
                    "informed-consent forms.\n"
                    "PEPTIDES/GLP-1: program workflows (semaglutide, tirzepatide, peptide protocols) · medication templates "
                    "with titration schedules · contraindication/black-box screening fields · prior-auth tracking · "
                    "supply/inventory tracking · refill cadence + follow-up visit templates.\n"
                    "TECHNICAL: LBFs, fee sheets/CPT + non-covered service codes, orders sets, patient-portal messaging "
                    "templates, care-plan templates, OpenEMR REST/FHIR exposure for the NURA app.\n\n"
                    "GATES: all clinical content = clinician-reviewed (founder approves templates before activation) · "
                    "PHI stays in OpenEMR (KVM4) · no auto-prescribing — order drafting only, provider authorization "
                    "required · coding suggestions marked as suggestions.\n"
                    "BLOCKER: OpenEMR API/DB credentials must be dropped (~/uploads) to move lane from mock to live."),
    "assigneeAgentId": DEV,
    "priority": "high",
    "status": "todo",
}
try:
    req = urllib.request.Request(base + f"/api/companies/{CID}/issues", data=json.dumps(issue).encode(),
                                 headers=hdr, method="POST")
    with urllib.request.urlopen(req, timeout=8) as r:
        d = json.loads(r.read())
        print("NUR-44 ->", r.status, d.get("id", d.get("issueId", "?")))
except urllib.error.HTTPError as e:
    print("ERR", e.code, e.read().decode()[:200])
