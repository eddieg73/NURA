import json, re, urllib.request

def fetch(url, timeout=60):
    req = urllib.request.Request(url, headers={"User-Agent": "NURA-Provisioner/1.0"})
    with urllib.request.urlopen(req, timeout=timeout) as r:
        return r.read()

body = fetch("https://storage.googleapis.com/idc-open-data/?max-keys=50&prefix=dicom/", timeout=30).decode("utf-8", "replace")
keys = re.findall(r"<Key>([^<]+)</Key>", body)
print("keys listed:", len(keys))
dcm = [k for k in keys if k.lower().endswith(".dcm")]
print("dcm files:", len(dcm))
for k in dcm[:3]:
    print(" -", k[:100])
sample = dcm[0] if dcm else None
if sample:
    data = fetch("https://storage.googleapis.com/idc-open-data/" + sample, timeout=120)
    print("downloaded:", sample.split("/")[-1], "| bytes:", len(data), "| DICOM magic:", data[128:132] == b"DICM")
    open("/opt/data/datasets/idc-sample.dcm", "wb").write(data)
    print("saved: /opt/data/datasets/idc-sample.dcm")
