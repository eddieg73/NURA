#!/usr/bin/env python3
"""
Verify the greenlet ABI state, which the Aug-26 failure named directly:

  playwright not importable ... : No module named 'greenlet._greenlet'

The skill requires greenlet 3.2.4 built for cp313:
  "greenlet MUST be 3.2.4 with --python-version 3.13 (3.5.4 ships source-only; 3.2.4 default wheel =
   cp311 -- wrong ABI; the cp313 wheel is the fix)"
Installed is 3.5.5. Check whether its C extension actually loads under this interpreter, and whether
the async playwright entrypoint imports end to end.
"""
import os
import subprocess
import sys

PP = "/opt/data/profiles/nura/python-packages"
sys.path.insert(0, PP)

print("=" * 88)
print("INTERPRETER")
print("=" * 88)
print(f"  running under : {sys.executable}")
print(f"  version       : {sys.version.split()[0]}")
print(f"  cache tag     : {sys.implementation.cache_tag}")

print("\n" + "=" * 88)
print("GREENLET C-EXTENSION LOAD (the exact Aug-26 failure)")
print("=" * 88)
try:
    import greenlet
    print(f"  import greenlet        : OK  version={getattr(greenlet,'__version__','?')}")
    print(f"  module file            : {greenlet.__file__}")
except Exception as e:
    print(f"  import greenlet        : FAIL {type(e).__name__}: {e}")

try:
    import greenlet._greenlet as g  # noqa
    print(f"  import greenlet._greenlet : OK -> {g.__file__}")
except Exception as e:
    print(f"  import greenlet._greenlet : FAIL {type(e).__name__}: {e}")

# what .so files exist and do they match this interpreter's ABI tag?
print("\n  installed greenlet binaries:")
import glob
for p in sorted(glob.glob(os.path.join(PP, "greenlet*", "*.so")) +
                glob.glob(os.path.join(PP, "greenlet*", "**", "*.so"), recursive=True)):
    print(f"    {os.path.basename(p)}")

print("\n" + "=" * 88)
print("PLAYWRIGHT ASYNC CHAIN")
print("=" * 88)
try:
    from playwright.async_api import async_playwright  # noqa
    print("  from playwright.async_api import async_playwright : OK")
except Exception as e:
    print(f"  FAIL {type(e).__name__}: {e}")

print("\n" + "=" * 88)
print("SUBPROCESS PROBE (the way cron actually invokes it)")
print("=" * 88)
code = (
    "import sys; sys.path.insert(0,%r)\n"
    "import greenlet, greenlet._greenlet\n"
    "from playwright.async_api import async_playwright\n"
    "print('CHAIN OK', greenlet.__version__)\n" % PP)
r = subprocess.run(["/opt/hermes/.venv/bin/python3", "-c", code],
                   capture_output=True, text=True, timeout=60)
print(f"  stdout: {(r.stdout or '').strip()[:200]}")
print(f"  stderr: {(r.stderr or '').strip()[-300:]}")
print(f"  exit  : {r.returncode}")

print("\n" + "=" * 88)
print("THE eMEDICAL JOB'S OWN VIEW")
print("=" * 88)
r = subprocess.run(["/opt/hermes/.venv/bin/python3",
                    "/opt/data/profiles/nura/scripts/emed-gap-audit.py", "--selftest"],
                   capture_output=True, text=True, timeout=180,
                   env={**os.environ,
                        "PYTHONPATH": PP,
                        "PLAYWRIGHT_BROWSERS_PATH": "/opt/data/profiles/nura/.cache/ms-playwright"})
print(f"  exit: {r.returncode}")
print(f"  stdout: {(r.stdout or '')[:900]}")
if r.stderr:
    print(f"  stderr: {r.stderr[-600:]}")
