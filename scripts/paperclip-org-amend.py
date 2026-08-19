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
    "body": ("ORG UPDATE (founder 2026-08-02): Oussama and Amrit no longer run shop. Hermes + Atlas (CEO) "
             "run operations. AMENDMENT to the ruling request: deploy authority options are now (a) Hermes "
             "via docker lanes :8100-8102 or (b) founder host-side SSH — the Oussama route is removed. "
             "Everything else in the ruling stands; deadline remains Monday 09:00 scrum."),
}
try:
    req = urllib.request.Request("http://127.0.0.1:3101/api/issues/480ee59e-2b64-4d9c-92c9-5a8a4898d0e0/comments",
                                 data=json.dumps(comment).encode(), headers=hdr, method="POST")
    with urllib.request.urlopen(req, timeout=10) as r:
        print("NUR-110 AMEND ->", r.status)
except urllib.error.HTTPError as e:
    print("ERR", e.code, e.read().decode()[:150])
