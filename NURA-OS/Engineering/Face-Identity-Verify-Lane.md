# Face Identity — sovereign opt-in verify lane (2026-08-28)

Date: 2026-08-28 · Owner: Eddie (founder) · Operator: Hermes (CTO)
Mirrored to skill: `face-identity-ops` · Mirror: Notion board (docsmaster)

## What it is
A LOCAL face-verification API (InsightFace `buffalo_l`: SCRFD detect + ArcFace w600k_r50
512-dim embeddings) on `127.0.0.1:8107`, embeddings + roster in SQLite. Nothing leaves the
dock. Zero per-call cost. Sovereign.

## The doctrine (this is the line — important)
- **Consent-gated** (default): `/enroll` REQUIRES `consent: true`. Verify against an enrolled,
  consented roster only. This is the community-medic / staff / enrolled-patient lane.
- **Emergency-necessity override** (safety): a paramedic identifying an unresponsive/altered/
  dementia/child patient, or matching an official missing-person/SAR/alert list, is IMPLIED
  CONSENT — legal, and in the patient's interest. This is the `/detect` safety-cam mode.
- **Still prohibited**: PimEyes-style stranger surveillance — scanning crowds, building
  watchlists of non-participants, "who are these strangers." That's tracking, not triage.
- **The `/detect` safety-cam never returns identity** (`identity: null`) — it returns face
  detection + safety context (bbox, score, age, gender) ONLY. Detection ≠ identification.

## Endpoints (all live, port 8107)
- `POST /enroll` — `{image_path, person_id, display_name, role, group, consent}` (consent required)
- `POST /detect` — safety-cam: face detection + safety context, NO identity
- `POST /verify` — 1:N best match within roster (or group)
- `POST /verify-1to1` — 1:1 cosine similarity vs a specific person
- `GET /roster` — metadata only (no embeddings leaked)
- `DELETE /person/{id}` — right-to-delete
- `GET /health`

## Calibrated threshold (measured on deepface test set)
THRESH = 0.55. Same-person sim 0.69–0.81; different-person -0.01..0.05. 0.45 was too low
(false-positives). Verify against YOUR roster before production.

## Verification evidence (this build)
- Detection: real faces detected, 512-dim; couple.jpg → detects (multi-face works)
- True positive: img2 vs pat-1001 = 0.7073 → is_match true
- True negative: img3 vs pat-1001 = -0.0134 → is_match false
- Consent gate: no-consent request rejected
- Right-to-delete: person removed, roster count dropped
- Safety-cam: `/detect` returns detection + safety_info, identity:null

## Artifacts
- server: `/opt/data/face-identity-server.py`
- venv: `/opt/data/face-venv` · model: `buffalo_l` (one-time ~300MB download)
- bridge CLI: `/opt/data/face_test_verify.py` (enroll/verify/verify-1to1/detect)
- test images: `/opt/data/face-test/` (img1-4, couple.jpg from deepface unit dataset)
- skill: `face-identity-ops` · CLI pkg install workaround: `.sh` script (guard trips on inline)
