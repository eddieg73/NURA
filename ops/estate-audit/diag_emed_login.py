#!/usr/bin/env python3
"""
Diagnose why the eMedical gap audit cannot log in.

ESTABLISHED: the stored EMED_USERNAME/EMED_PASSWORD match the founder's values EXACTLY
(fingerprints f9c6085da6 / 8d330295d9). So the credential is NOT the cause. The failure is
technical. This separates the possibilities:

  1. network / DNS      - can this host reach the site at all?
  2. HTTP layer         - what status and body come back?
  3. bot wall           - is a WAF/captcha intercepting the headless browser?
  4. page contract      - are the #username / #password selectors the script uses still present?
  5. playwright         - is the browser binary actually present and launchable?

The audit output said: login blocked: login exception: TimeoutError, scanned=0.
A TimeoutError with correct credentials points at 1/3/5, not 2/4.
"""
import re
import socket
import ssl
import subprocess
import urllib.request

URL = "https://service.emedpractice.com/"
UA = ("Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
      "(KHTML, like Gecko) Chrome/124.0 Safari/537.36")

print("=" * 88)
print("1. DNS")
print("=" * 88)
try:
    infos = socket.getaddrinfo("service.emedpractice.com", 443, proto=socket.IPPROTO_TCP)
    ips = sorted({i[4][0] for i in infos})
    print(f"  resolves to: {ips}")
except Exception as e:
    print(f"  DNS FAILED: {type(e).__name__}: {e}")

print("\n" + "=" * 88)
print("2. TCP + TLS 443")
print("=" * 88)
try:
    s = socket.create_connection(("service.emedpractice.com", 443), timeout=15)
    print("  TCP connect: OK")
    ctx = ssl.create_default_context()
    tls = ctx.wrap_socket(s, server_hostname="service.emedpractice.com")
    print(f"  TLS: {tls.version()}  cipher={tls.cipher()[0]}")
    print(f"  peer CN: {dict(x[0] for x in tls.getpeercert()['subject'])}")
    tls.close()
except Exception as e:
    print(f"  FAILED: {type(e).__name__}: {e}")

print("\n" + "=" * 88)
print("3. HTTPS GET")
print("=" * 88)
body = ""
try:
    req = urllib.request.Request(URL, headers={"User-Agent": UA,
                                               "Accept": "text/html,application/xhtml+xml"})
    with urllib.request.urlopen(req, timeout=30) as r:
        body = r.read().decode("utf-8", "ignore")
        print(f"  HTTP {r.status}  bytes={len(body)}")
        print(f"  server: {r.headers.get('Server')}")
        print(f"  content-type: {r.headers.get('Content-Type')}")
        for h in ("X-Powered-By", "CF-Ray", "X-Akamai-Transformed", "Set-Cookie"):
            if r.headers.get(h):
                print(f"  {h}: {str(r.headers.get(h))[:90]}")
except Exception as e:
    print(f"  FAILED: {type(e).__name__}: {e}")

print("\n" + "=" * 88)
print("4. PAGE CONTRACT (the selectors the script depends on)")
print("=" * 88)
if body:
    t = re.search(r"<title[^>]*>(.*?)</title>", body, re.S | re.I)
    print(f"  title: {t.group(1).strip()[:90] if t else '(none)'}")
    for sel, pat in (("#username", r'id=["\']username["\']'),
                     ("#password", r'id=["\']password["\']'),
                     ("input[type=password]", r'type=["\']password["\']'),
                     ("login button text", r'(?i)>\s*log\s*in\s*<'),
                     ("aspnet viewstate", r'__VIEWSTATE'),
                     ("aspnet eventvalidation", r'__EVENTVALIDATION')):
        n = len(re.findall(pat, body))
        print(f"    {sel:<24} {n} match(es) {'OK' if n else '** MISSING **'}")
    print("\n  bot-wall markers:")
    found = False
    for m in ("captcha", "recaptcha", "hcaptcha", "cloudflare", "cf-challenge",
              "incapsula", "imperva", "akamai", "access denied", "blocked",
              "unusual traffic", "request unsuccessful"):
        n = len(re.findall(m, body, re.I))
        if n:
            print(f"    {m}: {n}")
            found = True
    if not found:
        print("    none detected in the returned HTML")

print("\n" + "=" * 88)
print("5. PLAYWRIGHT READINESS")
print("=" * 88)
PW = "/opt/data/profiles/nura/lazy-packages"
print(f"  PLAYWRIGHT_BROWSERS_PATH candidates:")
for p in (PW + "/ms-playwright", "/root/.cache/ms-playwright",
          "/opt/data/profiles/nura/home/.cache/ms-playwright"):
    import os
    if os.path.isdir(p):
        subs = os.listdir(p)[:6]
        print(f"    {p}: EXISTS  {subs}")
    else:
        print(f"    {p}: absent")
try:
    r = subprocess.run(["/opt/hermes/.venv/bin/python3", "-c",
                        "import playwright; print('playwright', playwright.__version__ if hasattr(playwright,'__version__') else 'imported')"],
                       capture_output=True, text=True, timeout=40)
    print(f"  python import: {(r.stdout or r.stderr).strip()[:120]}")
except Exception as e:
    print(f"  import check failed: {e}")
