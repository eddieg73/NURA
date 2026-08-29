# Medic Wearable — On-Device Facial Recognition (patient-ID + first-responder safety)

**Class:** Internal BUILD SPEC (the Reg A stays capability-framed — no open-source names, per the proprietary-process doctrine). **Research:** 2026-08-27 (edge_facial_recognition.md).

## The engine (chosen)
**InsightFace** (29.6k★, code MIT; models research-only) — the full pipeline as small ONNX packs. Use the **`buffalo_sc`** pack: **16 MB, LFW 99.70** (buffalo_s-level accuracy with the_edge). It bundles **SCRFD/RetinaFace detect + ArcFace embed (512-d) + alignment**.
- Alternatives (fallback): DeepFace (prototyping, TF-heavy) · face_recognition/dlib (simple, old) · OpenFace (CMU, unmaintained) · SpherFace/CosFace + FaceNet (method originators) · **GhostFaceNets** (lightweight mobile backbone).

## The pipeline (run on the edge device)
```
FRAME → SCRFD detect (facebox) → 5-point align → ArcFace embed (512-d)
      → MiniFAS liveness gate (reject spoof) 
      → cosine vs GALLERY (named embeddings) ≥ threshold → identity / no-match
      → (b) cross-check 2nd gallery: WATCHLIST (criminal/missing-person) → threat flag
```

## The two galleries (two use-cases)
| Use-case | Gallery | When | Gate |
|---|---|---|---|
| **(a) Patient-ID** | local patient-embedding gallery (from the practice) | match a face at point-of-care → pull chart/record | **local-only; HIPAA-sensitive; consent** |
| **(b) First-responder safety** | criminal / missing-person / **watchlist** embedding gallery | before/on scene → warn the medic | shown to medic only; **law-enforcement / public-safety authorization** |

## Edge deployment
- **ONNX Runtime (CPU) or TensorRT (Jetson)** — the `buffalo_sc` pack runs in <16 MB memory; on Orin-Nano / mid phone SoC, ~15–40 ms/frame (estimates from Jetson-Nano/Xavier data; Orin-Nano improves).
- **NCNN** (BSD-3) if a pure-CPU mobile path is needed. Face detect (SCRFD) is the heavier stage; embed is light.
- Run entirely on-device (no cloud, no PHI off the device).

## Privacy / legal (non-negotiable gates)
- **BIPA / state biometric laws** — written notice + consent before enrollment/capture for *patient* recognition.
- **4th-Amendment / public-safety limits** — the watchlist/threat match is a **decision-support signal to the medic**, not arrest authority; no mass surveillance; record-all + audit; limit to public navigable-airspace/surfaces; a warrant/emergency predicate for targeted surveillance.
- **HIPAA** — patient embeddings + matches are PHI; local-only, encrypted, audited; no PHI to cloud.
- **Never an autonomous decision** — the tool alerts/assists the human; the medic (and clinical team) decides.

## Incorporate into Reg A
The Reg A's "Medics' Eyewear / Body-Cam (facial recognition, on-device)" capability section carries this — **capability-framed** (no open-source names), with the patient-ID + watchlist/first-responder-safety use-cases and the privacy/consent/bio laws + public-safety limits.

## Source
`/opt/data/edge_facial_recognition.md` (InsightFace/DeepFace/dlib/OpenFace/FaceNet/SphereFace/GhostFaceNets; pipeline; ONNX/TensorRT/NCNN; BIPA + 4th-Amendment caveats; URLs + licenses + stars).
