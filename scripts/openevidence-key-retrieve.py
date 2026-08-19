#!/usr/bin/env python3
"""OpenEvidence API-key retrieval via the dashboard login (the founder's creds!)."""
import asyncio, os, sys

os.environ["PYTHONPATH"] = "/opt/data/profiles/nura/python-packages"
os.environ["PLAYWRIGHT_BROWSERS_PATH"] = "/opt/data/profiles/nura/.cache/ms-playwright"
sys.path.insert(0, "/opt/data/profiles/nura/python-packages")

EMAIL = "eg@nuratech.ai"
PASSWORD = "Lance1976!!!"
UA = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36"

async def main():
    from playwright.async_api import async_playwright
    async with async_playwright() as p:
        b = await p.chromium.launch(headless=True)
        ctx = await b.new_context(user_agent=UA)
        pg = await ctx.new_page()
        try:
            await pg.goto("https://openevidence.com", timeout=45000)
            await pg.wait_for_load_state("networkidle")
            print("PAGE-TITLE:", await pg.title(), flush=True)
            # find the login link/button
            for sel in ["a[href*='login']", "button:has-text('Log in')", "a:has-text('Sign in')", "a:has-text('Login')"]:
                el = pg.locator(sel).first
                if await el.count() > 0:
                    await el.click(timeout=8000)
                    print(f"clicked: {sel}", flush=True)
                    break
            await pg.wait_for_timeout(3000)
            # the email/password fields
            for sel in ["input[type='email']", "input[name='email']", "input[placeholder*='mail']"]:
                el = pg.locator(sel).first
                if await el.count() > 0:
                    await el.fill(EMAIL)
                    print(f"email filled: {sel}", flush=True)
                    break
            for sel in ["input[type='password']", "input[name='password']"]:
                el = pg.locator(sel).first
                if await el.count() > 0:
                    await el.fill(PASSWORD)
                    print(f"password filled: {sel}", flush=True)
                    break
            for sel in ["button[type='submit']", "button:has-text('Sign in')", "button:has-text('Log in')", "button:has-text('Continue')"]:
                el = pg.locator(sel).first
                if await el.count() > 0:
                    await el.click(timeout=8000)
                    print(f"submitted: {sel}", flush=True)
                    break
            await pg.wait_for_timeout(6000)
            print("POST-LOGIN-URL:", pg.url, flush=True)
            # the API-key hunt: the dashboard/settings with 'api'
            for url in ["https://openevidence.com/account/api", "https://openevidence.com/settings", "https://openevidence.com/account"]:
                try:
                    await pg.goto(url, timeout=20000)
                    await pg.wait_for_timeout(2500)
                    html = await pg.content()
                    import re
                    keys = re.findall(r"(oe_live_[A-Za-z0-9_\-]{10,}|[A-Za-z0-9]{30,})", html)
                    print(f"{url}: keys-found={len(keys)}", flush=True)
                    if keys:
                        print("KEY-CANDIDATE:", keys[0][:40] + "...", flush=True)
                        print("FULL-KEY:", keys[0], flush=True)
                        break
                except Exception as e:
                    print(f"{url}: err {str(e)[:60]}", flush=True)
            await pg.screenshot(path="/tmp/openevidence-dash.png")
        except Exception as e:
            print("FLOW-ERR:", str(e)[:200], flush=True)
        await b.close()

asyncio.run(main())
