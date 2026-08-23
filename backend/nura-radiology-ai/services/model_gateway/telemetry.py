"""Gateway telemetry — provider, latency, route, outcome, model."""
import time, json, logging, os
from pathlib import Path

logger = logging.getLogger("nura.gateway.telemetry")


class Telemetry:
    def __init__(self, path=None):
        self.path = path or "/opt/data/nura-radiology-ai/model-gateway/telemetry.jsonl"
        Path(self.path).parent.mkdir(parents=True, exist_ok=True)

    def record(self, task, provider, route, ok, latency_ms, notes=None):
        row = {"task": task, "provider": provider, "route": route, "ok": ok,
               "latency_ms": round(latency_ms, 1), "ts": time.strftime("%Y-%m-%dT%H:%M:%SZ"),
               "notes": notes or []}
        try:
            with open(self.path, "a") as f:
                f.write(json.dumps(row) + "\n")
        except Exception as e:
            logger.warning("telemetry write failed: %s", e)
        return row
