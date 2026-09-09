#!/usr/bin/env python3
"""Ensure -> CarePilot FastAPI propose-only intake stub.

- Optional: accept a JSON path of already-extracted read-only Ensure rows
- Maps to a propose-only intake POST shape
- POSTs to localhost FastAPI when up; otherwise writes normalized JSON under ./out/
- Never auto-orders / claims / diagnoses. No SFTP.
"""
from __future__ import annotations

import argparse
import json
import os
import sys
import uuid
from datetime import datetime, timezone
from pathlib import Path
from typing import Any
from urllib.error import URLError, HTTPError
from urllib.request import Request, urlopen

OUT_DIR = Path(__file__).resolve().parent / "out"
DEFAULT_BASE = os.environ.get("CAREPILOT_API_BASE", "http://127.0.0.1:8100")
INTAKE_PATH = os.environ.get("ENSURE_INTAKE_PATH", "/api/integrations/ensure/intake")
WORK_QUEUE_PATH = "/api/work-queue"
HEALTH_PATH = "/health"

SAFETY = {
    "mode": "propose_only",
    "no_auto_orders": True,
    "no_auto_claims": True,
    "no_auto_diagnoses": True,
    "no_sftp_writes": True,
    "lane": "A_ensure_rpa_read",
}


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


def http_json(method: str, url: str, body: dict | None = None, timeout: float = 8.0) -> tuple[int, Any]:
    data = None
    headers = {"Accept": "application/json", "X-Role": "care_coordinator"}
    if body is not None:
        data = json.dumps(body).encode("utf-8")
        headers["Content-Type"] = "application/json"
    req = Request(url, data=data, headers=headers, method=method)
    with urlopen(req, timeout=timeout) as resp:
        raw = resp.read().decode("utf-8") or "{}"
        try:
            parsed = json.loads(raw)
        except json.JSONDecodeError:
            parsed = {"raw": raw[:500]}
        return resp.status, parsed


def fastapi_up(base: str) -> bool:
    try:
        code, _ = http_json("GET", base.rstrip("/") + HEALTH_PATH)
        return 200 <= code < 300
    except Exception:
        return False


def normalize_rows(rows: list[dict]) -> dict:
    """Map generic Ensure extract rows into propose-only intake envelope."""
    proposals = []
    for i, row in enumerate(rows):
        # Keep only non-PHI-safe operational fields when present; pass through
        # opaque refs the human team already owns. Do not invent clinical actions.
        drop = {
                "mrn", "patient_name", "ssn", "dob", "name", "first_name", "last_name",
                "member_id", "subscriber_id", "phone", "email", "address", "diagnosis",
                "medications", "claims", "orders",
            }
        clean = {k: v for k, v in row.items() if k not in drop}
        # Prefer explicit aggregate signals blob when present
        if isinstance(clean.get("signals"), dict):
            sig = clean["signals"]
            clean["signals"] = {
                sk: sv for sk, sv in sig.items()
                if sk in (
                    "page_title", "url_path_hash", "nav_item_count", "metric_card_count",
                    "link_count", "button_count", "nav_labels_safe", "metric_labels_safe",
                    "phi_policy",
                )
            }
        proposals.append({
            "proposal_id": str(uuid.uuid4()),
            "source": "ensure_portal",
            "kind": row.get("kind") or "ensure_work_item",
            "status": "proposed",
            "requires_human_approval": True,
            "external_ref": row.get("external_ref") or row.get("id") or f"ensure-row-{i}",
            "summary": row.get("summary") or "Ensure read-only item (propose-only)",
            "payload": clean,
        })
    return {
        "ok": True,
        "received_at": utc_now(),
        "safety": SAFETY,
        "count": len(proposals),
        "proposals": proposals,
    }


def write_out(envelope: dict, tag: str) -> Path:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    path = OUT_DIR / f"ensure_intake_{tag}_{datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%SZ')}.json"
    path.write_text(json.dumps(envelope, indent=2) + "\n")
    return path


def post_intake(base: str, envelope: dict) -> tuple[bool, str]:
    url = base.rstrip("/") + INTAKE_PATH
    try:
        code, body = http_json("POST", url, envelope)
        return True, f"POST {url} -> {code} keys={list(body)[:8] if isinstance(body, dict) else type(body)}"
    except HTTPError as e:
        # Endpoint may not exist yet — fall back note
        return False, f"HTTPError {e.code} on {url}"
    except URLError as e:
        return False, f"URLError {e.reason}"
    except Exception as e:
        return False, f"{type(e).__name__}: {e}"


def demo_rows() -> list[dict]:
    return [{
        "kind": "ensure_queue_probe",
        "external_ref": "demo-ensure-1",
        "summary": "Synthetic Ensure row for wiring check (no PHI)",
        "lane": "A",
    }]


def main() -> int:
    ap = argparse.ArgumentParser(description="Ensure -> FastAPI propose-only intake stub")
    ap.add_argument("--json", dest="json_path", help="Path to JSON list/object of Ensure extract rows")
    ap.add_argument("--base", default=DEFAULT_BASE, help="CarePilot FastAPI base URL")
    ap.add_argument("--demo", action="store_true", help="Use synthetic non-PHI demo row")
    ap.add_argument("--extract", action="store_true", help="Reserved: read-only extract (not implemented beyond demo)")
    args = ap.parse_args()

    if args.json_path:
        raw = json.loads(Path(args.json_path).read_text())
        if isinstance(raw, dict) and "rows" in raw:
            rows = raw["rows"]
        elif isinstance(raw, list):
            rows = raw
        else:
            rows = [raw]
    elif args.demo or args.extract:
        rows = demo_rows()
    else:
        print("Provide --json PATH or --demo. Refusing empty intake.")
        return 2

    envelope = normalize_rows(rows)
    up = fastapi_up(args.base)
    print(f"FASTAPI_REACHABLE={'yes' if up else 'no'} base={args.base}")

    if up:
        ok, note = post_intake(args.base, envelope)
        print("POST_NOTE=" + note)
        if ok:
            print("DISPOSITION=posted_propose_only")
            return 0
        # fallback write
        path = write_out(envelope, "fallback")
        print(f"DISPOSITION=wrote_out_after_post_fail path={path}")
        print("NOTE=FastAPI up but intake POST failed; normalized JSON written for human review")
        return 0

    path = write_out(envelope, "offline")
    print(f"DISPOSITION=wrote_out_engine_down path={path}")
    print("NOTE=CarePilot FastAPI not reachable; wrote propose-only normalized JSON under out/")
    return 0


if __name__ == "__main__":
    sys.exit(main())
