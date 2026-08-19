#!/usr/bin/env python3
"""NURA Model Router — Perplexity-style on-the-fly model selection + swarm mode.
Tier selection: classify task -> ordered candidate list (free -> fast -> accurate -> frontier).
Swarm mode: run N models in parallel, synthesize best answer (mixture-of-agents).
Doctrine: fast/accurate/free FIRST; quality never sacrificed; cost ledger."""
import json, os, re, sys, time, urllib.request, urllib.parse

ENV = "/opt/data/profiles/nura/.env"
def env(name):
    for line in open(ENV):
        if line.startswith(name + "="):
            return line.strip().split("=", 1)[1].strip("'\"")
    return None

# ---- Tier definitions (ordered: free first) ----
TIERS = {
    "free":   [("openrouter", "nvidia/nemotron-3-super-120b-a12b:free"),
               ("openrouter", "poolside/laguna-s-2.1:free")],
    "fast":   [("deepseek", "deepseek-chat"),
               ("gemini", "gemini-2.5-flash")],
    "accurate":[("deepseek", "deepseek-reasoner"),
               ("gemini", "gemini-2.5-pro")],
    "frontier":[("gemini", "gemini-2.5-pro"),
               ("anthropic", "claude-sonnet-4.6")],
}
VISION_LANES = ["nemotron-nano-12b-v2-vl:free", "gemini-2.5-flash", "gemini-2.5-pro"]

# ---- Classification heuristics ----
CLINICAL = ["patient", "diagnos", "icd", "hcc", "raf", "soap", "chart", "medication", "lab", "fda", "symptom", "dose", "prescri"]
RESEARCH = ["research", "literature", "paper", "study", "evidence", "compare", "analyze", "why", "explain", "mechanism", "review"]
CODE = ["code", "bug", "function", "api", "deploy", "docker", "script", "error", "python", "json", "yaml"]
VISION = ["image", "photo", "screenshot", "ocr", "picture", "scan", "diagram", "x-ray", "fax"]

def classify(query):
    q = query.lower()
    tags = []
    if any(k in q for k in VISION): tags.append("vision")
    if re.search(r"\b(patient|diagnos|icd|hcc|soap|chart|medication|lab|fda|symptom|dose|prescri|clinical)\b", q): tags.append("clinical")
    if re.search(r"\bRAF\b", query): tags.append("clinical")  # uppercase RAF = risk-adjustment code
    if any(k in q for k in RESEARCH): tags.append("research")
    if any(k in q for k in CODE): tags.append("code")
    if len(q) > 600: tags.append("long")
    if q.count("?") >= 2 or len(q) > 200: tags.append("complex")
    return tags

def route(query):
    tags = classify(query)
    tier = "free"
    if "clinical" in tags or "complex" in tags or "long" in tags:
        tier = "accurate" if ("research" in tags or "clinical" in tags) else "fast"
    if "vision" in tags:
        return {"mode": "vision", "lanes": VISION_LANES, "tags": tags, "tier": "vision"}
    return {"mode": "llm", "tiers": [tier] + [t for t in ["fast", "accurate", "frontier"] if t != tier],
            "tags": tags, "tier": tier}

# ---- API callers ----
def call_openrouter(model, prompt, key):
    payload = {"model": model, "max_tokens": 800, "messages": [{"role": "user", "content": prompt}]}
    req = urllib.request.Request("https://openrouter.ai/api/v1/chat/completions",
        data=json.dumps(payload).encode(),
        headers={"Authorization": f"Bearer {key}", "Content-Type": "application/json"}, method="POST")
    with urllib.request.urlopen(req, timeout=60) as r:
        return json.loads(r.read())["choices"][0]["message"]["content"]

def call_deepseek(model, prompt, key):
    payload = {"model": model, "max_tokens": 800, "messages": [{"role": "user", "content": prompt}]}
    req = urllib.request.Request("https://api.deepseek.com/chat/completions",
        data=json.dumps(payload).encode(),
        headers={"Authorization": f"Bearer {key}", "Content-Type": "application/json"}, method="POST")
    with urllib.request.urlopen(req, timeout=60) as r:
        return json.loads(r.read())["choices"][0]["message"]["content"]

def call_gemini(model, prompt, key):
    payload = {"contents": [{"parts": [{"text": prompt}]}]}
    req = urllib.request.Request(
        f"https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent?key={key}",
        data=json.dumps(payload).encode(), headers={"Content-Type": "application/json"}, method="POST")
    with urllib.request.urlopen(req, timeout=60) as r:
        return json.loads(r.read())["candidates"][0]["content"]["parts"][0]["text"]

CALLERS = {"openrouter": call_openrouter, "deepseek": call_deepseek, "gemini": call_gemini,
           "anthropic": lambda m, p, k: (_ for _ in ()).throw(RuntimeError("anthropic key pending"))}

