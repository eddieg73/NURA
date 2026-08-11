#!/usr/bin/env python3
"""NURA TRACE-CLASSIFIER — the Layer-3 artifact: classify a failed run into the 3 buckets.
Usage: trace-classifier.py --log <file-or-stdin> → the bucket + the evidence-line."""
import sys, re, argparse

PLANNING = ["wrong approach", "misread", "invalid_request", "no such", "not found", "404", "doesn't exist", "unsupported"]
EXECUTION = ["traceback", "exception", "syntaxerror", "typeerror", "valueerror", "non-null constraint", "connection refused",
             "timeout", "exit 1", "sqlite_constraint", "401", "403", "500", "502", "failed to connect"]
CONTEXT = ["too large", "token limit", "overflow", "payload", "context window", "exceeded", "max length", "too long"]

def classify(text):
    t = text.lower()
    scores = {}
    for bucket, pats in [("PLANNING", PLANNING), ("EXECUTION", EXECUTION), ("CONTEXT-OVERFLOW", CONTEXT)]:
        hits = [p for p in pats if p in t]
        scores[bucket] = hits
    ranked = sorted(scores.items(), key=lambda kv: -len(kv[1]))
    top, hits = ranked[0]
    return top, hits[:3]

if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--log", default="-")
    a = ap.parse_args()
    text = sys.stdin.read() if a.log == "-" else open(a.log, encoding="utf-8", errors="ignore").read()
    bucket, hits = classify(text)
    print(f"CLASSIFICATION: {bucket}")
    print(f"EVIDENCE: {', '.join(hits) if hits else '(no-pattern-match — manual review!)'}")
    print(f"RECOMMENDATION: " + {
        "PLANNING": "re-plan the approach (the plan-griller!) — the intent/tool-choice misread",
        "EXECUTION": "fix the call (the script/API-error!) — the syntax/runtime-correction + retry",
        "CONTEXT-OVERFLOW": "reduce the payload (the context-filter!) — the token-efficiency-pass",
    }.get(bucket, "manual-review"))
