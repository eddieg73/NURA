#!/usr/bin/env python3
"""
Locate playwright and compare against what emed-gap-audit.py expects.

Two live problems found so far:
  * `#username` does not exist on the login page (the script fills it -> would fail)
  * `import playwright` fails in /opt/hermes/.venv

The script sets PLAYWRIGHT_BROWSERS_PATH from a constant and injects a PYTHONPATH at run time.
If the interpreter it runs under genuinely lacks playwright, the failure is an IMPORT error, not a
login TimeoutError -- so establish which one the job actually hits.
"""
import os
import re
import subprocess

SCRIPT = "/opt/data/profiles/nura/scripts/emed-gap-audit.py"
src = open(SCRIPT, errors="ignore").read()

print("=" * 88)
print("WHAT THE SCRIPT EXPECTS")
print("=" * 88)
for pat, label in ((r'PW_BROWSERS\s*=\s*["\']([^"\']+)', "PW_BROWSERS"),
                   (r'PYTHONPATH\s*[=:]\s*["\']?([^"\'\n]+)', "PYTHONPATH hint"),
                   (r'LOGIN_USERNAME\s*=\s*["\']([^"\']+)', "LOGIN_USERNAME selector"),
                   (r'LOGIN_PASSWORD\s*=\s*["\']([^"\']+)', "LOGIN_PASSWORD selector"),
                   (r'LOGIN_BUTTON\s*=\s*["\']([^"\']+)', "LOGIN_BUTTON selector")):
    m = re.search(pat, src)
    print(f"  {label:<24}: {m.group(1) if m else '(not found)'}")

m = re.search(r'PYTHONPATH.*?["\']([^"\']*site-packages[^"\']*)', src, re.S)
if m:
    print(f"  PYTHONPATH site-packages: {m.group(1)}")

print("\n  relevant lines 325-360:")
for i, ln in enumerate(src.splitlines()[324:360], 325):
    print(f"    {i:>4}: {ln}")

print("\n" + "=" * 88)
print("WHERE IS PLAYWRIGHT ACTUALLY INSTALLED?")
print("=" * 88)
cands = [
    "/opt/hermes/.venv/lib/python3.13/site-packages/playwright",
    "/opt/hermes/.venv/lib/python3.12/site-packages/playwright",
    "/opt/data/profiles/nura/lazy-packages/playwright",
]
for c in cands:
    print(f"  {c}: {'EXISTS' if os.path.exists(c) else 'absent'}")

r = subprocess.run(["find", "/opt", "-maxdepth 7", "-name", "playwright", "-type", "d"],
                   capture_output=True, text=True, timeout=90)
print("\n  find results (playwright dirs):")
for line in (r.stdout or "").splitlines()[:12]:
    print(f"    {line}")

r = subprocess.run(["find", "/opt", "/root", "-maxdepth 8", "-name", "ms-playwright", "-type", "d"],
                   capture_output=True, text=True, timeout=90)
print("\n  find results (ms-playwright browser dirs):")
print(f"    {(r.stdout or '').strip() or '(NONE FOUND — no browser binaries installed)'}")

print("\n" + "=" * 88)
print("INTERPRETER PROBES")
print("=" * 88)
for py in ("/opt/hermes/.venv/bin/python3", "/usr/bin/python3", "python3"):
    r = subprocess.run([py, "-c", "import playwright, sys; print('OK', sys.executable)"],
                       capture_output=True, text=True, timeout=40)
    status = (r.stdout or "").strip() or (r.stderr or "").strip().splitlines()[-1][:110]
    print(f"  {py:<34} {status}")

print("\n" + "=" * 88)
print("VERDICT LOGIC")
print("=" * 88)
have_pw = any(os.path.exists(c) for c in cands)
have_browser = bool((subprocess.run(["find", "/opt", "/root", "-maxdepth 8", "-name", "ms-playwright",
                                     "-type", "d"], capture_output=True, text=True).stdout or "").strip())
print(f"  playwright package dir present : {have_pw}")
print(f"  browser binaries present       : {have_browser}")
if not have_browser:
    print("  => The script cannot launch a browser at all. A login attempt fails before reaching")
    print("     eMedical, which is consistent with an exception, not a page-level timeout.")
print("  NOTE: the recorded failure was `login exception: TimeoutError`. Verify which exception")
print("  the job ACTUALLY raises now before assuming; do not act on the old message alone.")
