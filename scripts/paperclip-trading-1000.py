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
    "body": ("FOUNDER UPDATE 2026-08-02: trading account funded at $1,000 (raised from $10). Build accordingly: "
             "risk engine = 1% hard cap = $10 risk/trade, 1:2 RR = $20 targets; position sizing must be "
             "%based, never fixed-lot at this size (micro lots); the architecture is size-agnostic — keep it "
             "that way. Paper phase + backtest still mandatory before ANY live entry regardless of size. "
             "Also note: Hermes is probing official congressional disclosure sources for the Pelosi/")
}
comment["body"] += "officials tracker module (follows NUR-83)."
try:
    req = urllib.request.Request("http://127.0.0.1:3101/api/issues/79c870bc-8c9a-4669-8b0e-4786e33b17b4/comments",
                                 data=json.dumps(comment).encode(), headers=hdr, method="POST")
    with urllib.request.urlopen(req, timeout=10) as r:
        print("COMMENT ->", r.status)
except urllib.error.HTTPError as e:
    print("ERR", e.code, e.read().decode()[:150])
