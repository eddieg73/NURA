#!/usr/bin/env python3
"""NURA Medical Imaging Vision Lane — labs/imaging reports + DICOM/PNG images.
Usage:
  medical-imaging-vision.py <image.png|image.jpg|file.dcm> [prompt]
  medical-imaging-vision.py --modalities       # dataset matrix
  medical-imaging-vision.py --sample <modality>  # fetch a real reference image (Open-i/MedPix)
Routes through vision-proxy.py cascade (free-vl -> gemini). DICOM -> PNG via pydicom.
Output: structured findings JSON (normal/abnormal, confidence, findings) — NEVER a diagnosis (clinical doctrine).
"""
import json, os, subprocess, sys, sysconfig, urllib.request
from pathlib import Path

sys.path.insert(0, "/opt/data/profiles/nura/python-packages")
VP = "/opt/data/scripts/vision-proxy.py"
OUT = Path("/opt/data/profiles/nura/data/imaging-vision")
OUT.mkdir(parents=True, exist_ok=True)

PROMPT = ("You are a medical imaging assistant providing STRUCTURED DESCRIPTIONS only (never a final "
          "diagnosis). Describe: 1) imaging type/modality, 2) NORMAL or ABNORMAL findings, 3) key findings, "
          "4) confidence (0-1), 5) what a radiologist should verify. No clinical conclusions beyond what is "
          "visible. Format as JSON.")

def dcm_to_png(path):
    try:
        import pydicom, numpy as np
        from PIL import Image
        ds = pydicom.dcmread(path)
        arr = ds.pixel_array
        if arr.ndim == 3:
            arr = arr[..., 0]
        arr = arr.astype(float)
        arr = (arr - arr.min()) / (arr.max() - arr.min() + 1e-9) * 255
        png = OUT / (Path(path).stem + ".png")
        Image.fromarray(arr.astype("uint8")).save(png)
        return str(png)
    except ImportError:
        return None  # pydicom/numpy missing — labeled
    except Exception as e:
        return f"ERR {e}"

def analyze(path, prompt=PROMPT):
    if path.lower().endswith(".dcm"):
        png = dcm_to_png(path)
        if png is None:
            return {"error": "pydicom/numpy missing — install in python-packages"}
        if str(png).startswith("ERR"):
            return {"error": png}
        path = png
    r = subprocess.run(["python3", VP, path, "free-vl", prompt], capture_output=True, text=True, timeout=240)
    return {"image": path, "analysis": r.stdout.strip()[:3000], "cascade_err": r.stderr.strip()[:200]}

def modalities():
    return {
        "cxr": {"name": "Chest X-ray", "datasets": ["Open-i (public)", "CheXpert (license pending)", "MIMIC-CXR (CITI pending)"]},
        "ct": {"name": "CT", "datasets": ["DeepLesion (public)", "TCGA (public)", "IDC on Lab"]},
        "mri": {"name": "MRI", "datasets": ["BraTS (brain, public)", "TCGA", "IDC"]},
        "us": {"name": "Ultrasound", "datasets": ["Open-i (public)", "BUTD (public)"]},
        "mammo": {"name": "Mammography", "datasets": ["CBIS-DDSM (public)"]},
        "path": {"name": "Pathology", "datasets": ["TCGA (public)"]},
        "ref": {"name": "Reference/teaching", "datasets": ["MedPix (NLM, public)"]},
    }

def sample(mod):
    url = f"https://openi.nlm.nih.gov/api/search?query={mod}&it=img,imgLrg&limit=1"
    with urllib.request.urlopen(url, timeout=20) as r:
        d = json.loads(r.read())
    for it in d.get("List", []):
        u = it.get("imgLrg") or it.get("image")
        if u:
            full = ("https://openi.nlm.nih.gov" + u) if u.startswith("/") else u
            dst = OUT / f"sample-{mod}.jpg"
            urllib.request.urlretrieve(full, dst)
            return {"url": full, "saved": str(dst)}
    return {"error": "no image"}

if __name__ == "__main__":
    args = sys.argv[1:]
    if "--modalities" in args:
        print(json.dumps(modalities(), indent=1)); sys.exit(0)
    if "--sample" in args:
        i = args.index("--sample")
        print(json.dumps(sample(args[i + 1] if i + 1 < len(args) else "cxr"), indent=1)); sys.exit(0)
    if not args:
        print("usage: medical-imaging-vision.py <image|dcm> [prompt] | --modalities | --sample <mod>")
        sys.exit(1)
    print(json.dumps(analyze(args[0], args[1] if len(args) > 1 else PROMPT), indent=1))
