#!/usr/bin/env python3
"""Inspect the OpenEvidence dashboard's search UI (the element-hunt!)."""
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
        await pg.wait_for_timeout(7000)
        print("URL:", pg.url, flush=True)
        # the element-census: inputs + contenteditable + textareas + the placeholder-any
        census = await pg.evaluate("""() => {
            const els = [...document.querySelectorAll('input, textarea, [contenteditable=true], [role=textbox], [role=searchbox]')];
            return els.slice(0, 15).map(e => ({tag: e.tagName, type: e.type || '', ph: e.placeholder || '', role: e.getAttribute('role') || '', cls: (e.className || '').toString().slice(0, 40)}));
        }""")
        print("CENSUS:", json_dumps(census), flush=True)
        await pg.screenshot(path="/tmp/openevidence-dash2.png")
        await b.close()

def json_dumps(x):
    import json
    return json.dumps(x)

asyncio.run(main())
