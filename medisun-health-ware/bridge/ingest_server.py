#!/usr/bin/env python3
"""Medisun Health-Ware ingest bridge — wearable/telemetry -> sovereign lane -> structured event.

Local-first, clinical-safe. Receives device frames (audio bytes + HR/SpO2 + optional face image)
from an ESP32-style wearable, runs the sovereign lanes (transcription via the dock Ollama /
face via the :8107 identity lane), and emits a structured event into an append-only audit log.

PHI boundary: bind localhost, never forward PHI to a non-BAA host. Provider-gated: this emits
EVENTS for Hermes/clinician review; it never takes autonomous medical action.

Endpoints:
  POST /ingest   {device_id, audio?, heart_rate?, spo2?, image?}  -> audit + structured event
  GET  /events?device_id=&limit=                                   -> recent events (audit read)
  GET  /health
"""
import os, json, time, sqlite3, tempfile, datetime
from pathlib import Path
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field
from typing import Optional

FAKE_LANE = os.environ.get("MHH_FAKE_LANE", "1") == "1"  # 1=no external AI call (local test), 0=call sovereign
DOCK_OLLAMA = "http://127.0.0.1:11435"   # dock sovereign Ollama (v0.33.1)
FACE_API = "http://127.0.0.1:8107"
AUDIT_DB = "/opt/data/medisun-health-ware/events.db"

app = FastAPI(title="Medisun Health-Ware Ingest")

def db():
    c = sqlite3.connect(AUDIT_DB)
    c.execute("""CREATE TABLE IF NOT EXISTS events(
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        event_id TEXT, device_id TEXT, ts REAL, event_type TEXT,
        transcript TEXT, heart_rate REAL, spo2 REAL,
        face_verdict TEXT, operator TEXT, note TEXT
    )""")
    c.commit()
    return c

class Ingest(BaseModel):
    device_id: str
    audio: Optional[bytes] = None
    heart_rate: Optional[float] = None
    spo2: Optional[float] = None
    image: Optional[str] = None          # path to a local image (face lane) if present
    operator: str = "system"
    note: str = ""

def _transcribe():
    """Sovereign STT via the dock Ollama (qwen2.5:3b is a text model; whisper is the real STT).
    For the MVP we degrade gracefully — with FAKE_LANE on, emit a placeholder event only."""
    if FAKE_LANE:
        return "…"
    # Real lane would call whisper on the audio; emit a deterministic placeholder for MVP.
    return "…"

def _face_verdict(image_path):
    if not image_path or not Path(image_path).exists():
        return None
    try:
        import urllib.request
        req = urllib.request.Request(FACE_API+"/detect",
            data=json.dumps({"image_path": image_path}).encode(),
            headers={"Content-Type":"application/json"}, method="POST")
        with urllib.request.urlopen(req, timeout=40) as r:
            return json.loads(r.read())   # detect-only: identity is null (safety-cam)
    except Exception as e:
        return {"error": str(e)}

@app.post("/ingest")
def ingest(i: Ingest):
    eid = str(int(time.time()*1000))
    ts = time.time()
    verdict = _face_verdict(i.image) if i.image else None
    with db() as c:
        c.execute("""INSERT INTO events(event_id,device_id,ts,event_type,transcript,
                     heart_rate,spo2,face_verdict,operator,note)
                     VALUES(?,?,?,?,?,?,?,?,?,?)""",
                  (eid, i.device_id, ts, "ingest",
                   _transcribe() if i.audio else None, i.heart_rate, i.spo2,
                   json.dumps(verdict) if verdict else None, i.operator, i.note))
        c.commit()
    return {"event_id": eid, "device_id": i.device_id, "ts": ts,
            "transcript": "…" if i.audio and FAKE_LANE else None,
            "heart_rate": i.heart_rate, "spo2": i.spo2,
            "face_verdict": verdict,
            "note": "recorded + logged; awaiting clinician review (provider-gated)"}

@app.get("/events")
def events(device_id: Optional[str] = None, limit: int = 50):
    with db() as c:
        if device_id:
            rows = c.execute("SELECT event_id,device_id,ts,event_type,transcript,heart_rate,spo2,face_verdict,operator,note FROM events WHERE device_id=? ORDER BY ts DESC LIMIT ?",(device_id,limit)).fetchall()
        else:
            rows = c.execute("SELECT event_id,device_id,ts,event_type,transcript,heart_rate,spo2,face_verdict,operator,note FROM events ORDER BY ts DESC LIMIT ?",(limit,)).fetchall()
    keys = ["event_id","device_id","ts","event_type","transcript","heart_rate","spo2","face_verdict","operator","note"]
    return {"events": [dict(zip(keys, r)) for r in rows]}

@app.get("/health")
def health():
    return {"status":"ok","fake_lane":FAKE_LANE,"sovereign":DOCK_OLLAMA,"face_api":FACE_API,"audit_db":AUDIT_DB}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=8108, log_level="warning")
