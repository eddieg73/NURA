#!/usr/bin/env python3
"""The Facebook share-page read — the python-playwright lane (the known-working!)."""
import asyncio, os, sys

os.environ["PYTHONPATH"] = "/opt/data/profiles/nura/python-packages"
os.environ["PLAYWRIGHT_BROWSERS_PATH"] = "/opt/data/profiles/nura/.cache/ms-playwright"
sys.path.insert(0, "/opt/data/profiles/nura/python-packages")
UA = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36"

async def main():
    from playwright.async_api import async_playwright
    async with async_playwright() as p:
        b = await p.chromium.launch(headless=True)
        ctx = await b.new_context(user_agent=UA)
        pg = await ctx.new_page()
        try:
            await pg.goto("https://www.facebook.com/share/r/1DH1e2x292/", timeout=45000)
            await pg.wait_for_timeout(6000)
            title = await pg.title()
            print("TITLE:", title, flush=True)
            # the meta-description + the og-tags
            meta = await pg.evaluate("""() => {
                const og = document.querySelector('meta[property="og:description"]');
                const ogt = document.querySelector('meta[property="og:title"]');
                const desc = document.querySelector('meta[name="description"]');
                return {og_desc: og ? og.content : '', og_title: ogt ? ogt.content : '', desc: desc ? desc.content : ''};
            }""")
            print("META:", meta, flush=True)
            await pg.screenshot(path="/tmp/fb-share.png")
        except Exception as e:
            print("ERR:", str(e)[:150], flush=True)
        await b.close()

asyncio.run(main())
