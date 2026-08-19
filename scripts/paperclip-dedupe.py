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
DUP = "8d376a16-f0de-4976-ae7a-88816143c57b"
ORIG = "fa200fb7-6520-4553-ad62-701b6c0febd5"
NUR54 = "3bcdbbcf-e499-4415-a6e1-15a3fbd6c4dc"

# 1. Try to delete the duplicate
try:
    req = urllib.request.Request(base + f"/api/agents/{DUP}", headers=hdr, method="DELETE")
    with urllib.request.urlopen(req, timeout=8) as r:
        print("DELETE DUP ->", r.status)
except urllib.error.HTTPError as e:
    print("DELETE DUP ERR", e.code, e.read().decode()[:150])
except Exception as e:
    print("DELETE DUP", str(e)[:100])

# 2. Reassign NUR-54 to the original Perfex dev
try:
    req = urllib.request.Request(base + f"/api/issues/{NUR54}",
                                 data=json.dumps({"assigneeAgentId": ORIG}).encode(),
                                 headers=hdr, method="PATCH")
    with urllib.request.urlopen(req, timeout=8) as r:
        print("REASSIGN NUR-54 ->", r.status)
except urllib.error.HTTPError as e:
    print("REASSIGN ERR", e.code, e.read().decode()[:150])
except Exception as e:
    print("REASSIGN", str(e)[:100])
