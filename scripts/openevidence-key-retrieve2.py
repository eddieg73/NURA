#!/usr/bin/env python3
"""OpenEvidence REAL API-key retrieval — the developer-portal page, targeted."""
import asyncio, os, sys, re

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
        # 1. the login
        await pg.goto("https://www.openevidence.com", timeout=45000)
        await pg.wait_for_load_state("networkidle")
        for sel in ["a[href*='login']", "button:has-text('Log in')", "a:has-text('Log in')"]:
            el = pg.locator(sel).first
            if await el.count() > 0:
                await el.click(timeout=8000)
                break
        await pg.wait_for_timeout(2500)
        for sel in ["input[type='email']", "input[name='email']"]:
            el = pg.locator(sel).first
            if await el.count() > 0:
                await el.fill(EMAIL)
                break
        for sel in ["input[type='password']", "input[name='password']"]:
            el = pg.locator(sel).first
            if await el.count() > 0:
                await el.fill(PASSWORD)
                break
        for sel in ["button[type='submit']", "button:has-text('Log in')", "button:has-text('Sign in')", "button:has-text('Continue')"]:
            el = pg.locator(sel).first
            if await el.count() > 0:
                await el.click(timeout=8000)
                break
        await pg.wait_for_timeout(6000)
        print("logged-in:", pg.url, flush=True)
        # 2. the developer page (the real API-key!)
        for url in ["https://www.openevidence.com/developer", "https://openevidence.com/developer", "https://www.openevidence.com/api-keys", "https://www.openevidence.com/settings/api"]:
            try:
                await pg.goto(url, timeout=25000)
                await pg.wait_for_timeout(3000)
                html = await pg.content()
                # the targeted API-key patterns (the real keys!)
                keys = re.findall(r"(oe_(?:live|test|sk)_[A-Za-z0-9_\-]{16,}|[A-Za-z0-9]{40,})", html)
                # the key-display fields
                key_inputs = await pg.locator("input[value*='oe_'], input[value*='sk_'], input[value*='live']").count()
                print(f"{url}: regex-keys={len(keys)} inputs={key_inputs}", flush=True)
                if keys:
                    print("REAL-KEY:", keys[0], flush=True)
                    break
                # the copy-buttons (the key-reveal!)
                reveal = pg.locator("button:has-text('Show'), button:has-text('Copy'), button:has-text('Generate')").first
                if await reveal.count() > 0:
                    await reveal.click(timeout=5000)
                    await pg.wait_for_timeout(1500)
                    html2 = await pg.content()
                    keys2 = re.findall(r"(oe_(?:live|test|sk)_[A-Za-z0-9_\-]{16,}|[A-Za-z0-9]{40,})", html2)
                    print(f"{url}: after-reveal keys={len(keys2)}", flush=True)
                    if keys2:
                        print("REAL-KEY:", keys2[0], flush=True)
                        break
            except Exception as e:
                print(f"{url}: {str(e)[:70]}", flush=True)
        await pg.screenshot(path="/tmp/openevidence-dev.png")
        await b.close()

asyncio.run(main())
