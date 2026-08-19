import json, re, time, urllib.request
from pathlib import Path

def fetch(url, timeout=120):
    req = urllib.request.Request(url, headers={"User-Agent": "NURA-Provisioner/1.0"})
    with urllib.request.urlopen(req, timeout=timeout) as r:
        return r.read()

body = fetch("https://storage.googleapis.com/idc-open-data/?max-keys=100", timeout=30).decode("utf-8", "replace")
keys = re.findall(r"<Key>([^<]+)</Key>", body)
sample = keys[0]
data = fetch("https://storage.googleapis.com/idc-open-data/" + sample, timeout=180)
ok = data[128:132] == b"DICM"
Path("/opt/data/datasets/idc-sample.dcm").write_bytes(data)
print("key:", sample[:90])
print("bytes:", len(data), "| DICOM magic:", ok)
print("saved: /opt/data/datasets/idc-sample.dcm")

# update status json
st = Path("/opt/data/profiles/nura/data/datasets-status.json")
status = json.loads(st.read_text()) if st.exists() else {"datasets": {}}
status["updated"] = time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())
status["datasets"]["IDC"] = {"status": "LIVE", "lane": "GCS bucket idc-open-data (S3 XML listing)", "sample_downloaded": sample.split("/")[-1], "bytes": len(data), "dicom_magic_verified": bool(ok)}
st.write_text(json.dumps(status, indent=1))
print("status updated")
