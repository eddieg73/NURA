#!/usr/bin/env python3
"""NURA Radiology AI Orchestrator — FastAPI.

The net-new layer between the existing Orthanc (PACS) and Mirth (interface engine).
Flow: Orthanc "stable study" webhook -> registry lookup -> model runner -> structured
finding -> DICOM-SR (to PACS) + HL7 ORU (to Mirth/RIS).

Every output is a DRAFT — provider review required. Never autonomous diagnosis.
"""
import os
import socket
import time
import uuid

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel

app = FastAPI(title="NURA Radiology AI Orchestrator", version="0.1.0")

# ---------------------------------------------------------------------------
# Model registry. In-memory default; the Postgres impl (schema.sql) swaps in
# behind the same interface so the orchestrator code doesn't change.
# ---------------------------------------------------------------------------
REGISTRY = {
    "torchxrayvision-cxr-triage": {
        "task": "triage", "modality": "XR", "anatomy": "chest",
        "checkpoint_ref": "/opt/radiology-venv (TorchXRayVision)",
        "status": "dev",
    },
    "totalsegmentator-anatomy": {
        "task": "segmentation", "modality": "CT", "anatomy": "full_body",
        "checkpoint_ref": "/opt/radiology-venv (TotalSegmentator)",
        "status": "dev",
    },
}

# Pluggable inference runners: slug -> callable(study_ctx) -> dict.
# Populated when a model is actually wired to a checkpoint. Empty = honest 501.
RUNNERS: dict = {}


class StableStudy(BaseModel):
    """Orthanc 'OnStableStudy' change callback payload (subset we use)."""
    ID: str | None = None
    StudyInstanceUID: str | None = None
    PatientID: str | None = None
    PatientName: str | None = None
    MainDicomTags: dict | None = None
    Series: list | None = None


class ModelNotWired(Exception):
    pass


def select_model(modality: str) -> str:
    """Route a study to a model by modality. First match wins; explicit registry
    routing (by anatomy/series) replaces this once models are wired."""
    if modality.upper() in ("CR", "DX", "XA", "MG"):
        return "torchxrayvision-cxr-triage"
    if modality.upper() == "CT":
        return "totalsegmentator-anatomy"
    return ""


def build_dicom_sr(study_uid: str, patient_id: str, finding_text: str) -> bytes:
    """Minimal Basic Text DICOM-SR (SOP 1.2.840.10008.5.1.4.1.1.88.11)."""
    import pydicom
    from pydicom.dataset import Dataset, FileMetaDataset
    from pydicom.uid import generate_uid, ExplicitVRLittleEndian

    file_meta = FileMetaDataset()
    file_meta.MediaStorageSOPClassUID = "1.2.840.10008.5.1.4.1.1.88.11"
    file_meta.MediaStorageSOPInstanceUID = generate_uid()
    file_meta.TransferSyntaxUID = ExplicitVRLittleEndian
    file_meta.ImplementationClassUID = "1.2.826.0.1.3680043.10.999"

    ds = Dataset()
    ds.file_meta = file_meta
    ds.SOPClassUID = "1.2.840.10008.5.1.4.1.1.88.11"
    ds.SOPInstanceUID = file_meta.MediaStorageSOPInstanceUID
    ds.StudyInstanceUID = study_uid
    ds.SeriesInstanceUID = generate_uid()
    ds.PatientID = patient_id or "UNKNOWN"
    ds.Modality = "SR"
    ds.ContentDate = time.strftime("%Y%m%d")
    ds.ContentTime = time.strftime("%H%M%S")
    ds.VerificationFlag = "UNVERIFIED"
    ds.CompletionFlag = "PARTIAL"

    # ContentSequence: TEXT finding under a CONTAINER (Basic Text SR shape)
    def concept(code, meaning, scheme="DCM", version="01"):
        c = Dataset()
        c.CodeValue = code
        c.CodingSchemeDesignator = scheme
        c.CodeMeaning = meaning
        c.CodingSchemeVersion = version
        return c

    container = Dataset()
    container.RelationshipType = "CONTAINS"
    container.ValueType = "CONTAINER"
    container.ConceptNameCodeSequence = [concept("55111-9", "Current imaging procedure descriptions", "LN")]
    container.ContinuityOfContent = "SEPARATE"

    text_item = Dataset()
    text_item.RelationshipType = "CONTAINS"
    text_item.ValueType = "TEXT"
    text_item.ConceptNameCodeSequence = [concept("121071", "Finding")]
    text_item.TextValue = finding_text

    ds.ContentSequence = [container, text_item]

    from io import BytesIO
    buf = BytesIO()
    pydicom.dcmwrite(buf, ds, write_like_original=False)
    return buf.getvalue()


