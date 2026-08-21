#!/usr/bin/env python3
"""CIRCUIT-BREAKER — the deterministic loop-guard: hashes the tool-payloads, hard-halts on 3x identical-failures, tracks the budgets.
The Layer: the doom-loop-prevention + the cost-caps (the founder's runtime-safety!)."""
import hashlib, json, os, datetime, subprocess

STATE = "/opt/data/profiles/nura/cron/output/circuit-breaker.json"
os.makedirs(os.path.dirname(STATE), exist_ok=True)

def load_state():
    if os.path.exists(STATE):
        try:
            return json.load(open(STATE))
        except Exception:
            return {"failures": {}, "budgets": {}}
    return {"failures": {}, "budgets": {}}

def save_state(s):
    with open(STATE, "w") as f:
        json.dump(s, f)

def check(action_hash, stderr_hash, budget_id="default"):
    """Register an action-failure; return HALT if the same payload+stderr repeats 3x."""
    s = load_state()
    key = f"{action_hash}:{stderr_hash}"
    s["failures"][key] = s["failures"].get(key, 0) + 1
    count = s["failures"][key]
    # the budget-check
    budget = s["budgets"].get(budget_id, {"tokens": 0, "calls": 0})
    budget["calls"] += 1
    s["budgets"][budget_id] = budget
    save_state(s)
    if count >= 3:
        return f"HALT: the identical-failure repeated {count}x ({key[:40]}...) — the loop-guard tripped!"
    if budget["calls"] > 200:
        return f"HALT: the budget-call-cap exceeded ({budget['calls']}) for {budget_id}!"
    return f"ok ({count}x)"

def log_failure(cmd):
    """The cron-facing helper: hash the command + the stderr, run the guard."""
    action_hash = hashlib.sha256(cmd.encode()).hexdigest()[:16]
    r = subprocess.run(cmd, shell=True, capture_output=True, text=True, timeout=30)
    stderr_hash = hashlib.sha256(r.stderr.encode()).hexdigest()[:16] if r.stderr else "clean"
    verdict = check(action_hash, stderr_hash)
    if verdict.startswith("HALT"):
        print(f"⛔ {verdict}")
        print(f"   cmd: {cmd[:90]}")
    return verdict

if __name__ == "__main__":
    # the self-test with the demo-failure!
    print(log_failure("echo 'demo-failure-xyz' 1>&2; exit 1"))
    print(log_failure("echo 'demo-failure-xyz' 1>&2; exit 1"))
    print(log_failure("echo 'demo-failure-xyz' 1>&2; exit 1"))
