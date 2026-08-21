#!/usr/bin/env python3
"""TRAJECTORY-EVAL-BENCH — the CI/CD-for-agents: the deterministic task-suite with the 3-axis metrics (success · steps · cost!)."""
import subprocess, time, json, os, datetime

BENCH = "/opt/data/profiles/nura/cron/output/eval-bench.json"
os.makedirs(os.path.dirname(BENCH), exist_ok=True)

# the deterministic tasks (the NURA-relevant!)
TASKS = [
    {"name": "docsgpt-health", "cmd": "curl -s -m 8 -o /dev/null -w '%{http_code}' http://72.61.71.211:7091/api/health", "expect": "200"},
    {"name": "ollama-tags", "cmd": "curl -s -m 8 -o /dev/null -w '%{http_code}' http://72.60.163.140:11434/api/tags", "expect": "200"},
    {"name": "tunnel-11434", "cmd": "python3 -c \"import socket; s=socket.socket(); s.settimeout(2); s.connect(('127.0.0.1',11434)); print('open')\"", "expect": "open"},
    {"name": "mesh-lab", "cmd": "ssh -o BatchMode=yes -o ConnectTimeout=6 -i ~/.ssh/id_nura_clean root@72.60.163.140 'echo mesh-ok'", "expect": "mesh-ok"},
    {"name": "firecrawl-lane", "cmd": "grep -c 'FIRECRAWL_API_KEY=' /opt/data/profiles/nura/.env", "expect": "1"},
]

def run():
    results = []
    for t in TASKS:
        start = time.time()
        try:
            r = subprocess.run(t["cmd"], shell=True, capture_output=True, text=True, timeout=25)
            out = (r.stdout + r.stderr).strip()
            ok = t["expect"] in out
            results.append({"task": t["name"], "success": ok, "seconds": round(time.time() - start, 2),
                            "output": out[:80]})
        except Exception as e:
            results.append({"task": t["name"], "success": False, "seconds": round(time.time() - start, 2), "output": str(e)[:60]})
    passed = sum(1 for r in results if r["success"])
    total = len(results)
    avg_s = round(sum(r["seconds"] for r in results) / total, 2)
    print(f"🧪 EVAL-BENCH — {datetime.datetime.now().strftime('%b %d, %H:%M')}")
    print(f"· SUCCESS: {passed}/{total} · avg-step: {avg_s}s")
    for r in results:
        print(f"  {'✓' if r['success'] else '✗'} {r['task']}: {r['seconds']}s | {r['output'][:50]}")
    with open(BENCH, "w") as f:
        json.dump({"date": datetime.datetime.now().isoformat(), "passed": passed, "total": total, "results": results}, f)

if __name__ == "__main__":
    run()