def build_oru(patient_id: str, patient_name: str, finding_text: str) -> bytes:
    """Minimal HL7 ORU^R01 with one OBX text finding (for the Mirth ORU channel)."""
    ts = time.strftime("%Y%m%d%H%M%S")
    msgid = uuid.uuid4().hex[:12]
    msg = (
        f"MSH|^~\\&|NURA_AI|NURATECH|MIRTH|NURATECH|{ts}||ORU^R01|{msgid}|P|2.5\r"
        f"PID|||{patient_id or ''}||{patient_name or ''}\r"
        f"OBR|1|||RADIOLOGY^NURA AI DRAFT|||{ts}\r"
        f"OBX|1|ST|RAD^AI Finding^LN||{finding_text}||||||F\r"
    )
    # MLLP framing
    return b"\x0b" + msg.encode("utf-8") + b"\x1c\x0d"


def send_oru_mllp(host: str, port: int, payload: bytes) -> bool:
    """Send an HL7 message to Mirth over MLLP. Returns True on ACK receipt."""
    try:
        with socket.create_connection((host, port), timeout=10) as s:
            s.sendall(payload)
            ack = s.recv(4096)
            return b"MSA|AA" in ack
    except Exception as e:
        app.state.last_mllp_error = str(e)
        return False


@app.get("/health")
def health():
    return {"status": "ok", "models": list(REGISTRY), "runners": list(RUNNERS)}


@app.get("/models")
def models():
    return REGISTRY


@app.post("/webhooks/orthanc/stable-study", status_code=202)
def stable_study(payload: StableStudy):
    study_uid = payload.StudyInstanceUID or (payload.MainDicomTags or {}).get("StudyInstanceUID")
    if not study_uid:
        raise HTTPException(status_code=400, detail="missing StudyInstanceUID")

    # Determine modality from the first series' MainDicomTags (Orthanc embeds it).
    modality = ""
    series_tags = (payload.MainDicomTags or {}).get("Modality")
    if series_tags:
        modality = series_tags
    elif payload.Series:
        modality = (payload.Series[0].get("MainDicomTags") or {}).get("Modality", "")

    slug = select_model(modality)
    if not slug:
        raise HTTPException(status_code=501, detail=f"no model for modality '{modality}'")

    if slug not in RUNNERS:
        raise HTTPException(
            status_code=501,
            detail=f"model '{slug}' registered but inference not wired — "
                   f"connect checkpoint at {REGISTRY[slug]['checkpoint_ref']}",
        )

    result = RUNNERS[slug]({"study_uid": study_uid, "patient_id": payload.PatientID})
    finding_text = result.get("finding", "AI draft pending")
    draft_text = f"DRAFT — PROVIDER REVIEW REQUIRED. {finding_text}"

    sr_bytes = build_dicom_sr(study_uid, payload.PatientID or "", draft_text)
    oru_bytes = build_oru(payload.PatientID or "", payload.PatientName or "", draft_text)

    mirth_ok = send_oru_mllp(
        os.environ.get("MIRTH_MLLP_HOST", "127.0.0.1"),
        int(os.environ.get("MIRTH_MLLP_PORT", "6663")),
        oru_bytes,
    )

    return {
        "study_uid": study_uid,
        "model": slug,
        "finding": draft_text,
        "dicom_sr_bytes": len(sr_bytes),
        "oru_acked": mirth_ok,
        "status": "draft",
    }
