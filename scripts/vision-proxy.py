#!/usr/bin/env python3
"""NURA Vision Proxy — routes image analysis to the best vision LLM via OpenRouter.
DeepSeek has no vision; this is the vision lane. Usage:
  vision-proxy.py <image-path> [lane] [prompt]
Lanes: free-vl (DEFAULT, verified: nvidia/nemotron-nano-12b-v2-vl:free)
       -> free-reasoning (nvidia/nemotron-3-nano-omni-30b-a3b-reasoning:free)
       -> gemini (direct API, google/gemini-2.5-flash — GOOGLE_API_KEY, verified)
       -> gemini-pro (direct API, gemini-2.5-pro)
Auto-cascade: on 429/5xx/empty, falls through to the next lane.
REMOVED: gemma-4-31b-it:free (429 + not verified VLM) and claude-opus-5 (not in provider doctrine).
Quality gate: caller must verify output; clinical images NEVER diagnosed by this lane;
PHI images must use the local Lab VLM (never OpenRouter)."""
import base64, json, os, sys, time, urllib.request

LANES = [
    ("free-vl", "nvidia/nemotron-nano-12b-v2-vl:free"),
    ("free-reasoning", "nvidia/nemotron-3-nano-omni-30b-a3b-reasoning:free"),
    ("gemini", "gemini-2.5-flash"),
    ("gemini-pro", "gemini-2.5-pro"),
]
FALLBACKS = [m for _, m in LANES[1:]]  # cascade order after the requested lane

def read_env(name):
    for line in open("/opt/data/profiles/nura/.env"):
        if line.startswith(name + "="):
            return line.strip().split("=", 1)[1].strip("'\"")
    return None

def main():
    path = sys.argv[1]
    lane = sys.argv[2] if len(sys.argv) > 2 else "free-vl"
    prompt = sys.argv[3] if len(sys.argv) > 3 else "Describe this image in detail. If it contains text, transcribe it exactly."
    models = []
    for name, m in LANES:
        if name == lane:
            models.append(m)
            break
    models += [m for _, m in LANES if m not in models]  # cascade: rest of lanes in order
    key = read_env("OPENROUTER_API_KEY")
    if not key:
        print("OPENROUTER_API_KEY missing"); sys.exit(1)
    mime = "image/png" if path.lower().endswith(".png") else ("image/jpeg" if path.lower().endswith((".jpg", ".jpeg")) else "image/webp")
    b64 = base64.b64encode(open(path, "rb").read()).decode()
    for i, model in enumerate(models):
        try:
            if model.startswith("gemini-"):
                gkey = read_env("GOOGLE_API_KEY")
                if not gkey:
                    raise RuntimeError("GOOGLE_API_KEY missing")
                payload = {"contents": [{"parts": [
                    {"text": prompt},
                    {"inline_data": {"mime_type": mime, "data": b64}}]}]}
                req = urllib.request.Request(
                    f"https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent?key={gkey}",
                    data=json.dumps(payload).encode(),
                    headers={"Content-Type": "application/json"}, method="POST")
                with urllib.request.urlopen(req, timeout=120) as r:
                    d = json.loads(r.read())
                out = d["candidates"][0]["content"]["parts"][0]["text"]
            else:
                payload = {"model": model, "max_tokens": 1024, "messages": [{"role": "user", "content": [
                    {"type": "text", "text": prompt},
                    {"type": "image_url", "image_url": {"url": f"data:{mime};base64,{b64}"}}]}]}
                req = urllib.request.Request("https://openrouter.ai/api/v1/chat/completions",
                                             data=json.dumps(payload).encode(),
                                             headers={"Authorization": f"Bearer {key}", "Content-Type": "application/json"},
                                             method="POST")
                with urllib.request.urlopen(req, timeout=120) as r:
                    d = json.loads(r.read())
                out = d["choices"][0]["message"]["content"]
            if out and out.strip():
                print(out)
                return
            print(f"[{model}] empty output", file=sys.stderr)
        except Exception as e:
            print(f"[{model}] {type(e).__name__}: {str(e)[:120]}", file=sys.stderr)
            if i < len(models) - 1:
                time.sleep(1)
    print("ALL VISION LANES FAILED"); sys.exit(1)

if __name__ == "__main__":
    main()
