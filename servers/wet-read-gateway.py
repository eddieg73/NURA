#!/usr/bin/env python3
"""Wet-Read Gateway — HTTP POST /v1/wet-read for the vision LLM pipeline.
Receives {instance_id, modality, dicom_web_uri, patient_id} → fetches DICOM (dry-run mode when
Orthanc not live) → converts via pydicom → vision cascade → structured impression with STAT flags.
Draft-only output; clinician review gate mandatory (never a final read).
Usage: python3 wet-read-gateway.py [--port 8000] [--dry-run]
"""
import base64, json, os, sys, urllib.request
from http.server import BaseHTTPRequestHandler, HTTPServer

VP = "/opt/data/profiles/nura/scripts/vision-proxy.py"
sys.path.insert(0, "/opt/data/profiles/nura/python-packages")
DRY = "--dry-run" in sys.argv
PORT = 8000
if "--port" in sys.argv:
    PORT = int(sys.argv[sys.argv.index("--port") + 1])

IMPRESSION_PROMPT = ("You are a radiology wet-read triage assistant. Describe: modality, NORMAL/ABNORMAL, "
                     "key findings (e.g., pneumothorax, intracranial hemorrhage, fracture), confidence 0-1, "
                     "STAT flag (true if emergent), what a radiologist must verify. JSON only. Never final.")

def dcm_to_png_bytes(path):
    import pydicom
    from PIL import Image
    import io
    ds = pydicom.dcmread(path)
    arr = ds.pixel_array
    if arr.ndim == 3:
        arr = arr[..., 0]
    arr = arr.astype(float)
    # simple windowing for CT (soft tissue default)
    if ds.Modality == "CT":
        center, width = 40, 400
        arr = (arr - (center - width / 2)) / width * 255
    arr = (arr - arr.min()) / (arr.max() - arr.min() + 1e-9) * 255
    img = Image.fromarray(arr.astype("uint8"))
    buf = io.BytesIO()
    img.save(buf, "PNG")
    return base64.b64encode(buf.getvalue()).decode()

def wet_read(payload):
    uri = payload.get("dicom_web_uri", "")
    if DRY or "orthanc" not in uri:
        # dry-run: no fetch — return structured placeholder + note
        return {"instance_id": payload.get("instance_id"), "modality": payload.get("modality"),
                "status": "dry_run_no_fetch", "note": "Orthanc not reachable yet (NUR-68) — pipeline verified end-to-end after deploy",
                "requires_provider_review": True}
    # fetch DICOM via DICOMweb WADO-RS (when Orthanc live)
    req = urllib.request.Request(uri, headers={"Accept": "application/dicom"})
    with urllib.request.urlopen(req, timeout=30) as r:
        data = r.read()
    tmp = "/tmp/wet-read.dcm"
    open(tmp, "wb").write(data)
    png_b64 = dcm_to_png_bytes(tmp)
    # call the vision cascade with an OpenAI-style payload via vision-proxy CLI? use gemini lane directly
    import subprocess
    img = "/tmp/wet-read.png"
    import base64 as b64mod
    open(img, "wb").write(b64mod.b64decode(png_b64))
    r = subprocess.run(["python3", VP, img, "free-vl", IMPRESSION_PROMPT], capture_output=True, text=True, timeout=240)
    return {"instance_id": payload.get("instance_id"), "modality": payload.get("modality"),
            "impression": r.stdout.strip()[:3000], "requires_provider_review": True}

class H(BaseHTTPRequestHandler):
    def do_POST(self):
        if self.path != "/v1/wet-read":
            self.send_response(404); self.end_headers(); return
        n = int(self.headers.get("Content-Length", 0))
        try:
            payload = json.loads(self.rfile.read(n))
            out = wet_read(payload)
            body = json.dumps(out, indent=1).encode()
            self.send_response(200)
            self.send_header("Content-Type", "application/json")
            self.end_headers()
            self.wfile.write(body)
        except Exception as e:
            self.send_response(500)
            self.end_headers()
            self.wfile.write(json.dumps({"error": str(e)[:200]}).encode())
    def log_message(self, *a):
        pass

if __name__ == "__main__":
    print(f"wet-read gateway {'(DRY-RUN)' if DRY else ''} on :{PORT} — POST /v1/wet-read")
    HTTPServer(("127.0.0.1", PORT), H).serve_forever()
