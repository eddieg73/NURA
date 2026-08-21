#!/usr/bin/env python3
"""Output redaction — replaces known secrets + token patterns with [REDACTED_SECRET].
Usage: cmd | python3 redact-secrets.py | ...   or   python3 redact-secrets.py < file
Loads KEY=VALUE pairs from the profile .env (0600) + pattern-matches common token shapes.
Never logs/echoes the secrets themselves."""
import re, sys, os

ENV_FILE = "/opt/data/profiles/nura/.env"
RED = "[REDACTED_SECRET]"

secrets = []
try:
    for line in open(ENV_FILE):
        line = line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        k, _, v = line.partition("=")
        v = v.strip().strip("'\"")
        if len(v) >= 8 and not v.startswith(("http", "/", "${", ".")):
            secrets.append(v)
except OSError:
    pass

# Token/credential shapes (pattern layer — catches things not in .env)
patterns = [
    r"sk-[A-Za-z0-9_-]{12,}",
    r"secret_[A-Za-z0-9]{20,}",
    r"rpa?_[A-Za-z0-9]{20,}",
    r"gh[pousr]_[A-Za-z0-9]{20,}",
    r"xox[baprs]-[A-Za-z0-9-]{10,}",
    r"AKIA[0-9A-Z]{16}",
    r"-----BEGIN (RSA |EC |OPENSSH )?PRIVATE KEY-----.*?-----END (RSA |EC |OPENSSH )?PRIVATE KEY-----",
    r"Bearer [A-Za-z0-9._-]{20,}",
    r"Basic [A-Za-z0-9+/=]{20,}",
    r"(?:password|passwd|secret|token|api[_-]?key|client[_-]?secret|access[_-]?key)\s*[=:]\s*[^\s,;]+",
]

def redact(text: str) -> str:
    for s in secrets:
        if s and len(s) >= 8:
            text = text.replace(s, RED)
    for p in patterns:
        text = re.sub(p, RED, text, flags=re.DOTALL)
    return text

data = sys.stdin.read() if not sys.argv[1:] else open(sys.argv[1]).read()
sys.stdout.write(redact(data))
