import json, urllib.request

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
hdr = {"User-Agent": "NURA-Hermes/1.0", "Content-Type": "application/json",
       "x-api-key": key or "", "Authorization": "Bearer " + (key or "")}

for label, iid in [("NUR-42", "2744d901-a61d-4034-85b0-2ad6cdd7cbd1"),
                   ("NUR-62", "2a7f2abf-8c11-43e8-89d9-45fd6cc06612")]:
    try:
        req = urllib.request.Request(f"http://127.0.0.1:3101/api/issues/{iid}/comments", headers=hdr)
        with urllib.request.urlopen(req, timeout=8) as r:
            d = json.loads(r.read())
        items = d if isinstance(d, list) else d.get("comments", d.get("items", []))
        print(f"{label}: {len(items)} comments")
        for c in items[-2:]:
            print("  -", str(c.get("content", c.get("body", "?")))[:200])
    except Exception as e:
        print(f"{label}: {str(e)[:100]}")
