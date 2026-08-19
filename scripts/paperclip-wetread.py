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
CTO = "c454a3cb-3516-4046-b60f-03e0b1bea002"

issue = {
    "title": "NUR-100: Orthanc DICOMweb + ThaiRIS bilingual + Wet-Read pipeline (plan banked, gateway built)",
    "description": ("Founder 2026-08-02 architectural plan archived: /opt/data/Obsidian Vault/NURA-OS/"
                    "Orthanc-ThaiRIS-WetRead-Plan.md. BUILT NOW: scripts/wet-read-gateway.py (HTTP POST "
                    "/v1/wet-read -> DICOM fetch -> pydicom windowing -> vision cascade -> impression + STAT "
                    "flags + requires_provider_review; DRY-RUN VERIFIED 200). Orthanc DICOMweb config already "
                    "present in imaging-stack/modules/orthanc/orthanc.json (add HttpWebhooks n8n + "
                    "OnStoredInstance hook per plan on deploy).\n"
                    "CTO SEQUENCE:\n"
                    "1) ORTHANC: on deploy (NUR-68): DICOMweb WADO-RS + n8n webhook + OnStoredInstance hook "
                    "-> wet-read gateway (DX/CR/CT/MR/US).\n"
                    "2) THAIRIS (NUR-75): bilingual TH/EN demographic + indication fields; UTF-8/ISO-2022-JP "
                    "tag encoding for Thai rendering.\n"
                    "3) WET-READ: gateway live on deploy; impression JSON -> Agent feed -> clinician review "
                    "gate (draft-only; never final read).\n"
                    "4) DATASETS (gates): MIMIC-CXR + MIMIC-IV = CITI/PhysioNet credentialed (founder drop); "
                    "CheXpert = license; RSNA = kaggle.json; IDC = OPEN -> deploy to Lab 1030183 now; eICU "
                    "credentialed; training on Lab (Swin/ViT + BiomedCLIP; Thai EN<->TH corpus).\n"
                    "5) Evidence: gateway dry-run output + Orthanc config diff on this issue."),
    "assigneeAgentId": CTO, "priority": "high", "status": "todo",
}
try:
    req = urllib.request.Request(base + f"/api/companies/{CID}/issues", data=json.dumps(issue).encode(),
                                 headers=hdr, method="POST")
    with urllib.request.urlopen(req, timeout=10) as r:
        d = json.loads(r.read())
        print("NUR-100 ->", r.status, d.get("id", d.get("issueId", "?")))
except urllib.error.HTTPError as e:
    print("ERR", e.code, e.read().decode()[:200])
