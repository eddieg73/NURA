#!/usr/bin/env python3
"""THE FAILURE-TAXONOMY — the F01-F18 classifier (the trace-classifier's upgrade!).
Every failure → the F-code → the candidate-fix → the replay-measurement (the statistically-tractable learning!)."""
import re, sys

TAXONOMY = {
    "F01": ("reasoning failure", ["incorrect logic", "wrong conclusion", "misreason"]),
    "F02": ("factual hallucination", ["fabricated", "hallucinat", "not in source", "unsupported claim"]),
    "F03": ("retrieval failure", ["no results", "search empty", "not found", "retrieval"]),
    "F04": ("tool-selection failure", ["wrong tool", "should have used", "tool selection"]),
    "F05": ("tool-execution failure", ["traceback", "exception", "connection refused", "timeout", "500", "502", "non-null constraint", "not null constraint", "sqlite_constraint"]),
    "F06": ("planning failure", ["wrong approach", "misread", "invalid_request", "no such"]),
    "F07": ("premature termination", ["interrupted", "killed", "stopped early"]),
    "F08": ("unnecessary tool use", ["redundant call", "unnecessary"]),
    "F09": ("excessive token consumption", ["token limit", "context overflow", "too long", "truncat"]),
    "F10": ("latency regression", ["slow", "latency", "timed out after"]),
    "F11": ("skill selection failure", ["wrong skill", "skill not applicable"]),
    "F12": ("stale skill", ["outdated", "stale", "deprecated"]),
    "F13": ("memory contamination", ["memory conflict", "contamination", "stale memory"]),
    "F14": ("instruction-following failure", ["misunderstood instruction", "did not follow"]),
    "F15": ("authorization/safety violation", ["unauthorized", "permission denied", "security"]),
    "F16": ("environment/dependency failure", ["module not found", "import error", "dependency", "not installed"]),
    "F17": ("coding regression", ["regression", "test failed", "breaking change"]),
    "F18": ("test coverage deficiency", ["no test", "coverage", "untested"]),
}

def classify(text):
    t = text.lower()
    hits = []
    for code, (name, pats) in TAXONOMY.items():
        for p in pats:
            if p in t:
                hits.append((code, name, p))
                break
    return hits or [("F99", "unclassified", "")]

if __name__ == "__main__":
    text = sys.stdin.read() if not sys.argv[1:] else open(sys.argv[1], encoding="utf-8", errors="ignore").read()
    hits = classify(text)
    print("FAILURE-CLASSIFICATION:")
    for code, name, pat in hits[:5]:
        print(f"  {code} {name} (matched: '{pat}')")
