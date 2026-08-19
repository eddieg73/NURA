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
    "body": ("FOUNDER SEQUENCING (2026-08-02): NURA PROVIDES the RIS/PACS (bundle SaaS, SaaS division DIV-1). "
             "NORTH MIAMI (NURA Imaging hub, 13886 W Dixie Hwy) is the FIRST CUSTOMER SITE — the deployment IS "
             "product delivery. Sequence: 1) Docker access decision, 2) North Miami stack bring-up on 1441409 "
             "(Orthanc + ThaiRIS + OHIF + OpenEMR — the delivered bundle), 3) modality AE-title registration + "
             "MWL, 4) go-live as the reference case. Little Haiti and Ft. Lauderdale follow as customers 2-3. "
             "Reference: docs/manuals/MEDISUN-RIS-PACS-SETUP.md + docs/projects/NURA-IMAGING-MASTER-PLAN.md.")
}
try:
    req = urllib.request.Request(f"http://127.0.0.1:3101/api/issues/0504d207-ee22-49c8-bae5-d219512becab/comments",
                                 data=json.dumps(comment).encode(), headers=hdr, method="POST")
    with urllib.request.urlopen(req, timeout=10) as r:
        print("COMMENT ->", r.status)
except urllib.error.HTTPError as e:
    print("ERR", e.code, e.read().decode()[:150])
