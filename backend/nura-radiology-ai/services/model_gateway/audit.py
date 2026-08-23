"""Audit log — every gateway call is recorded (who/what/when/provenance/outcome)."""
import time, json, logging
from pathlib import Path

logger = logging.getLogger("nura.gateway.audit")


class AuditLog:
    def __init__(self, path=None):
        self.path = path or "/opt/data/nura-radiology-ai/model-gateway/audit.jsonl"
        Path(self.path).parent.mkdir(parents=True, exist_ok=True)

    def record(self, entry: dict):
        entry = {**{"ts": time.strftime("%Y-%m-%dT%H:%M:%SZ"), "source": "model_gateway"}, **entry}
        try:
            with open(self.path, "a") as f:
                f.write(json.dumps(entry) + "\n")
        except Exception as e:
            logger.warning("audit write failed: %s", e)
        return entry
