#!/usr/bin/env python3
from __future__ import annotations

import argparse
import hashlib
import json
import os
import time
from datetime import datetime, timezone
from uuid import uuid4

import httpx

from app.security import sign_request


def main() -> int:
    parser = argparse.ArgumentParser(description="Send a signed event to the Hermes bridge")
    parser.add_argument("--url", required=True)
    parser.add_argument("--secret", default=os.getenv("HERMES_WEBHOOK_SECRET"))
    parser.add_argument("--key-id", default=os.getenv("HERMES_WEBHOOK_KEY_ID", "primary"))
    parser.add_argument("--event-type", default="nura.hermes.review.requested.v1")
    parser.add_argument("--source-service", default="hermes-agent")
    parser.add_argument("--work-item", required=True)
    parser.add_argument("--summary", required=True)
    parser.add_argument("--link")
    parser.add_argument("--priority", choices=["P1", "P2", "P3", "P4"], default="P2")
    parser.add_argument("--status", choices=["Assigned", "In Progress", "Needs Review", "Approved", "Blocked", "Done"], default="Needs Review")
    parser.add_argument("--idempotency-key")
    args = parser.parse_args()
    if not args.secret:
        parser.error("--secret or HERMES_WEBHOOK_SECRET is required")

    event_id = str(uuid4())
    idempotency_key = args.idempotency_key or hashlib.sha256(
        f"{args.event_type}:{args.work_item}:{event_id}".encode("utf-8")
    ).hexdigest()
    event = {
        "spec_version": "1.0",
        "event_id": event_id,
        "event_type": args.event_type,
        "source_service": args.source_service,
        "tenant_id": "nuratech",
        "correlation_id": event_id,
        "idempotency_key": idempotency_key,
        "occurred_at": datetime.now(timezone.utc).isoformat(),
        "data_classification": "INTERNAL",
        "provenance": {"producer": args.source_service, "sender": "send_event.py"},
        "severity": "info",
        "notification": {
            "work_item": args.work_item,
            "summary": args.summary,
            "lane": "Platform/Engineering",
            "priority": args.priority,
            "status": args.status,
            "work_type": "Review",
            "owner": "Hermes",
            "reviewer": "ChatGPT",
            "link": args.link,
        },
    }
    raw_body = json.dumps(event, separators=(",", ":"), sort_keys=True).encode("utf-8")
    timestamp = str(int(time.time()))
    headers = {
        "Content-Type": "application/json",
        "X-Hermes-Event-Id": event_id,
        "X-Hermes-Timestamp": timestamp,
        "X-Hermes-Key-Id": args.key_id,
        "X-Hermes-Signature": sign_request(args.secret, timestamp, event_id, raw_body),
    }
    response = httpx.post(args.url, content=raw_body, headers=headers, timeout=15)
    print(response.status_code, response.text)
    return 0 if response.is_success else 1


if __name__ == "__main__":
    raise SystemExit(main())
