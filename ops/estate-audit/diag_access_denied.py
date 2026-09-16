#!/usr/bin/env python3
"""
WHY does the headless browser get "Access Denied" when curl from the same host gets the login form?

Observed:
  curl (UA Chrome/124, plain HTTP)  -> HTTP 200, 53,676 bytes, real form (#email present)
  playwright headless (UA Chrome/126) -> HTTP 200, title "Access Denied", form fields MISSING

The IP is therefore not blanket-blocked. Isolate the discriminator by varying ONE thing at a time:
  A. same UA as the working curl, headless
  B. a normal desktop UA, headless
  C. the browser's own request API (browser network stack, no JS/DOM) with the curl UA
  D. raw curl with the browser's UA (to test whether UA alone flips it to Access Denied)

Whatever flips to "Access Denied" is the discriminator. Do not guess — this decides the fix.
"""
import asyncio
import os
import subprocess
import sys

PY_PACKAGES = "/opt/data/profiles/nura/python-packages"
PW_BROWSERS = "/opt/data/profiles/nura/.cache/ms-playwright"
URL = "https://service.emedpractice.com/"

UA_CURL = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0 Safari/537.36"
UA_BROWSER = ("Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
              "(KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36")

sys.path.insert(0, PY_PACKAGES)
os.environ["PLAYWRIGHT_BROWSERS_PATH"] = PW_BROWSERS


def verdict(title, html):
    denied = "access denied" in (title or "").lower()
    has_form = ("#email" in html) or ('id="email"' in html)
    return ("ACCESS-DENIED" if denied else "OK"), has_form, len(html)


print("=" * 88)
print("D. RAW CURL WITH THE BROWSER'S UA (does UA alone flip it?)")
print("=" * 88)
for label, ua in (("curl UA", UA_CURL), ("browser UA", UA_BROWSER)):
    r = subprocess.run(["curl", "-s", "-m", "25", "-w", "\n__HTTP__%{http_code}",
                        "-A", ua, URL], capture_output=True, text=True, timeout=40)
    body = r.stdout
    code = body.rsplit("__HTTP__", 1)[-1].strip() if "__HTTP__" in body else "?"
    t = ""
    low = body.lower()
    if "<title>" in low:
        t = body[low.index("<title>") + 7: low.index("</title>")] if "</title>" in low else ""
    st, has_form, n = verdict(t, body)
    print(f"  {label:<12} HTTP {code}  title={t[:40]!r:<44} form={has_form}  {st}")


async def main():
    from playwright.async_api import async_playwright
    async with async_playwright() as p:
        b = await p.chromium.launch(headless=True)

        print("\n" + "=" * 88)
        print("A/B. HEADLESS WITH EACH UA")
        print("=" * 88)
        for label, ua in (("curl UA", UA_CURL), ("browser UA", UA_BROWSER)):
            ctx = await b.new_context(user_agent=ua)
            pg = await ctx.new_page()
            r = await pg.goto(URL, wait_until="domcontentloaded", timeout=45000)
            html = await pg.content()
            t = await pg.title()
            st, has_form, n = verdict(t, html)
            print(f"  {label:<12} HTTP {r.status}  title={t[:40]!r:<44} form={has_form}  {n}B  {st}")
            await ctx.close()

        print("\n" + "=" * 88)
        print("C. BROWSER NETWORK STACK, NO DOM (page.request — bypasses JS)")
        print("=" * 88)
        ctx = await b.new_context(user_agent=UA_CURL)
        pg = await ctx.new_page()
        resp = await pg.request.get(URL)
        body = await resp.text()
        st, has_form, n = verdict("", body)
        print(f"  request.get  HTTP {resp.status}  bytes={n}  form={has_form}  {st}")
        await ctx.close()

        print("\n" + "=" * 88)
        print("E. WHAT THE DENIED PAGE ACTUALLY SAYS")
        print("=" * 88)
        ctx = await b.new_context(user_agent=UA_BROWSER)
        pg = await ctx.new_page()
        await pg.goto(URL, wait_until="domcontentloaded", timeout=45000)
        html = await pg.content()
        import re
        text = re.sub(r"<[^>]+>", " ", html)
        text = re.sub(r"\s+", " ", text).strip()
        print(f"  visible text: {text[:600]}")

        print("\n" + "=" * 88)
        print("F. CLIENT HINTS / HEADERS SENT")
        print("=" * 88)
        try:
            r = await pg.evaluate("""() => {
              return {ua: navigator.userAgent, webdriver: navigator.webdriver,
                      langs: navigator.languages.join(','),
                      plugins: navigator.plugins.length,
                      platform: navigator.platform,
                      hw: navigator.hardwareConcurrency};
            }""")
            for k, v in r.items():
                print(f"    {k:<12} {v}")
        except Exception as e:
            print(f"    probe failed: {e}")

        await b.close()


asyncio.run(main())
