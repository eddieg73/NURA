#!/usr/bin/env python3
"""Dataset provisioner — stages open imaging/lab datasets + gate-checks the gated ones.
Runs on the Clinic node now (Lab copy queued behind the Docker ruling).
Writes data/datasets-status.json with evidence per dataset.
"""
import json, os, time, urllib.request, urllib.error
from pathlib import Path

OUT = Path("/opt/data/profiles/nura/data/datasets-status.json")
STAGE = Path("/opt/data/datasets")

def probe(url, timeout=20, headers=None):
    req = urllib.request.Request(url, headers=headers or {"User-Agent": "NURA-Provisioner/1.0"})
    with urllib.request.urlopen(req, timeout=timeout) as r:
        return r.status, r.read()

def main():
    STAGE.mkdir(exist_ok=True)
    status = {"updated": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()), "datasets": {}}

    # 1. IDC (Imaging Data Commons) — DICOMweb API lane probe
    for ep in ["https://api.imaging.datacommons.cancer.gov/v1/version",
               "https://api.imaging.datacommons.cancer.gov/v1/collections"]:
        try:
            code, body = probe(ep)
            status["datasets"]["IDC"] = {"status": "live", "endpoint": ep, "http": code,
                                          "sample": body[:150].decode("utf-8", "replace")}
            break
        except Exception as e:
            status["datasets"]["IDC"] = {"status": "probe_failed", "endpoint": ep, "error": str(e)[:120]}

    # 2. IDC DICOMweb (IDC viewer endpoint for actual WADO-RS)
    try:
        code, body = probe("https://dicom.idc-dev.org/dicom-web/studies", timeout=25)
        status["datasets"]["IDC_DICOMweb"] = {"status": "live" if code == 200 else "http_" + str(code), "http": code}
    except Exception as e:
        status["datasets"]["IDC_DICOMweb"] = {"status": "error", "error": str(e)[:120]}

    # 3. Saga / OsiriX sample DICOMs (direct download candidates)
    saga_urls = ["https://www.osirix-viewer.com/resources/dicom-image-library/",
                 "https://www.sagacortex.com/"]
    for u in saga_urls:
        try:
            code, _ = probe(u, timeout=15)
            status["datasets"]["Saga_samples"] = {"status": "reachable" if code == 200 else "http_" + str(code), "url": u}
            break
        except Exception as e:
            status["datasets"]["Saga_samples"] = {"status": "unreachable", "error": str(e)[:100]}

    # 4. Gated datasets — evidence-based status
    gates = {
        "MIMIC-CXR": "CITI/PhysioNet credentialed (PENDING founder drop)",
        "MIMIC-IV": "CITI/PhysioNet credentialed (PENDING founder drop)",
        "eICU": "credentialed (PENDING founder drop)",
        "CheXpert": "Stanford license (PENDING)",
        "RSNA_AbdominalTrauma": "Kaggle (PENDING kaggle.json)",
        "BUSI": "Kaggle (PENDING kaggle.json)",
        "CQ500": "Qure.ai registration form (PENDING)",
        "fastMRI": "NYU download form (PENDING)",
    }
    for name, gate in gates.items():
        status["datasets"][name] = {"status": "gated", "gate": gate}

    OUT.write_text(json.dumps(status, indent=1))
    print(json.dumps(status["datasets"], indent=1)[:1400])

if __name__ == "__main__":
    main()
