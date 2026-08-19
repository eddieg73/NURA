import json, urllib.request, urllib.error
def _env(name):
    for line in open("/opt/data/profiles/nura/.env"):
        if line.startswith(name + "="):
            return line.strip().split("=", 1)[1].strip("'\"")
    return ""
key = _env("OPENROUTER_API_KEY")
body = {"model": "google/gemma-4-31b-it:free",
        "messages": [{"role": "user", "content": "Say OK"}], "max_tokens": 10}
req = urllib.request.Request("https://openrouter.ai/api/v1/chat/completions",
    data=json.dumps(body).encode(),
    headers={"Authorization": f"Bearer {key}", "Content-Type": "application/json"})
try:
    r = urllib.request.urlopen(req, timeout=60)
    print("FREE MODEL OK:", json.loads(r.read())["choices"][0]["message"]["content"][:40])
except urllib.error.HTTPError as e:
    print("HTTP", e.code, e.read()[:200])
except Exception as e:
    print("ERR", str(e)[:120])
