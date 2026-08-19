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

# 1. Create the SaaS division company
try:
    req = urllib.request.Request(base + "/api/companies",
                                 data=json.dumps({"name": "NURA Imaging SaaS Division",
                                                  "description": "CRM + EMR + RIS + PACS as SaaS — productized for NURA Imaging and external imaging/clinical practices. Anchor customer: NURA Imaging (North Miami hub)."}).encode(),
                                 headers=hdr, method="POST")
    with urllib.request.urlopen(req, timeout=10) as r:
        d = json.loads(r.read())
        cid = d.get("id")
        print("DIVISION ->", r.status, cid, d.get("name", "?"))
except urllib.error.HTTPError as e:
    print("DIVISION ERR", e.code, e.read().decode()[:200]); raise SystemExit

def mk_agent(name, role, title, reports_to=None):
    ag = {"name": name, "role": role, "title": title,
          "adapter": "hermes_gateway", "adapterConfig": {"apiBaseUrl": "http://127.0.0.1:8642/v1"}}
    if reports_to: ag["reportsTo"] = reports_to
    try:
        req = urllib.request.Request(base + f"/api/companies/{cid}/agents", data=json.dumps(ag).encode(),
                                     headers=hdr, method="POST")
        with urllib.request.urlopen(req, timeout=10) as r:
            d = json.loads(r.read())
            print("AGENT ->", r.status, d.get("id"), d.get("name"))
            return d.get("id")
    except urllib.error.HTTPError as e:
        print("AGENT ERR", name, e.code, e.read().decode()[:120]); return None

ceo = mk_agent("SaaS Division CEO", "general", "SaaS Division CEO — CRM/EMR/RIS/PACS product line")
mk_agent("SaaS CRM Lead", "general", "NURA CRM SaaS lead (healthcare/med-spa CRM)", ceo)
mk_agent("SaaS EMR Lead", "general", "NURA EMR SaaS lead (clinical records)", ceo)
mk_agent("SaaS RIS Lead", "general", "NURA RIS SaaS lead (scheduling/orders/workflow)", ceo)
mk_agent("SaaS PACS Lead", "general", "NURA PACS SaaS lead (Orthanc/OHIF platform)", ceo)

issue = {
    "title": "DIV-1: SaaS Division charter — CRM + EMR + RIS + PACS product line",
    "description": ("SaaS division created 2026-08-02 (founder directive). Product line: NURA CRM (healthcare CRM), "
                    "NURA EMR (clinical records), NURA RIS (radiology workflow), NURA PACS (Orthanc/OHIF imaging). "
                    "ANCHOR CUSTOMER: NURA Imaging (North Miami hub, 3,200 sq ft, Phase 1: X-ray/CT/MRI/US/Mammo-MQSA/DEXA) "
                    "— docs/projects/NURA-IMAGING-MASTER-PLAN.md.\n"
                    "CEO TASKS: 1) product charter + module map (multi-tenant SaaS, per-tenant isolation, role-based "
                    "access, audit); 2) pricing/finance model (Midas); 3) compliance: HIPAA + ACR/MQSA readiness for "
                    "imaging SaaS (Vigil); 4) integration contracts: eMedical EMR, Supabase, Zapier, GHL, multilingual "
                    "agents (EN/ES/Creole); 5) roadmap: Phase 1 = NURA Imaging internal rollout; Phase 2 = external "
                    "practices. All agents wired to Hermes gateway; Hermes holds the master plan + product-lineup "
                    "branding (nura-product-lineup skill)."),
    "assigneeAgentId": ceo, "priority": "high", "status": "todo",
}
try:
    req = urllib.request.Request(base + f"/api/companies/{cid}/issues", data=json.dumps(issue).encode(),
                                 headers=hdr, method="POST")
    with urllib.request.urlopen(req, timeout=10) as r:
        d = json.loads(r.read())
        print("DIV-1 ->", r.status, d.get("id", d.get("issueId", "?")))
except urllib.error.HTTPError as e:
    print("ISSUE ERR", e.code, e.read().decode()[:150])
