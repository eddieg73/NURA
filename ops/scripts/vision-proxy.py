#!/usr/bin/env python3
"""NURA Vision Proxy — routes image analysis to the best vision LLM via OpenRouter.
DeepSeek has no vision; this is the vision lane. Usage:
  vision-proxy.py <image-path> [lane] [prompt]
Lanes: free (default, gemma-4-31b-it:free) -> free-vl (nemotron-nano-12b-v2-vl:free)
       -> frontier (google/gemini-2.5-pro) -> opus (anthropic/claude-opus-5)
Quality gate: caller must verify output; clinical images NEVER diagnosed by this lane."""
import base64, json, os, sys, urllib.request

LANES = {
    "free": "google/gemma-4-31b-it:free",
    "free-vl": "nvidia/nemotron-nano-12b-v2-vl:free",
    "free-reasoning": "nvidia/nemotron-3-nano-omni-30b-a3b-reasoning:free",
    "frontier": "google/gemini-2.5-pro",
    "opus": "anthropic/claude-opus-5",
}

def read_env(name):
    for line in open("/opt/data/profiles/nura/.env"):
        if line.startswith(name + "="):
            return line.strip().split("=", 1)[1].strip("'\"")
    return None

def main():
    path = sys.argv[1]
    lane = sys.argv[2] if len(sys.argv) > 2 else "free"
    prompt = sys.argv[3] if len(sys.argv) > 3 else "Describe this image in detail. If it contains text, transcribe it exactly."
    model = LANES.get(lane)
    if not model:
        print("unknown lane", lane, list(LANES)); sys.exit(1)
    key = read_env("OPENROUTER_API_KEY")
    if not key:
        print("OPENROUTER_API_KEY missing"); sys.exit(1)
    mime = "image/png" if path.lower().endswith(".png") else ("image/jpeg" if path.lower().endswith((".jpg", ".jpeg")) else "image/webp")
    b64 = base64.b64encode(open(path, "rb").read()).decode()
    payload = {"model": model, "max_tokens": 1024, "messages": [{"role": "user", "content": [
        {"type": "text", "text": prompt},
        {"type": "image_url", "image_url": {"url": f"data:{mime};base64,{b64}"}}]}]}
    req = urllib.request.Request("https://openrouter.ai/api/v1/chat/completions",
                                 data=json.dumps(payload).encode(),
                                 headers={"Authorization": f"Bearer {key}", "Content-Type": "application/json"},
                                 method="POST")
    with urllib.request.urlopen(req, timeout=120) as r:
        d = json.loads(r.read())
    print(d["choices"][0]["message"]["content"])

if __name__ == "__main__":
    main()
