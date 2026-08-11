#!/usr/bin/env python3
"""NURA CONTEXT-FILTER — the Layer-1 standard: probe → reduce → return-small.
The harness-pattern: filter INSIDE the sandbox, return ONLY the small-window to the context."""
import json, sys

def filter_json(data, keys=None, max_items=10, max_len=400):
    """Reduce a JSON payload to the essential-window."""
    if isinstance(data, list):
        out = data[:max_items]
        if keys:
            out = [{k: item.get(k) for k in keys if k in item} for item in out]
    elif isinstance(data, dict):
        out = {k: data[k] for k in keys if k in data} if keys else data
    else:
        out = data
    s = json.dumps(out, default=str)
    return s[:max_len] + ("..." if len(s) > max_len else "")

def filter_text(text, max_len=400, head_lines=8):
    """Reduce raw-text output (stdout/API-bodies) to the head-window."""
    lines = text.splitlines()[:head_lines]
    s = "\n".join(lines)
    return s[:max_len] + ("..." if len(s) > max_len else "")

if __name__ == "__main__":
    # the CLI: echo '{...}' | context-filter.py --keys a,b --max 5
    import argparse
    ap = argparse.ArgumentParser()
    ap.add_argument("--keys", default="")
    ap.add_argument("--max", type=int, default=10)
    ap.add_argument("--maxlen", type=int, default=400)
    a = ap.parse_args()
    raw = sys.stdin.read()
    try:
        data = json.loads(raw)
        # the auto-descend: unwrap the single-key wrapper ({"data": [...]} → the list!)
        if isinstance(data, dict) and len(data) == 1:
            inner = list(data.values())[0]
            if isinstance(inner, (list, dict)):
                data = inner
        print(filter_json(data, [k.strip() for k in a.keys.split(",") if k], a.max, a.maxlen))
    except Exception:
        print(filter_text(raw, a.maxlen))
