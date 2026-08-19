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
    "body": ("FOUNDER STORAGE-ISOLATION PATTERN ATTACHED (2026-08-02) — skill hermes-saas-productization "
             "references/tenant-storage-isolation.md. IMPLEMENTATION RULES for NUR-106 step 3:\n"
             "1) Host tree /opt/hermes/tenants/<tenant_id>/{config,memory,skills} (0700).\n"
             "2) docker-py provisioning: config ro, memory rw, skills ro mounts to /app/*.\n"
             "3) HARDENING (mandatory): user 10001:10001 + chown host dirs; read_only=True root fs; "
             "cap_drop ALL; network_mode none (agent routes via gateway, not container net); mem_limit 1g; "
             "remove=True ephemeral.\n"
             "4) Filesystem boundary: ro system+skills (no backdoor injection), non-root breakout=zero "
             "host perms, root fs read-only (no /tmp binaries).\n"
             "5) MULTI-NODE: 2-5 servers = NFS v4/EFS on /opt/hermes/tenants; k8s scale = RWX PVC per "
             "tenant.\n"
             "CTO: fold into the tenant template + document image build (hermes-agent:latest per NUR-87 "
             "pattern). Evidence: one tenant container run with mounts verified on this issue."),
}
try:
    req = urllib.request.Request("http://127.0.0.1:3101/api/issues/2de602a7-4f8a-415c-b211-2b7dbf78bf8f/comments",
                                 data=json.dumps(comment).encode(), headers=hdr, method="POST")
    with urllib.request.urlopen(req, timeout=10) as r:
        print("NUR-106 COMMENT ->", r.status)
except urllib.error.HTTPError as e:
    print("ERR", e.code, e.read().decode()[:150])
