#!/usr/bin/env python3
"""NURA Free Lane Health — probes free inference lanes, updates free-lanes.json.
Silent when all healthy; prints only changes (degraded/recovered/new). Stdlib only."""
import datetime, json, os, sys, urllib.request

STATE = "/opt/data/profiles/nura/data/lessons/free-lanes.json"
os.makedirs(os.path.dirname(STATE), exist_ok=True)
TEST = [{"role": "user", "content": "Reply with exactly: OK"}]

def read_env(name):
    for line in open("/opt/data/profiles/nura/.env"):
        if line.startswith(name + "="):
            return line.strip().split("=", 1)[1].strip("'\"")
    return None

def probe_openrouter(model, key, timeout=45):
    req = urllib.request.Request(
        "https://openrouter.ai/api/v1/chat/completions",
        data=json.dumps({"model": model, "messages": TEST, "max_tokens": 8}).encode(),
        headers={"Authorization": f"Bearer {key}", "Content-Type": "application/json"}, method="POST")
    with urllib.request.urlopen(req, timeout=timeout) as r:
        d = json.loads(r.read())
        return bool(d.get("choices"))

def main():
    key = read_env("OPENROUTER_API_KEY")
    lanes = {
        "nemotron-120b": "nvidia/nemotron-3-super-120b-a12b:free",
        "nemotron-550b": "nvidia/nemotron-3-ultra-550b-a55b:free",
        "laguna-fast": "poolside/laguna-s-2.1:free",
        "gemma-large": "google/gemma-4-31b-it:free",
        "north-code": "cohere/north-mini-code:free",
    }
    state = {}
    if os.path.exists(STATE):
        state = json.load(open(STATE))
    now = datetime.datetime.utcnow().isoformat(timespec="minutes")
    changes = []
    for name, model in lanes.items():
        prev = state.get(name, {})
        try:
            if not key:
                raise RuntimeError("no key")
            ok = probe_openrouter(model, key)
            if ok:
                new = {"healthy": True, "checked_at": now, "model": model}
                if prev.get("healthy") is not True:
                    changes.append(f"✓ {name} RECOVERED ({model})")
            else:
                new = {"healthy": False, "checked_at": now, "model": model, "error": "empty response"}
                if prev.get("healthy") is not False:
                    changes.append(f"✗ {name} DEGRADED ({model})")
        except Exception as e:
            new = {"healthy": False, "checked_at": now, "model": model, "error": str(e)[:80]}
            if prev.get("healthy") is not False:
                changes.append(f"✗ {name} DEGRADED ({model}): {str(e)[:60]}")
        state[name] = new
    json.dump(state, open(STATE, "w"), indent=1)
    if changes:
        print("FREE LANE STATUS " + datetime.date.today().isoformat())
        for c in changes:
            print(" " + c)
        dead = [k for k, v in state.items() if not v.get("healthy")]
        if dead:
            print(f"  {len(dead)} degraded: {', '.join(dead)} — rotation will skip; paid fallback per skill.")

if __name__ == "__main__":
    main()
