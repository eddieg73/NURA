"""Optional propose-only Ensure intake route to mount on CarePilot FastAPI.

Keeps AI propose-only: stores proposals in memory / returns ack; never orders/claims/diagnoses.
"""
from fastapi import APIRouter
from pydantic import BaseModel, Field
from typing import Any, Optional
from datetime import datetime, timezone
import uuid

router = APIRouter(prefix="/api/integrations/ensure", tags=["ensure"])

_PROPOSALS: list[dict] = []

class EnsureIntake(BaseModel):
    ok: bool = True
    received_at: Optional[str] = None
    safety: dict[str, Any] = Field(default_factory=dict)
    count: int = 0
    proposals: list[dict[str, Any]] = Field(default_factory=list)

@router.post("/intake")
def ensure_intake(body: EnsureIntake):
    """Propose-only intake. Does not place orders, submit claims, or add diagnoses."""
    ack_id = str(uuid.uuid4())
    entry = {
        "ack_id": ack_id,
        "received_at": body.received_at or datetime.now(timezone.utc).isoformat(),
        "count": body.count or len(body.proposals),
        "safety": body.safety or {"mode": "propose_only"},
        "proposals": body.proposals,
        "status": "queued_for_human_review",
    }
    _PROPOSALS.append({"ack_id": ack_id, "count": entry["count"]})
    return {"ok": True, "mode": "propose_only", "ack_id": ack_id, "queued": entry["count"]}

@router.get("/intake/queued")
def ensure_queued():
    return {"ok": True, "queued": len(_PROPOSALS), "acks": _PROPOSALS[-20:]}
