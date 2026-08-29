# Medisun Health-Ware — Technical SPEC

## 1. System context
Medisun Integrated Health MSO. The founder/medical director wants a sovereign clinical edge:
wearable capture + identity/safety-cam, engineered in-house (the "Ivy League students" pattern:
thin ESP32 + open ML + MCP), but clinical-grade.

## 2. Architecture

### 2.1 Layers
- **Device** (ESP32-S3): INMP441 mic (I2S), MAX30102 (HR/SpO2), optional camera (glass/cam gated).
  Captures locally; streams audio/telemetry over WiFi/BLE. Never does the heavy AI.
- **Bridge** (`ingest_server.py`, dock, port 8108): receives device frames, calls the sovereign
  lanes (whisper STT, local LLM, face lane), emits structured events. FastAPI.
- **Face/Identity** (`:8107`, already built): InsightFace buffalo_l, consent-gated enroll +
  verify + safety-cam detect (`identity: null`).
- **Sovereign AI** (dock Ollama `:11435`, qwen2.5:3b): local STT/LLM. Free, offline.
- **Memory** (Qdrant `:6333` + four-node clock): capture summaries + facts, retrieval.
- **Clinical** (FHIR Observation → OpenEMR via the sidecar doctrine, API only).
- **Audit** (append-only log): every capture/enroll/verify/override: operator, when, why, result.

### 2.2 Data flow
1. Device captures → bridge `/ingest` (audio bytes + HR/SpO2 + device_id + timestamp)
2. Bridge: audio → whisper STT (sovereign) → text; vitals → normalized metric
3. Bridge: face image (if present) → face lane `/verify` or `/detect`
4. Bridge emits `{event_type, device_id, ts, transcript?, vitals?, face_verdict?}` → audit + Hermes MCP
5. Hermes/NURA: summarizes, stores memory (vault/Qdrant), writes FHIR Observation (provider-gated)

### 2.3 The clinical semantics (the part they never built)
- **Provider gate**: no autonomous action. Bridge emits events; Hermes drafts; clinician approves.
- **PHI boundary**: bridge is on the clinical host; never send PHI to a non-BAA host.
- **Audit**: every override/verify logged with operator + reason.

## 3. Build order
- **P1 Software spine** — ingest bridge + clinic identity flow (THIS repo). Proves the data path.
- **P2 Wearable** — ESP32-S3 firmware (MicroPython/ESP-IDF), pins per NextBand (`MAX30102` SDA/SCL,
  `INMP441` I2S WS/BCK/DIN, ESP32-S3 N16R8).
- **P3 Clinical wire** — bridge → FHIR Observation → OpenEMR (API only, sidecar doctrine).
- **P4 Safety-cam/glasses** — capture pane, gated.

## 4. Endpoints (bridge, port 8108)
- `POST /ingest` — `{device_id, audio?, heart_rate?, spo2?, image?}`
- `GET /health`
- `GET /events?device_id=&limit=` — recent events (audit read)

## 5. Security
- Localhost bind (127.0.0.1) unless a specific reason to expose.
- No PHI to external lanes. Sealed creds (.env 0600). Key-free sovereign lanes.
- The face lane's `/detect` never returns identity (safety-cam).
- Every `/ingest` logs an audit row (who/what/why).

## 6. Verification gate
Never claim a device/capture/integration works without a real probe: a `/ingest` POST returns a
structured event; the audit log has the row; the face lane returns a verdict. The model proposes,
the probe disposes.
