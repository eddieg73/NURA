#!/usr/bin/env python3
"""OPEN-EVIDENCE KNOWLEDGE SCRAPER — the dashboard search → the evidence-answers → the knowledge base!
The founder's directive: use best practices to take advantage of the API/platform; scrape the knowledge."""
import asyncio, os, sys, json, re, datetime

os.environ["PYTHONPATH"] = "/opt/data/profiles/nura/python-packages"
os.environ["PLAYWRIGHT_BROWSERS_PATH"] = "/opt/data/profiles/nura/.cache/ms-playwright"
sys.path.insert(0, "/opt/data/profiles/nura/python-packages")

EMAIL = "eg@nuratech.ai"
PASSWORD = "Lance1976!!!"
UA = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36"
OUT = "/opt/data/nura-corpora-local/openevidence-knowledge.jsonl"

QUESTIONS = [
    "What is the first-line treatment for community-acquired pneumonia in adults?",
    "What is the first-line treatment for hypertension?",
    "What is the first-line treatment for type 2 diabetes mellitus?",
    "What is the recommended treatment for acute ischemic stroke within 4.5 hours?",
    "What is the first-line therapy for heart failure with reduced ejection fraction?",
    "What is the treatment for sepsis with hypotension?",
    "What is the first-line treatment for major depressive disorder?",
    "What is the recommended anticoagulation for atrial fibrillation?",
    "What is the treatment for anaphylaxis?",
    "What is the first-line therapy for asthma exacerbation?",
    "What is the treatment for acute coronary syndrome?",
    "What is the recommended management of hyperkalemia?",
]

async def main():
    from playwright.async_api import async_playwright
    results = []
    async with async_playwright() as p:
        b = await p.chromium.launch(headless=True)
        ctx = await b.new_context(user_agent=UA)
        pg = await ctx.new_page()
        # the login
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
        # the search flow per question
        for q in QUESTIONS:
            try:
                await pg.goto("https://www.openevidence.com", timeout=25000)
                await pg.wait_for_timeout(2000)
                # the search box
                search = pg.locator("input[type='text'], input[type='search'], textarea").first
                if await search.count() > 0:
                    await search.fill(q)
                    await search.press("Enter")
                    await pg.wait_for_timeout(12000)  # the evidence generation!
                    # the answer-extract: the main content
                    text = await pg.inner_text("body")
                    # the citation-links
                    citations = re.findall(r"https?://(?:doi\.org|pubmed\.ncbi\.nlm\.nih\.gov|www\.nejm\.org|www\.thelancet\.com|jamanetwork\.com)[^\s\"'<>]+", text)
                    results.append({"question": q, "answer_snippet": text[:3000], "citations": citations[:5], "scraped_at": datetime.datetime.now().isoformat()})
                    print(f"[{len(results)}/{len(QUESTIONS)}] {q[:50]}... citations={len(citations)}", flush=True)
                else:
                    print(f"no-search-box for: {q[:40]}", flush=True)
            except Exception as e:
                print(f"ERR {q[:40]}: {str(e)[:70]}", flush=True)
        await b.close()
    with open(OUT, "w") as f:
        for r in results:
            f.write(json.dumps(r) + "\n")
    print(f"=== KNOWLEDGE-SCRAPE COMPLETE: {len(results)} answers → {OUT} ===", flush=True)

asyncio.run(main())
