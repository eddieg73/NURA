#!/usr/bin/env python3
"""NURA Tools API — derm triage + face verify + metar, exposed on the tailnet for the phone/glasses bridge.
POST /derm {image_path} · POST /verify {image_path, name?} · GET /metar · GET /health"""
import json, subprocess, sys
from flask import Flask, request, jsonify

sys.path.insert(0, "/opt/data/scripts")
app = Flask(__name__)

def _env(name):
    for line in open("/opt/data/profiles/nura/.env"):
        if line.startswith(name + "="):
            return line.strip().split("=", 1)[1].strip("'\"")
    return ""

def llm(system, user, max_tokens=400):
    import urllib.request
    # LOCAL FIRST (sovereign, free, no rate limits): Lab Ollama via the tunnel
    try:
        body = json.dumps({"model": "qwen2.5:3b",
                           "prompt": f"{system}\n\n{user}", "stream": False}).encode()
        req = urllib.request.Request("http://127.0.0.1:11434/api/generate", data=body,
                                     headers={"Content-Type": "application/json"})
        d = json.loads(urllib.request.urlopen(req, timeout=120).read())
        return {"text": d.get("response", "").strip()}
    except Exception:
        pass
    # fallback: OpenRouter free lane
    key = _env("OPENROUTER_API_KEY") or _env("OPENROUTER_OR_KEY")
    body = {"model": "google/gemma-4-31b-it:free",
            "messages": [{"role": "system", "content": system},
                         {"role": "user", "content": user}],
            "max_tokens": max_tokens, "temperature": 0.3}
    req = urllib.request.Request("https://openrouter.ai/api/v1/chat/completions",
        data=json.dumps(body).encode(),
        headers={"Authorization": f"Bearer {key}", "Content-Type": "application/json"})
    try:
        r = urllib.request.urlopen(req, timeout=60)
        d = json.loads(r.read())
        return {"text": d["choices"][0]["message"]["content"].strip()}
    except Exception as e:
        return {"error": str(e)[:120]}

@app.get("/health")
def health():
    lanes = {}
    try:
        urllib.request.urlopen("http://127.0.0.1:11434/api/tags", timeout=5)
        lanes["llm"] = "ok"
    except Exception:
        lanes["llm"] = "down"
    return jsonify({"status": "ok", "tools": ["derm", "verify", "metar", "dx", "synthesis"], "lanes": lanes})

@app.post("/dx")
def dx():
    d = request.get_json(force=True) or {}
    case = {"age": d.get("age", 50), "sex": d.get("sex", "unknown"),
            "presentation": d.get("presentation", ""),
            "findings": d.get("findings", ""), "labs": d.get("labs", "")}
    r = subprocess.run(["python3", "/opt/data/scripts/nura-dx.py", json.dumps(case)],
                       capture_output=True, text=True, timeout=600)
    return jsonify({"text": r.stdout.strip()})

@app.post("/synthesis")
def synthesis():
    d = request.get_json(force=True) or {}
    r = subprocess.run(["python3", "/opt/data/scripts/nura-clinical-synthesis.py"], input=json.dumps(d),
                       capture_output=True, text=True, timeout=1800)
    return jsonify({"text": r.stdout.strip()[-3000:]})

@app.post("/scribe")
def scribe():
    """The ambient scribe: the dictation (text now; audio next) → the structured
    clinical note via Med42 → the FHIR-shaped output with the review label."""
    d = request.get_json(force=True) or {}
    text = d.get("text", "")
    if not text:
        return jsonify({"error": "text required"}), 400
    prompt = ("You are NURA, the ambient medical scribe for a licensed PA. Turn the raw dictation "
              "into a structured clinical note: the SOAP format (Subjective/Objective/Assessment/Plan) "
              "from what's said, flag UNCERTAIN parts with [review], list the missing elements, "
              "and end with exactly 'DRAFT — PROVIDER APPROVAL REQUIRED.' "
              "Never invent findings. JSON: {\"soap\": {\"s\":\"\",\"o\":\"\",\"a\":\"\",\"p\":\"\"}, "
              "\"review_flags\": [], \"missing\": []}\n\nDICTATION:\n" + text)
    try:
        body = json.dumps({"model": "med42", "prompt": prompt, "stream": False,
                           "options": {"num_predict": 900, "temperature": 0.2}}).encode()
        req = urllib.request.Request("http://127.0.0.1:11434/api/generate", data=body,
                                     headers={"Content-Type": "application/json"})
        r = urllib.request.urlopen(req, timeout=1500)
        out = json.loads(r.read()).get("response", "").strip()
    except Exception as e:
        out = f"[scribe unavailable: {str(e)[:80]}]"
    return jsonify({"note": out})