def run(prompt, tier="free", n=2):
    """Run prompt across up to n lanes in the tier (swarm) — parallel, best-of via synthesis."""
    lanes = []
    for t in [tier] + [x for x in ["fast", "accurate", "frontier"] if x != tier]:
        for prov, model in TIERS[t]:
            lanes.append((prov, model))
        if len(lanes) >= n: break
    results = []
    for prov, model in lanes[:n]:
        try:
            key = env("OPENROUTER_API_KEY" if prov == "openrouter" else
                      "DEEPSEEK_API_KEY" if prov == "deepseek" else "GOOGLE_API_KEY" if prov == "gemini" else "ANTHROPIC_API_KEY")
            t0 = time.time()
            out = CALLERS[prov](model, prompt, key)
            res = {"model": f"{prov}/{model}", "latency_s": round(time.time() - t0, 1),
                   "len": len(out), "text": out}
            results.append(res)
            log_ledger({"query": prompt, "tier": tier, "model": res["model"], "query_len": len(prompt),
                        "latency_s": res["latency_s"], "len": res["len"], "est_cost_usd": 0.0, "mode": "swarm"})
        except Exception as e:
            results.append({"model": f"{prov}/{model}", "error": str(e)[:80]})
    return results

def swarm(prompt, n=2, tier="fast"):
    """Swarm: parallel answers -> synthesis (DeepSeek) -> final."""
    results = run(prompt, tier=tier, n=n)
    ok = [r for r in results if "text" in r]
    if not ok:
        return {"answers": results, "final": None, "error": "no lanes succeeded"}
    if len(ok) == 1:
        return {"answers": results, "final": ok[0]["text"], "synthesized": False}
    comb = "\n\n".join(f"[{r['model']}]\n{r['text'][:1200]}" for r in ok)
    synth = f"Below are {len(ok)} candidate answers from different models. Produce ONE consolidated, accurate answer (no meta-commentary, no headers).\n\n{comb}"
    key = env("DEEPSEEK_API_KEY")
    try:
        final = call_deepseek("deepseek-chat", synth, key)
    except Exception as e:
        final = ok[0]["text"] + f"\n\n[synthesis failed: {str(e)[:60]}]"
    return {"answers": results, "final": final, "synthesized": len(ok) > 1}

def log_ledger(entry):
    """Cost/usage ledger: CSV (always) + Perfex expenses (when PERFEX_API_TOKEN present + reachable)."""
    import csv, hashlib, datetime
    ref = hashlib.sha1(f"{entry.get('query','')[:64]}|{entry.get('tier','')}|{entry.get('model','')}".encode()).hexdigest()[:12]
    row = {"ts": datetime.datetime.utcnow().isoformat(), "ref": ref, "tier": entry.get("tier", ""),
           "model": entry.get("model", ""), "query_len": entry.get("query_len", 0),
           "latency_s": entry.get("latency_s", 0), "chars": entry.get("len", 0),
           "est_cost_usd": entry.get("est_cost_usd", 0.0), "mode": entry.get("mode", "single")}
    os.makedirs("/opt/data/profiles/nura/data/ledger", exist_ok=True)
    path = "/opt/data/profiles/nura/data/ledger/model-routing.csv"
    new = not os.path.exists(path)
    with open(path, "a") as f:
        w = csv.DictWriter(f, fieldnames=list(row.keys()))
        if new: w.writeheader()
        w.writerow(row)
    # Perfex mirror (best-effort; requires token + reachable base)
    pbase = env("PERFEX_BASE_URL") or "https://195.35.32.113/api"
    ptok = env("PERFEX_API_TOKEN")
    if ptok and pbase:
        try:
            payload = {"expense_name": f"AI {row['tier']} {row['model']}", "amount": row["est_cost_usd"],
                       "date": row["ts"][:10], "note": json.dumps(row)}
            req = urllib.request.Request(pbase + "/api/expenses", data=json.dumps(payload).encode(),
                                         headers={"x-api-key": ptok, "Content-Type": "application/json"}, method="POST")
            with urllib.request.urlopen(req, timeout=10) as r:
                print(f"[ledger] perfex expense -> {r.status}")
        except Exception as e:
            print(f"[ledger] perfex skipped: {str(e)[:70]}")
    else:
        print(f"[ledger] perfex pending (token/base) — CSV only: {path}")
    return ref

if __name__ == "__main__":
    q = sys.argv[1] if len(sys.argv) > 1 else "Summarize the key risks in Medicare Advantage RAF coding"
    mode = sys.argv[2] if len(sys.argv) > 2 else "route"
    if mode == "route":
        r = route(q)
        print(json.dumps({"query_len": len(q), **r}, indent=1))
    elif mode == "swarm":
        n = int(sys.argv[3]) if len(sys.argv) > 3 else 2
        out = swarm(q, n=n)
        print(json.dumps({"models": [a.get("model") for a in out["answers"]],
                          "synthesized": out.get("synthesized"), "final_len": len(out.get("final") or "")}, indent=1))
        print("\nFINAL:\n", (out.get("final") or "")[:500])
