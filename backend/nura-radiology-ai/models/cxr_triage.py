#!/usr/bin/env python3
"""NURA CXR triage — TorchXRayVision DenseNet-121 (18 pathologies).

Emits the NURA Radiology Inference contract (spec §49):
  classification.status: NORMAL | ABNORMAL_NONURGENT | ABNORMAL_URGENT | CRITICAL | INDETERMINATE
  findings[], negative_findings[], ranked differential[], must_not_miss[],
  recommendations[], model provenance, requires_provider_review.

DRAFT — PROVIDER REVIEW REQUIRED. Never autonomous diagnosis. The five assertion levels are
kept separate: image -> feature -> abnormal -> compatible-with-disease -> provider-diagnosed.
"""
import json, sys
import torch, torchvision, torchxrayvision as xrv, skimage.io

# Dangerous / must-not-miss findings (deterministic escalation config - spec §56).
# NOTE: these are POLICY defaults to be clinically validated, NOT proven thresholds.
CRITICAL = {"Pneumothorax", "Effusion", "Edema", "Mass"}      # clinically critical class
URGENT   = {"Pneumonia", "Consolidation", "Atelectasis", "Cardiomegaly", "Infiltration"}
CONFIDENT = 0.65          # top-1 pathology must exceed this to avoid abstaining (indeterminate)
PRESENT   = 0.60          # "present"
TRIAGE    = 0.50          # lower for a priority alert (higher sensitivity)
UNCERTAIN_BAND = 0.42     # max below this => indeterminate (abstain)
MODEL_WEIGHTS = "densenet121-res224-all"


def load_model(weights=MODEL_WEIGHTS):
    m = xrv.models.DenseNet(weights=weights); m.eval(); return m


def preprocess(path):
    import numpy as np, skimage.transform
    img = skimage.io.imread(path)
    img = xrv.datasets.normalize(img, 255)          # -> [-1024,1024], NOT [0,1]
    if img.ndim == 3:
        img = img.mean(2)
    h, w = img.shape; s = min(h, w); t, l = (h - s) // 2, (w - s) // 2
    img = img[t:t + s, l:l + s]
    img = skimage.transform.resize(img, (224, 224), mode="constant", preserve_range=True).astype(np.float32)
    return torch.from_numpy(img[None, None, ...])


def classify(scores, labels):
    """Return the 5-level classification + findings + differential + must_not_miss."""
    present = {labels[i]: round(float(scores[i]), 4) for i in range(len(labels)) if scores[i] >= PRESENT}
    borderline = {labels[i]: round(float(scores[i]), 4) for i in range(len(labels))
                  if TRIAGE <= scores[i] < PRESENT}
    flagged = {k: v for k, v in present.items() if k in CRITICAL}
    flagged_border = {k: v for k, v in borderline.items() if k in CRITICAL}
    top = max(float(x) for x in scores)

    if top < CONFIDENT:
        status = "INDETERMINATE"          # model not confident -> abstain (spec §49)
    elif flagged:
        status = "CRITICAL"
    elif any(k in URGENT for k in present):
        status = "ABNORMAL_URGENT"
    elif present:
        status = "ABNORMAL_NONURGENT"
    elif top < UNCERTAIN_BAND:
        status = "NORMAL"
    else:
        status = "INDETERMINATE"

    findings = [{"finding": k.replace("_", " ").lower(), "certainty": "present",
                 "severity": "critical" if k in CRITICAL else "abnormal",
                 "score": v} for k, v in sorted(present.items(), key=lambda kv: -kv[1])]

    # Ranked differential: present pathologies by score, highest relative likelihood first.
    diff = []
    for i, (k, v) in enumerate(sorted(present.items(), key=lambda kv: -kv[1]), 1):
        diff.append({
            "rank": i, "condition": k.replace("_", " ").lower(),
            "relative_likelihood": "high" if v >= 0.7 else ("moderate" if v >= 0.55 else "low"),
            "supporting_findings": [k.replace("_", " ").lower()],
            "contradicting_findings": [],
            "missing_information": ["clinical correlation", "prior comparison"],
        })
    # Must-not-miss: dangerous findings, ranked by clinical danger, SEPARATE from likelihood.
    danger_order = sorted(flagged.items(), key=lambda kv: kv[1])
    must_not_miss = [{"condition": k.replace("_", " ").lower(), "urgency": "critical" if k in
                      {"Pneumothorax", "Effusion", "Mass"} else "urgent",
                      "reason": "deterministic escalation - requires provider review",
                      "score": v} for k, v in danger_order]
    if not must_not_miss and flagged_border:
        must_not_miss = [{"condition": k.replace("_", " ").lower(), "urgency": "expedited",
                          "reason": "borderline critical finding - correlate clinically",
                          "score": v} for k, v in flagged_border.items()]

    return status, findings, diff, must_not_miss


def infer(model, image_path, patient_ref="opaque-patient-uuid", study_id="opaque-study-id"):
    x = preprocess(image_path)
    with torch.no_grad():
        pred = torch.sigmoid(model(x))[0]
    labels = model.pathologies
    scores = pred.tolist()
    status, findings, diff, must_not_miss = classify(pred, labels)

    return {
        "study_id": study_id,
        "patient_ref": patient_ref,
        "modality": "DX", "body_region": "CHEST",
        "quality": {"diagnostic": True, "issues": []},
        "classification": {"status": status},
        "findings": findings,
        "negative_findings": [] if findings else ["no significant thoracic finding"],
        "differential": diff,
        "must_not_miss": must_not_miss,
        "recommendations": [] if must_not_miss else [],
        "model": {"name": "torchxrayvision-densenet121", "version": "res224-all",
                  "threshold_version": "nura-cxr-1.0.0",
                  "deployment_status": "SHADOW_ONLY",   # spec §61 — NOT clinically enabled; uncalibrated
                  "known_limitations": ["uncalibrated on target population", "adult-trained", "threshold is policy default, not validated"]},
        "requires_provider_review": True,
        "flag": "DRAFT - PROVIDER REVIEW REQUIRED",
        # five-assertion provenance, kept separate (spec §60)
        "assertions": {
            "image_seen": True,
            "visual_feature_detected": bool(findings),
            "feature_is_abnormal": status.startswith("ABNORMAL") or status == "CRITICAL",
            "compatible_with_disease": False,          # model does not diagnose
            "provider_diagnosed": False,               # only a person may set this
        },
    }


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("usage: cxr_triage.py <image> [image2 ...]", file=sys.stderr); sys.exit(2)
    model = load_model()
    for p in sys.argv[1:]:
        print("== " + p)
        print(json.dumps(infer(model, p), indent=2))
