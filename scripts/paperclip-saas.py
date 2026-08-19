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
CTO = "c454a3cb-3516-4046-b60f-03e0b1bea002"

issue = {
    "title": "NUR-106: SaaS packaging — multi-tenant Hermes (profiles + FastAPI + n8n + Celery/Redis + Docker isolation)",
    "description": ("Founder 2026-08-02 blueprint (skill hermes-saas-productization + memory doctrine): "
                    "productize the NURA stack as multi-tenant SaaS.\n"
                    "CTO SEQUENCE:\n"
                    "1) MULTI-TENANCY: Hermes Profiles per tenant (config/memory/keys/skills isolated) — "
                    "scaffold a tenant template profile + onboarding checklist.\n"
                    "2) API LAYER: FastAPI gateway in front of Hermes (auth + billing + per-tenant routing); "
                    "n8n catches webhooks -> tenant CRM routes; Celery + Redis task queue so one tenant's "
                    "heavy job never bottlenecks the node.\n"
                    "3) EXECUTION ISOLATION (mandatory): tenant agents run in Docker backend (hardened "
                    "containers, dropped caps, PID limits, read-only root) — intelligence on host, "
                    "execution sandboxed; no host-level code execution for tenants.\n"
                    "4) HERMES CLOUD: managed alternative noted (Nous Research SaaS, hourly) — decision "
                    "rule: self-host for data perimeter; cloud only if ops load exceeds fleet.\n"
                    "5) Evidence: tenant #1 smoke test through FastAPI -> n8n -> tenant CRM on this issue."),
    "assigneeAgentId": CTO, "priority": "high", "status": "todo",
}
try:
    req = urllib.request.Request(base + f"/api/companies/{CID}/issues", data=json.dumps(issue).encode(),
                                 headers=hdr, method="POST")
    with urllib.request.urlopen(req, timeout=10) as r:
        d = json.loads(r.read())
        print("NUR-106 ->", r.status, d.get("id", d.get("issueId", "?")))
except urllib.error.HTTPError as e:
    print("ERR", e.code, e.read().decode()[:200])
