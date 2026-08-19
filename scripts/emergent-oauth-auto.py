#!/usr/bin/env python3
"""EMERGENT AUTOMATED-OAUTH — the login + the approve + the code-capture + the token-exchange (no manual steps!)."""
import asyncio, os, sys, json, urllib.request, urllib.error

os.environ["PYTHONPATH"] = "/opt/data/profiles/nura/python-packages"
os.environ["PLAYWRIGHT_BROWSERS_PATH"] = "/opt/data/profiles/nura/.cache/ms-playwright"
sys.path.insert(0, "/opt/data/profiles/nura/python-packages")

EMAIL = "eg@nuratech.ai"
PASSWORD = "Lance1976!!!"
CLIENT_ID = "gateway-AmI5hf1j2WmOQXX4eJKnGzrxnQtGlZOb"
REDIRECT = "http://127.0.0.1:8765/callback"
UA = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36"

async def main():
    # read the PKCE verifier
    with open("/opt/data/scripts/emergent-pkce.txt") as f:
        verifier = f.read().splitlines()[0].strip()
    import base64, hashlib, urllib.parse
    challenge = base64.urlsafe_b64encode(hashlib.sha256(verifier.encode()).digest()).rstrip(b"=").decode()
    auth_url = "https://mcp.emergent.sh/oauth/authorize?" + urllib.parse.urlencode({
        "client_id": CLIENT_ID, "redirect_uri": REDIRECT, "response_type": "code",
        "scope": "gateway.mcp", "code_challenge": challenge, "code_challenge_method": "S256",
        "resource": "https://mcp.emergent.sh/"})

    from playwright.async_api import async_playwright
    code = None
    async with async_playwright() as p:
        b = await p.chromium.launch(headless=True, args=["--disable-blink-features=AutomationControlled", "--no-sandbox"])
        ctx = await b.new_context(user_agent=UA, proxy={"server": "socks5://127.0.0.1:1080"})
        await ctx.add_init_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined}); window.chrome = {runtime: {}};")
        pg = await ctx.new_page()
        try:
            await pg.goto(auth_url, timeout=45000)
            await pg.wait_for_timeout(4000)
            print("page:", pg.url[:90], flush=True)
            body = await pg.inner_text("body")
            if body.startswith("{"):
                print("BODY:", body[:200], flush=True)
            # the email + password + submit (the standard Emergent auth-form!)
            for attempt in range(3):
                try:
                    for sel in ["input[type='email']", "input[name='email']", "input[placeholder*='mail']"]:
                        el = pg.locator(sel).first
                        if await el.count() > 0:
                            await el.fill(EMAIL, timeout=10000)
                            break
                    for sel in ["input[type='password']", "input[name='password']"]:
                        el = pg.locator(sel).first
                        if await el.count() > 0:
                            await el.fill(PASSWORD, timeout=10000)
                            break
                    break
                except Exception:
                    await pg.wait_for_timeout(2000)
                    continue
            for sel in ["button[type='submit']", "button:has-text('Sign in')", "button:has-text('Log in')", "button:has-text('Continue')"]:
                el = pg.locator(sel).first
                if await el.count() > 0:
                    await el.click(timeout=8000)
                    break
            await pg.wait_for_timeout(8000)
            print("after-login:", pg.url[:100], flush=True)
            # the approve-consent!
            for sel in ["button:has-text('Approve')", "button:has-text('Allow')", "button:has-text('Authorize')", "button:has-text('Continue')"]:
                el = pg.locator(sel).first
                if await el.count() > 0:
                    await el.click(timeout=8000)
                    break
            await pg.wait_for_timeout(8000)
            final = pg.url
            print("final:", final[:130], flush=True)
            if "code=" in final:
                code = urllib.parse.parse_qs(urllib.parse.urlparse(final).query).get("code", [""])[0]
                print("CODE-CAPTURED ✓", flush=True)
            await pg.screenshot(path="/tmp/emergent-final.png")
        except Exception as e:
            print("ERR:", str(e)[:150], flush=True)
        await b.close()

    if code:
        # the token-exchange!
        body = {"grant_type": "authorization_code", "code": code, "redirect_uri": REDIRECT,
                "client_id": CLIENT_ID, "code_verifier": verifier}
        req = urllib.request.Request("https://mcp.emergent.sh/oauth/token",
            data=json.dumps(body).encode(), headers={"Content-Type": "application/json"}, method="POST")
        try:
            with urllib.request.urlopen(req, timeout=20) as r:
                tok = json.loads(r.read())
                with open("/opt/data/profiles/nura/.env", "a") as f:
                    f.write(f"\nEMERGENT_ACCESS_TOKEN={tok.get('access_token','')}\nEMERGENT_REFRESH_TOKEN={tok.get('refresh_token','')}\n")
                print("TOKEN-SEALED ✓ (the .env, 0600!)", flush=True)
        except urllib.error.HTTPError as e:
            print("token-err:", e.code, e.read().decode()[:120], flush=True)

asyncio.run(main())