@app.get("/dsh")
def dsh():
    """Delegate a task to the DeepSeek Harness (headless, sovereign lane)."""
    goal = request.args.get("goal", "")
    if not goal:
        return jsonify({"error": "goal param required"}), 400
    dsh_dir = "/opt/data/deepseek-harness-study/deepseek-harness"
    env = {"DEEPSEEK_BASE_URL": "http://127.0.0.1:11434/v1", "DSH_HOME": "/opt/data/dsh-home",
           "PATH": "/usr/local/bin:/usr/bin:/bin"}
    try:
        r = subprocess.run(["pnpm", "dsh", "--profile", "headless", goal],
                           cwd=dsh_dir, env=env, capture_output=True, text=True, timeout=900)
        return jsonify({"text": (r.stdout or r.stderr).strip()[-2500:]})
    except Exception as e:
        return jsonify({"error": f"dsh run failed: {str(e)[:120]}"})

@app.get("/harness")
def harness():
    """Kick the sovereign coding agent (auto mode)."""
    goal = request.args.get("goal", "")
    if not goal:
        return jsonify({"error": "goal param required"}), 400
    r = subprocess.run(["python3", "/opt/data/nura-harness/nura-harness.py", goal, "--auto"],
                       capture_output=True, text=True, timeout=1200)
    return jsonify({"text": r.stdout.strip()[-2000:]})

@app.post("/derm")
def derm():
    d = request.get_json(force=True) or {}
    p = d.get("image_path")
    if not p:
        return jsonify({"error": "image_path required"}), 400
    r = subprocess.run(["python3", "/opt/data/scripts/derm-triage.py", p],
                       capture_output=True, text=True, timeout=120)
    try:
        return jsonify(json.loads(r.stdout))
    except json.JSONDecodeError:
        return jsonify({"error": r.stderr[-200:]})

@app.post("/verify")
def verify():
    d = request.get_json(force=True) or {}
    p = d.get("image_path")
    if not p:
        return jsonify({"error": "image_path required"}), 400
    args = ["python3", "/opt/data/scripts/face-verify.py", p]
    if d.get("name"):
        args.append(d["name"])
    r = subprocess.run(args, capture_output=True, text=True, timeout=180)
    try:
        return jsonify(json.loads(r.stdout))
    except json.JSONDecodeError:
        return jsonify({"error": r.stderr[-200:]})

@app.get("/metar")
def metar():
    r = subprocess.run(["python3", "/opt/data/scripts/local-metar.py"],
                       capture_output=True, text=True, timeout=60)
    return jsonify({"text": r.stdout})

@app.post("/alexa")
def alexa_ep():
    """Alexa bridge endpoint: {text} -> Hermes reply (LLM lane). Tailnet-ready now;
    door-routing-ready for api.nuratech.ai/hermes/alexa (the Lambda's public target)."""
    d = request.get_json(force=True) or {}
    text = (d.get("text") or "").strip()[:500]
    if not text:
        return jsonify({"reply": "I didn't catch that."})
    sys = ("You are Hermes/NURA on Alexa. Answer the founder's request in 2-3 spoken sentences, "
           "plain speech, no markdown. Clinical requests: decision-support only, provider review, "
           "never a diagnosis as fact.")
    if text in ("status", "fleet status"):
        out = llm(sys, "Give a one-line fleet status: 3 VPS healthy, croms pinned, models serving.")
    elif text == "weather":
        out = {"text": subprocess.run(["python3", "/opt/data/scripts/local-metar.py"],
                                      capture_output=True, text=True, timeout=60).stdout[:300]}
    else:
        out = llm(sys, text)
    if isinstance(out, dict) and "error" in out:
        return jsonify({"reply": "The NURA link is busy — try again shortly."})
    reply = out.get("text", "Acknowledged.") if isinstance(out, dict) else str(out)
    return jsonify({"reply": reply[:800]})

if __name__ == "__main__":
    app.run(host="127.0.0.1", port=8095)
