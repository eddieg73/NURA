import re, urllib.request

def fetch(url, timeout=30):
    req = urllib.request.Request(url, headers={"User-Agent": "NURA-Provisioner/1.0"})
    with urllib.request.urlopen(req, timeout=timeout) as r:
        return r.read().decode("utf-8", "replace")

body = fetch("https://storage.googleapis.com/idc-open-data/?max-keys=100", timeout=30)
keys = re.findall(r"<Key>([^<]+)</Key>", body)
print("root keys:", len(keys))
for k in keys[:12]:
    print(" -", k[:120])
