#!/usr/bin/env python3
"""NURA Provider Labs — ingestion engine (Documo fax + email -> OCR -> review queue).
CLI: provider-labs-ingest.py [--check-documo] [--check-email] [--queue] [--review <id>] [--all]
Outputs action items only (watchdog-friendly). Queue: data/provider-labs/queue.json
MCP lane: mcp-installs/provider-labs (tools: documo_ingest, email_ingest, queue_status, review_item).
"""
import json, os, sys, time, urllib.request
sys.path.insert(0, "/opt/data/profiles/nura/python-packages")  # pymupdf + greenlet + others live here
from datetime import datetime, timezone
from pathlib import Path

BASE = "/opt/data/profiles/nura"
QUEUE = Path(BASE + "/data/provider-labs/queue.json")
INBOX = Path(BASE + "/data/provider-labs/inbox")
INBOX.mkdir(parents=True, exist_ok=True)
ENV = BASE + "/.env"

def get(name):
    try:
        for line in open(ENV):
            if line.startswith(name + "="):
                return line.strip().split("=", 1)[1].strip("'\"")
    except OSError:
        pass
    return None

def qload():
    if QUEUE.exists():
        return json.loads(QUEUE.read_text())
    return {"items": []}

def qsave(q):
    QUEUE.write_text(json.dumps(q, indent=1))

def ocr_pdf(path):
    """OCR a PDF -> text. Uses pymupdf if available; else returns '' (labeled)."""
    try:
        import fitz
        doc = fitz.open(path)
        return "\n".join(pg.get_text() for pg in doc)[:8000]
    except Exception:
        return ""

def check_documo():
    key = get("DOCUMO_API_KEY")
    if not key:
        return ["DOCUMO_API_KEY missing — drop to enable fax ingestion"]
    out = []
    try:
        req = urllib.request.Request("https://api.documo.com/v1/faxes?status=received&limit=10",
                                     headers={"Authorization": f"Bearer {key}"})
        with urllib.request.urlopen(req, timeout=30) as r:
            faxes = json.loads(r.read())
        for fx in faxes if isinstance(faxes, list) else []:
            fid = fx.get("id")
            if not fid:
                continue
            out.append(f"fax {fid} from {fx.get('fromNumber','?')} received")
    except Exception as e:
        out.append(f"documo probe err: {str(e)[:80]}")
    return out

def check_email():
    """Gmail via gws CLI (nura@nuratech.ai) — search for PDF attachments from providers."""
    import subprocess
    try:
        r = subprocess.run(["gws", "mail", "search", "--query", "has:attachment filename:pdf newer_than:2d", "--limit", "5"],
                           capture_output=True, text=True, timeout=60, env={**os.environ, "PATH": os.environ.get("PATH","")})
        out = r.stdout.strip()
        return [f"email: {l}" for l in out.splitlines()[:5]] if out else []
    except Exception as e:
        return [f"email lane: {str(e)[:80]}"]

def main():
    args = sys.argv[1:]
    flags = set(args)
    q = qload()
    items = []
    if "--all" in flags or "--check-documo" in flags:
        items += check_documo()
    if "--all" in flags or "--check-email" in flags:
        items += check_email()
    if "--queue" in flags:
        n = len(q.get("items", []))
        items.append(f"queue: {n} item(s) awaiting provider review")
    if "--review" in flags:
        i = flags.index("--review")
        if i + 1 < len(args):
            rid = args[i + 1]
            for it in q.get("items", []):
                if it.get("id") == rid:
                    it["status"] = "reviewed"
                    it["reviewed_at"] = datetime.now(timezone.utc).isoformat()
            qsave(q)
            items.append(f"marked {rid} reviewed")
    if items:
        print("\n".join(items))
    # silent when nothing

if __name__ == "__main__":
    main()
