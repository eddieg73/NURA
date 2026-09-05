#!/usr/bin/env python3
"""Stand up the clinical pre-training corpus inventory — what we ACTUALLY have (honest).
Validates real DICOM via pydicom, catalogs modalities, flags the gap for pre-training."""
import os, json, glob, pydicom

CORPUS = "/opt/data/imaging-corpus"
out = {"real_dicom": 0, "png_jpg": 0, "modalities": {}}

# Real DICOM (SIIM CT)
dcm = glob.glob(os.path.join(CORPUS, "**", "*.dcm"), recursive=True)
for f in dcm[:400]:
    try:
        ds = pydicom.dcmread(f, stop_before_pixels=True)
        m = getattr(ds, "Modality", "?")
        out["modalities"][m] = out["modalities"].get(m, 0) + 1
        out["real_dicom"] += 1
    except Exception:
        pass

# PNG/JPG (public Kaggle conversions)
out["png_jpg"] = len(glob.glob(os.path.join(CORPUS, "**", "*.png"), recursive=True)) + \
                 len(glob.glob(os.path.join(CORPUS, "**", "*.jpg"), recursive=True))

print(json.dumps({"sampled_real_dicom_validated": out["real_dicom"],
                  "modalities_sampled": out["modalities"],
                  "png_jpg_public_datasets": out["png_jpg"],
                  "b2_native_dicom": 12089,
                  "note": "Only ~100 local + 12,089 B2 files are native DICOM. The 81K PNG/JPG are PUBLIC Kaggle datasets (brain-MRI, mammogram, chest-Xray, COVID, histopath) — convert to cme/pixels; public data is already published, NOT proprietary.", }, indent=2))

# Write the inventory to the vault/docs for the pipeline
INV = {
  "generated": "2026-09-05",
  "native_dicom": {"local_siim_ct": out["real_dicom"], "b2": 12089},
  "public_kaggle_png_jpg": out["png_jpg"],
  "modalities_sampled": out["modalities"],
  "pipeline": "pydicom (validated) -> pathml (tissue) -> imaging-data-commons (public acquisitions) -> label/enrich -> B2 nura-datasets/clinical-pretrain",
  "honest_caveat": "Pre-training a medical foundation model needs (a) curated native DICOM at scale, (b) a GPU train lane (DGX Spark gated), (c) PHI-consent/de-id. We have validation tooling + storage now; the training corpus is mostly PUBLIC data today, not proprietary patient imaging.",
}
os.makedirs("/opt/data/clinical-pretrain", exist_ok=True)
with open("/opt/data/clinical-pretrain/corpus-inventory.json", "w") as f:
    json.dump(INV, f, indent=2)
print("wrote /opt/data/clinical-pretrain/corpus-inventory.json")
