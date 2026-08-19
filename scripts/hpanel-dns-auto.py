#!/usr/bin/env python3
"""The hPanel-DNS-automation — the playwright: login → the DNS-zone → add the A-records (the founder's-account!)."""
import asyncio, os, sys, json

os.environ["PYTHONPATH"] = "/opt/data/profiles/nura/python-packages"
os.environ["PLAYWRIGHT_BROWSERS_PATH"] = "/opt/data/profiles/nura/.cache/ms-playwright"
sys.path.insert(0, "/opt/data/profiles/nura/python-packages")

EMAIL = "eg@nuratech.ai"
PASSWORD = "Lance1976!!!"
RECORDS = [
    ("chatwoot", "72.61.71.211"), ("chat", "72.61.71.211"), ("care", "72.61.71.211"),
    ("pacs", "72.61.71.211"), ("ai", "72.61.71.211"), ("docsgpt", "72.61.71.211"),
    ("langfuse", "72.60.163.140"), ("mattermost", "72.61.71.211"), ("ris", "72.61.71.211"),
    ("openemr", "72.61.71.211"), ("perfex", "72.60.163.140"),
]

async def main():
    from playwright.async_api import async_playwright
    async with async_playwright() as p:
        b = await p.chromium.launch(headless=True, args=["--disable-blink-features=AutomationControlled", "--no-sandbox"])
        ctx = await b.new_context(user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36")
        await ctx.add_init_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined});")
        pg = await ctx.new_page()
        try:
            await pg.goto("https://hpanel.hostinger.com/", timeout=45000)
            await pg.wait_for_timeout(5000)
            print("page:", pg.url[:60], flush=True)
            # the login!
            for sel in ["input[type='email']", "input[name='email']", "input[placeholder*='mail']"]:
                el = pg.locator(sel).first
                if await el.count() > 0:
                    await el.fill(EMAIL, timeout=10000)
                    break
            for sel in ["button[type='submit']", "button:has-text('Continue')", "button:has-text('Log in')"]:
                el = pg.locator(sel).first
                if await el.count() > 0:
                    await el.click(timeout=8000)
                    break
            await pg.wait_for_timeout(4000)
            for sel in ["input[type='password']", "input[name='password']"]:
                el = pg.locator(sel).first
                if await el.count() > 0:
                    await el.fill(PASSWORD, timeout=10000)
                    break
            for sel in ["button[type='submit']", "button:has-text('Log in')", "button:has-text('Continue')"]:
                el = pg.locator(sel).first
                if await el.count() > 0:
                    await el.click(timeout=8000)
                    break
            await pg.wait_for_timeout(8000)
            print("post-login:", pg.url[:70], flush=True)
            await pg.screenshot(path="/tmp/hpanel.png")
        except Exception as e:
            print("ERR:", str(e)[:130], flush=True)
        await b.close()

asyncio.run(main())
