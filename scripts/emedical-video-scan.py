import asyncio, os, sys
os.environ["PYTHONPATH"] = "/opt/data/profiles/nura/python-packages"
os.environ["PLAYWRIGHT_BROWSERS_PATH"] = "/opt/data/profiles/nura/.cache/ms-playwright"
sys.path.insert(0, "/opt/data/profiles/nura/python-packages")

async def m():
    from playwright.async_api import async_playwright
    async with async_playwright() as p:
        b = await p.chromium.launch(headless=True)
        pg = await b.new_page()
        await pg.goto("https://emedpractice.com/training-videos/", timeout=45000)
        await pg.wait_for_timeout(7000)
        embeds = await pg.evaluate("""() => {
            const out = [];
            document.querySelectorAll('iframe, video, source').forEach(e => {
                const s = e.src || e.getAttribute('src') || '';
                if (s) out.push(s);
            });
            return out.slice(0, 20);
        }""")
        print("EMBEDS:", embeds)
        # the titles!
        titles = await pg.evaluate("""() => {
            const out = [];
            document.querySelectorAll('h1,h2,h3,h4,.entry-title,.vc_video_title').forEach(e => {
                const t = (e.innerText || '').trim();
                if (t && t.length > 5) out.push(t);
            });
            return out.slice(0, 15);
        }""")
        print("TITLES:", titles)
        await b.close()

asyncio.run(m())
