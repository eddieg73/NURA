#!/usr/bin/env python3
"""NURA Trace Lane — structured, auditable end-to-end tracing for agent runs.

Implements the observability-trace-logger skill contract:
  - stable run_id across the whole run
  - one structured (component, event, timestamped-detail) entry per meaningful step
  - success=False on the first failure → detectable without rerunning
  - JSON export (append-only JSONL audit store — survives restart, auditable)
  - tracing is SEPARATE from orchestration (never changes behavior)

Span wrapping lets you trace across model call -> tool -> retrieval -> agent decision
(the gap identified in AI Eng Fundamentals #6 Logging vs Tracing).

Usage:
    from trace_lane import Trace, trace_span
    t = Trace(run_id="...", patient_id="...", agent="radintel")
    with trace_span(t, "planning", "plan_created"):
        ...
    with trace_span(t, "tool", "openemr_lab_trends", success=result_ok, result=...):
        ...
    t.add("agent", "decision", decision="...")
    t.export()  # appends JSON to the audit store

Reader:  TraceReader().get(run_id) -> list of events; first failure point queryable.
"""
import json
import os
import sys
import time
import uuid
import datetime
import threading
from contextlib import contextmanager

AUDIT_DIR = os.environ.get("NURA_TRACE_AUDIT_DIR", "/opt/data/profiles/nura/cron/output/traces")
AUDIT_FILE = os.path.join(AUDIT_DIR, "trace-lane.jsonl")

_lock = threading.Lock()


def _utcnow():
    return datetime.datetime.now(datetime.timezone.utc).isoformat()


class Trace:
    """A single run trace. append-only events; orchestration stays outside."""

    def __init__(self, run_id=None, patient_id=None, agent="hermes", model=None):
        self.run_id = run_id or uuid.uuid4().hex[:12]
        self.patient_id = patient_id
        self.agent = agent
        self.model = model
        self.events = []
        self._step = 0

    def add(self, component, event, success=None, **detail):
        """Record one structured trace entry (thread-safe, ordered)."""
        self._step += 1
        entry = {
            "run_id": self.run_id,
            "step": self._step,
            "timestamp": _utcnow(),
            "component": component,
            "event": event,
            "agent": self.agent,
            "model": self.model,
            "patient_id": self.patient_id,
            "detail": detail,
        }
        if success is not None:
            entry["success"] = success
        with _lock:
            self.events.append(entry)
        return entry

    # ------- dedicated span wrappers for the traceable surface -------
    @contextmanager
    def span(self, component, event, **fixed):
        """Context manager: emits started + completed span entries.

        Semantics (the contract):
          - 'started' entry is success-neutral (is_started=True)
          - if caller passes success=, honor it on the completion entry
          - else set success=True on normal completion, success=False on exception
        The first completion entry with success=False is the detectable failure point.
        """
        explicit_success = fixed.pop("success", None)
        self.add(component, event, is_started=True, **fixed)
        try:
            yield
        except Exception as exc:
            self.add(component, event, success=False,
                     error=str(exc)[:300], **fixed)
            raise
        else:
            self.add(component, event,
                     success=(True if explicit_success is None else explicit_success),
                     **fixed)

    def tool(self, name, result=None, success=None, **detail):
        kw = dict(detail)
        if result is not None:
            kw["result"] = result
        return self.span("tool", f"tool_called:{name}", tool=name, success=success, **kw)

    def retrieval(self, source, hits=None, success=None, **detail):
        return self.span("retrieval", f"retrieved:{source}", source=source,
                         hits=hits, success=success, **detail)

    def model_call(self, provider, model, success=None, **detail):
        return self.span("model", f"llm_call:{model}", provider=provider,
                         model=model, success=success, **detail)

    # ------- export -------
    def export(self, file=AUDIT_FILE):
        os.makedirs(os.path.dirname(file), exist_ok=True)
        payload = self.to_json()
        with _lock:
            with open(file, "a", encoding="utf-8") as f:
                f.write(json.dumps(payload, ensure_ascii=False, default=str) + "\n")
        return file

    def to_json(self):
        return {
            "run_id": self.run_id,
            "agent": self.agent,
            "patient_id": self.patient_id,
            "model": self.model,
            "created": self.events[0]["timestamp"] if self.events else _utcnow(),
            "event_count": len(self.events),
            "trace": self.events,
            "first_failure": self.first_failure(),
        }

    def first_failure(self):
        for e in self.events:
            if e.get("success") is False:
                return {"component": e["component"], "event": e["event"],
                        "error": e.get("detail", {}).get("error", ""), "step": e["step"]}
        return None


class TraceReader:
    """Read/mine the audit store. First-failure point queryable without rerunning."""

    def __init__(self, file=AUDIT_FILE):
        self.file = file

    def _lines(self):
        if not os.path.exists(self.file):
            return []
        with open(self.file, encoding="utf-8") as f:
            return [l for l in f if l.strip()]

    def all_run_ids(self):
        out = []
        for l in self._lines():
            try:
                out.append(json.loads(l)["run_id"])
            except Exception:
                continue
        return out

    def get(self, run_id):
        for l in self._lines():
            try:
                d = json.loads(l)
            except Exception:
                continue
            if d.get("run_id") == run_id:
                return d
        return None

    def first_failures(self, limit=50):
        """All runs where a failure occurred, with the first failing step."""
        out = []
        for l in self._lines():
            try:
                d = json.loads(l)
            except Exception:
                continue
            ff = d.get("first_failure")
            if ff:
                out.append({"run_id": d["run_id"], "agent": d.get("agent"),
                            "first_failure": ff, "created": d.get("created")})
        return out[:limit]


if __name__ == "__main__":
    # self-demonstration (proves the lane works end-to-end, not just a description)
    t = Trace(run_id="demo-run", patient_id="pt-001", agent="radintel", model="demo-model")
    with t.retrieval("openemr_lab_history", hits=3):
        pass
    with t.model_call("deepseek", "deepseek-v4-flash-vision-exp"):
        pass
    with t.tool("openemr_lab_trends", result="trends_ok"):
        pass
    with t.tool("chart_append", success=False, error="provider gate not met"):
        pass
    t.add("agent", "decision", decision="flag for provider review")

    f = t.export()
    print("exported ->", f)
    print("run_id:", t.run_id, "events:", len(t.events))
    print("first_failure:", t.first_failure())

    # read-back via reader (external-state verification, not self-report)
    r = TraceReader()
    got = r.get(t.run_id)
    print("reader returned run:", got["run_id"], "events:", got["event_count"])
    print("reader first_failures (all runs):", r.first_failures()[:3])
