from __future__ import annotations

import hashlib
import hmac
import time


class SignatureError(ValueError):
    pass


def _parse_signature(signature_header: str) -> str:
    try:
        version, digest = signature_header.split("=", 1)
    except ValueError as exc:
        raise SignatureError("Malformed X-Hermes-Signature header") from exc
    if version != "v1" or len(digest) != 64:
        raise SignatureError("Unsupported signature version or digest length")
    try:
        bytes.fromhex(digest)
    except ValueError as exc:
        raise SignatureError("Signature digest must be hexadecimal") from exc
    return digest.lower()


def signing_payload(timestamp: str, event_id: str, raw_body: bytes) -> bytes:
    return timestamp.encode("ascii") + b"." + event_id.encode("ascii") + b"." + raw_body


def sign_request(secret: str, timestamp: str, event_id: str, raw_body: bytes) -> str:
    digest = hmac.new(
        secret.encode("utf-8"),
        signing_payload(timestamp, event_id, raw_body),
        hashlib.sha256,
    ).hexdigest()
    return f"v1={digest}"


def verify_request(
    *,
    raw_body: bytes,
    event_id: str,
    timestamp: str,
    signature_header: str,
    key_id: str,
    expected_key_id: str,
    secret: str,
    max_age_seconds: int,
    now: int | None = None,
) -> None:
    if key_id != expected_key_id:
        raise SignatureError("Unknown webhook key ID")
    try:
        timestamp_value = int(timestamp)
    except ValueError as exc:
        raise SignatureError("X-Hermes-Timestamp must be Unix seconds") from exc
    current = int(time.time()) if now is None else now
    if abs(current - timestamp_value) > max_age_seconds:
        raise SignatureError("Webhook timestamp is outside the replay window")
    provided = _parse_signature(signature_header)
    expected = sign_request(secret, timestamp, event_id, raw_body).split("=", 1)[1]
    if not hmac.compare_digest(provided, expected):
        raise SignatureError("Invalid webhook signature")
