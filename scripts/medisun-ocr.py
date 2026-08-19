#!/usr/bin/env python3
"""Medisun Forms OCR — the PDF → the local vision → the structured JSON.
The pattern: the pymupdf render → the Ollama vision (the minicpm-v/qwen3-vl) → the field extract.
"""
import sys, os, json, base64, subprocess, time

VISION_MODEL = "minicpm-v:8b"
OLLAMA = "http://127.0.0.1:11434/api/generate"

def render_pdf(pdf_path, dpi=100):
    import pymupdf as fitz
    d = fitz.open(pdf_path)
    pages = []
    for i in range(len(d)):
        p = d[i].get_pixmap(dpi=dpi)
        path = f"/tmp/medisun-p{i}.png"
        p.save(path)
        pages.append(path)
    return pages

def vision_read(img_path, prompt):
    img = base64.b64encode(open(img_path, "rb").read()).decode()
    body = json.dumps({"model": VISION_MODEL, "prompt": prompt, "images": [img],
                       "stream": False, "options": {"num_predict": 300}})
    for attempt in range(2):
        r = subprocess.run(["curl", "-s", "-m", "380", OLLAMA, "-d", body],
                           capture_output=True, text=True, timeout=410)
        try:
            resp = json.loads(r.stdout).get("response", "")
            if resp.strip():
                return resp
        except Exception:
            pass
        time.sleep(5)
        VISION_MODEL_ALT = "qwen3-vl:8b"
        body = body.replace(VISION_MODEL, VISION_MODEL_ALT)
        VISION_MODEL = VISION_MODEL_ALT
    return ""

def main():
    pdf = sys.argv[1]
    pages = render_pdf(pdf)
    print(f"pages: {len(pages)}")
    results = []
    for i, p in enumerate(pages):
        txt = vision_read(p, "Extract ALL the fields and text from this form. List every labeled field with its value if visible.")
        results.append({"page": i + 1, "extracted": txt})
        print(f"  page {i+1}: {'ok' if txt else 'empty'}")
    out = pdf.replace(".pdf", "-ocr.json")
    json.dump({"source": pdf, "pages": results}, open(out, "w"), indent=2)
    print("saved:", out)

if __name__ == "__main__":
    main()
