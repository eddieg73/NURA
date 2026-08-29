# Medisun Health-Ware — sovereign clinical edge for Medisun Integrated Health

> Built for Medisun Integrated Health (the founder's MA MSO). The "engineering it ourselves"
> answer to the student/hackathon open-source wearables (Aegis, Friend/OMI, NextBand) — but
> clinical-grade: PHI-safe, provider-gated, FHIR/HL7 interoperable, audited.

**License: internal proprietary (NURA) — NOT for public release. Per IP doctrine: public
releases use NURA names; OSS we build on stays internal-only.**

---

## 1. What this is (and what it is NOT)

**IS:** a sovereign, local-first clinical edge for Medisun — voice capture + vitals telemetry
from a wearable, facial identity verify, and a safety-cam — all captured locally, pushed
through NURA's sovereign lanes, and stored/clinical-safe. Doctor/clinician-gated.

**IS NOT:** a consumer gadget. No autonomous medical action. No PimEyes-style stranger-ID.
No PHI to a non-BAA host. The students built a weekend prototype; we build the clinical layer.

## 2. The doctrine (the line — this is non-negotiable, medical director-signed)

1. **Consent-gated identity** — `/enroll` on the face lane REQUIRES consent. Verify consented
   people only (patients, staff, enrolled medics).
2. **Emergency-necessity override** — a medic identifying an unresponsive/altered/dementia/
   child patient, or matching an official missing/SAR/alert list, is IMPLIED CONSENT (legal,
   in the patient's interest). SAFETY-CAM mode runs detection + safety flags, NEVER identity.
3. **Never stranger-surveillance** — no crownd/non-participant watchlists, no "who are these
   strangers" reverse-search. That is tracking, not triage.
4. **Provider-gated** — every output is decision-support; a licensed clinician approves.
   No autonomous diagnosis/prescribing/order.
5. **PHI boundary** — capture stays on the BAA/clinical side; B2=binary, Postgres=state,
   Hermes=events (refs, never PHI), Redis=transient. Hostinger=non-PHI/synthetic only.
6. **Audit** — every enrollment, override, and verify is logged (who, when, why, result).

## 3. The reference architecture (the students' pattern, made NURA)

### Hardware options (per the open prototypes we vetted)
| Option | HW | Cost | Sensors | Notes |
|---|---|---|---|---|
| **Medisun Band (recommended)** | ESP32-S3 N16R8 | ~$15 | INMP441 mic + MAX30102 (HR/SpO2) | The `NextBand`/`Aegis` pattern |
| **Medisun Pendant** | ESP32-C3 | ~$10 | INMP441 mic | The `Friend`/OMI pattern |
| **Glass / safety-cam (gated)** | Meta Ray-Ban or OpenGlass | <$400 | camera | capture-to-verify only, gated |

### The pipeline (local capture → sovereign brain → clinical-safe store)
```
[Wearable: mic + HR/SpO2]  --BLE/WiFi-->  [Bridge server (dock)]  --MCP-->  [Hermes/NURA]
        |                                             |                         |
        |                                             v                         v
        +--- local capture (never leaves the device)   [sovereign lane]    [FHIR Observation
                                                         whisper + local        -> OpenEMR]
                                                         STT/LLM (dock Ollama)
```
- Heavy processing (STT/LLM/face) stays on the dock (sovereign lanes) — the device is a thin sensor.
- The `cortex`-style double-backend: heavy local (Rust/Python), cloud optional/never for PHI.
- Every capture → MCP tool → Hermes → vault/Qdrant (memory) + FHIR (clinical) + audit log.

## 4. Repository layout (this repo)
```
medisun-health-ware/
├── README.md               <- you are here (the master spec)
├── SPEC.md                 <- the technical reference architecture + build order
├── bridge/
│   └── ingest_server.py    <- the wearable/telemetry ingest bridge (FastAPI + sovereign lanes)
├── identity/
│   └── clinical_verify.sh  <- clinic identity/safety-cam flow (enroll + verify)
├── firmware/
│   └── MICROPYTHON.md      <- example ESP32 MicroPython skeleton (follows NextBand pins)
└── docs/
    └── SAFETY-POLICY.md    <- the safety-cam recording notice + retention + no-ID rule
```

## 5. Build order (the staged roadmap — "all of it")
- **Phase 1 (this deliverable): the software spine** — ingest bridge + clinic identity flow + spec. Get the data path working end to end.
- **Phase 2: the wearable** — ESP32-S3 + mic + MAX30102, MicroPython/ESP-IDF firmware per `firmware/MICROPYTHON.md`, BLE/WiFi → bridge.
- **Phase 3: clinical wire-up** — bridge → FHIR Observation → OpenEMR; provider approval gate; audit log.
- **Phase 4: safety-cam + glasses** — the capture-to-verify pane, gated (camera = consequential, founder-approval).

## 6. Run it
```bash
# ingest bridge (dock, sovereign lanes)
python3 -m venv .venv && source .venv/bin/activate
pip install fastapi uvicorn audioop-lts
uvicorn bridge.ingest_server:app --host 127.0.0.1 --port 8108

# clinic identity flow (uses the face lane already on :8107)
./identity/clinical_verify.sh enroll --person pat-1001 --name "Patient A" --group medisun
./identity/clinical_verify.sh verify --image /path/to/photo.jpg --group medisun
./identity/clinical_verify.sh safety --image /path/to/scene.jpg   # detect-only, no identity
```

## 7. The honest boundary (medical director sign-off required)
Capture is a **camera/mic in a clinical field**. A written **safety-cam policy** (recording
notice where practical, 30-day retention, no identity lookup) must be in the Medisun SOP before
go-live. See `docs/SAFETY-POLICY.md`. The founder (medical director) sets the clinical boundary;
Hermes sets the engineering.
