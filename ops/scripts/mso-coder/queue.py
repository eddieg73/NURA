#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
MSO CODER PRIORITY QUEUE MANAGER — Phase 1 (in-memory, PHI-stripped)
=====================================================================
Orders chart reviews for the Coder Workspace by:
  1. RAF opportunity  (delta + recapture + suspected potential, desc)
  2. Suspected HCC count (desc)
  3. Unrecaptured flags (desc)
  4. Submission time (oldest first)

Metrics counters: enqueued / reviewed / validated / RAF improvement total /
suspected + unrecaptured totals / per-tier counts.

CONSTRAINTS: in-memory only (no production data writes). Queue items carry
PHI-stripped synthetic patient references and chart HASHES, never chart text.
"""
import hashlib
import json
import threading
import time
import uuid
from datetime import datetime, timezone

# ---------------------------------------------------------------------------
# Name-collision guard: this workspace file is named queue.py per the MSO
# spec, which shadows the Python stdlib 'queue' module on sys.path. FastAPI/
# anyio run sync endpoints through `from queue import Queue`, so we load the
# REAL stdlib queue module by path (a plain `import queue` here would bind to
# this same partially-initialized file) and re-export its symbols; the
# module-level __getattr__ (PEP 562) covers any other attribute.
# ---------------------------------------------------------------------------
import importlib.util
import os
import sysconfig

_stdlib_queue_path = os.path.join(sysconfig.get_path("stdlib"), "queue.py")
_stdlib_queue_spec = importlib.util.spec_from_file_location(
    "_stdlib_queue", _stdlib_queue_path)
_stdlib_queue = importlib.util.module_from_spec(_stdlib_queue_spec)
_stdlib_queue_spec.loader.exec_module(_stdlib_queue)

Queue = _stdlib_queue.Queue
PriorityQueue = _stdlib_queue.PriorityQueue
LifoQueue = _stdlib_queue.LifoQueue
SimpleQueue = _stdlib_queue.SimpleQueue
Empty = _stdlib_queue.Empty
Full = _stdlib_queue.Full


def __getattr__(name):
    return getattr(_stdlib_queue, name)


def _now_utc():
    return datetime.now(timezone.utc).isoformat(timespec="seconds")


def _raf_of(review_payload):
    """Extract the RAF numbers from a /review payload safely."""
    ri = (review_payload or {}).get("raf_impact", {}) or {}
    return (float(ri.get("delta") or 0.0),
            float(ri.get("before") or 0.0),
            float(ri.get("after") or 0.0))


def score_review(review_payload):
    """
    Priority score from a /review payload:
      raf_opportunity = positive delta + unrecaptured RAF + suspected estimate
      tier: high (>=0.50 or any unrecaptured), medium (>=0.20), else low
    """
    ri = (review_payload or {}).get("raf_impact", {}) or {}
    delta, _before, _after = _raf_of(review_payload)
    unrecaptured = ri.get("unrecaptured") or []
    suspected = ri.get("suspected") or []
    unc_raf = sum(float(u.get("raf_estimate") or u.get("raf") or 0.0)
                  for u in unrecaptured)
    sus_raf = sum(float(s.get("raf_estimate") or 0.0) for s in suspected)
    opportunity = round(max(delta, 0.0) + unc_raf + sus_raf, 3)
    n_unc, n_sus = len(unrecaptured), len(suspected)
    if opportunity >= 0.50 or n_unc > 0:
        tier = "high"
    elif opportunity >= 0.20:
        tier = "medium"
    else:
        tier = "low"
    return {
        "raf_opportunity": opportunity,
        "suspected_count": n_sus,
        "unrecaptured_count": n_unc,
        "tier": tier,
    }


class CodingQueue:
    """Thread-safe priority queue + metrics for the Coder Workspace."""

    def __init__(self, max_size=2000):
        self._lock = threading.RLock()   # reentrant: snapshot() nests priority_order()
        self._items = {}          # queue_id -> item
        self._max_size = max_size
        self._metrics = {
            "enqueued": 0, "reviewed": 0, "validated": 0,
            "raf_improvement_total": 0.0,
            "suspected_total": 0, "unrecaptured_total": 0,
            "by_tier": {"high": 0, "medium": 0, "low": 0},
            "avg_turnaround_s": 0.0,
        }
        self._turnaround_sum_s = 0.0

    # ------------------------------------------------------------------
    def submit(self, review_payload, patient_ref="SYNTHETIC", source="mso-api"):
        """Enqueue a completed /review payload. Returns the queue item."""
        sc = score_review(review_payload)
        item = {
            "queue_id": uuid.uuid4().hex[:12],
            "review_id": (review_payload or {}).get("review_id", ""),
            "patient_ref": patient_ref,          # PHI-stripped synthetic only
            "chart_sha256": hashlib.sha256(
                str(review_payload.get("chart_meta", {}) or {}).encode()
            ).hexdigest()[:16],
            "submitted_at": _now_utc(),
            "submitted_ts": time.time(),
            "source": source,
            "priority": sc,
            "raf_delta": _raf_of(review_payload)[0],
            "status": "queued",                  # queued|reviewed|validated
        }
        with self._lock:
            while len(self._items) >= self._max_size:
                self._items.pop(next(iter(self._items)))
            self._items[item["queue_id"]] = item
            self._metrics["enqueued"] += 1
            self._metrics["suspected_total"] += sc["suspected_count"]
            self._metrics["unrecaptured_total"] += sc["unrecaptured_count"]
            self._metrics["by_tier"][sc["tier"]] += 1
        return item

    # ------------------------------------------------------------------
    def priority_order(self, tier=None):
        """Sorted by (raf_opportunity desc, suspected desc, unrecaptured desc,
        submitted_ts asc)."""
        with self._lock:
            items = list(self._items.values())
        if tier:
            items = [i for i in items if i["priority"]["tier"] == tier]
        return sorted(items, key=lambda i: (
            -i["priority"]["raf_opportunity"],
            -i["priority"]["suspected_count"],
            -i["priority"]["unrecaptured_count"],
            i["submitted_ts"]))

    # ------------------------------------------------------------------
    def mark_reviewed(self, queue_id):
        with self._lock:
            item = self._items.get(queue_id)
            if not item:
                return False
            if item["status"] == "queued":
                self._metrics["reviewed"] += 1
            item["status"] = "reviewed"
            item["reviewed_at"] = _now_utc()
            self._turnaround_sum_s += time.time() - item["submitted_ts"]
            n = max(self._metrics["reviewed"], 1)
            self._metrics["avg_turnaround_s"] = round(
                self._turnaround_sum_s / n, 1)
            return True

    def mark_validated(self, queue_id, raf_gain=0.0):
        """Provider approved a review — count the realized RAF improvement."""
        with self._lock:
            item = self._items.get(queue_id)
            if not item:
                return False
            if item["status"] != "validated":
                self._metrics["validated"] += 1
            item["status"] = "validated"
            item["validated_at"] = _now_utc()
            item["raf_gain_validated"] = float(raf_gain)
            self._metrics["raf_improvement_total"] = round(
                self._metrics["raf_improvement_total"] + float(raf_gain), 3)
            return True

    # ------------------------------------------------------------------
    def metrics(self):
        with self._lock:
            m = dict(self._metrics)
            m["queued_open"] = sum(
                1 for i in self._items.values() if i["status"] == "queued")
            m["generated_at_utc"] = _now_utc()
        return m

    def snapshot(self):
        with self._lock:
            return {
                "priority_order": [
                    {k: v for k, v in i.items() if k != "submitted_ts"}
                    for i in self.priority_order()],
                "metrics": self.metrics(),
                "note": "PHI-stripped: synthetic patient refs + chart hashes only",
                "status": "DRAFT \u2014 PROVIDER APPROVAL REQUIRED",
            }


_QUEUE = CodingQueue()


def get_queue():
    return _QUEUE


if __name__ == "__main__":  # CLI self-test with synthetic PHI-stripped reviews
    import nura_engine

    def fake_review(delta, unc, sus, review_id):
        return {
            "review_id": review_id,
            "raf_impact": {
                "delta": delta, "before": 0.0, "after": delta,
                "unrecaptured": [{"code": u["code"], "raf_estimate": u["raf"],
                                  "flag": "unrecaptured"}
                                 for u in unc],
                "suspected": [{"condition": s["cond"],
                               "raf_estimate": s["raf"],
                               "flag": "suspected"} for s in sus],
            },
        }

    q = get_queue()
    eng = nura_engine.get_engine()
    ref = eng.load_reference(eng.DEFAULT_REF)

    # 1) the Phase-1 sample chart (72yo DM2/CKD3b/CHF) — high opportunity
    sample = nura_engine.analyze_chart(eng.SAMPLE_ENCOUNTER, use_llm=False)
    raf_after = round(sum(float(c.get("raf") or 0) for c in sample["candidates"]
                          if c.get("hcc")), 3)
    q.submit(fake_review(raf_after - 0.166, [], [], "R-SAMPLE72"),
             patient_ref="SYN-72-DM2-CKD3-CHF")

    # 2) unrecaptured old MI (V28 trap) — high priority flag
    q.submit(fake_review(0.0, [{"code": "I252", "raf": 0.191}], [],
                         "R-UNRECAP-MI"),
             patient_ref="SYN-81-UNRECAP-OLDMIM")

    # 3) suspected diabetes (signal only) — medium
    q.submit(fake_review(0.0, [], [{"cond": "Diabetes mellitus",
                                    "raf": 0.166}], "R-SUSPECT-DM"),
             patient_ref="SYN-68-SUSPECT-DM2")

    # 4) low: HTN + GERD only
    q.submit(fake_review(0.0, [], [], "R-LOW-HTN"),
             patient_ref="SYN-55-HTN-GERD")

    print("=== MSO CODER QUEUE — priority order (DRAFT, PHI-stripped) ===")
    for i, item in enumerate(q.priority_order(), 1):
        p = item["priority"]
        print(f"{i}. {item['patient_ref']:<28} tier={p['tier']:<7} "
              f"raf_opp={p['raf_opportunity']:<6} susp={p['suspected_count']} "
              f"unrecap={p['unrecaptured_count']}")
    print("\n=== METRICS ===")
    print(json.dumps(q.metrics(), indent=2))
