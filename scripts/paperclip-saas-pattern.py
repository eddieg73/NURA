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

comment = {
    "body": ("FOUNDER ROUTING PATTERN ATTACHED (2026-08-02) — banked in skill hermes-saas-productization "
             "references/gateway-routing.md: payload contract {tenant_id, session_id, action, payload} · "
             "FastAPI /v1/agent/execute (X-Tenant-ID + X-API-Key, httpx->n8n, 502 on unreachable) · n8n "
             "3-node workflow (Webhook w/ Header Auth + Respond-to-Webhook -> HTTP Request to Hermes with "
             "X-Profile: tenant_id -> Respond) · Hermes loads tenant profile per X-Profile.\n"
             "PROD RULES (adopt): HMAC-SHA256 signing FastAPI<->n8n (anti internal spoofing); async webhook "
             "responses for >30s tasks; tenant_id -> ISOLATED Docker volumes (memory/sessions/skills never "
             "leak); per-tenant API keys + Celery rate limits.\n"
             "Interactive widget spec noted -> mapped to static architecture-diagram renders for now; "
             "interactive stage-selector = app backlog."),
}
try:
    req = urllib.request.Request("http://127.0.0.1:3101/api/issues/2de602a7-4f8a-415c-b211-2b7dbf78bf8f/comments",
                                 data=json.dumps(comment).encode(), headers=hdr, method="POST")
    with urllib.request.urlopen(req, timeout=10) as r:
        print("NUR-106 COMMENT ->", r.status)
except urllib.error.HTTPError as e:
    print("ERR", e.code, e.read().decode()[:150])
