#!/usr/bin/env python3
"""
Verify the playwright lane now works end to end against eMedical, WITHOUT logging in.

This stage is deliberately read-only: launch a browser, load the public login page, confirm the
selectors the job depends on are present in the LIVE DOM. It does NOT submit credentials — so it
cannot disturb the founder's own eMedical session (the job contract warns: single-session only).

Only after this passes is a login attempt justified.
"""
import asyncio
import os
import sys

PY_PACKAGES = "/opt/data/profiles/nura/python-packages"
PW_BROWSERS = "/opt/data/profiles/nura/.cache/ms-playwright"
URL = "https://service.emedpractice.com/"
UA = ("Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
      "(KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36")

sys.path.insert(0, PY_PACKAGES)
os.environ["PLAYWRIGHT_BROWSERS_PATH"] = PW_BROWSERS


async def main():
    from playwright.async_api import async_playwright

    print("=" * 86)
    print("PLAYWRIGHT LANE VERIFICATION (no credentials submitted)")
    print("=" * 86)
    async with async_playwright() as p:
        print(f"  chromium executable: {p.chromium.executable_path}")
        exists = os.path.exists(p.chromium.executable_path)
        print(f"  binary exists      : {exists}")
        if not exists:
            print("  FAIL: browser binary missing")
            return 1

        try:
            b = await p.chromium.launch(headless=True)
        except Exception as e:
            print(f"  LAUNCH FAILED: {type(e).__name__}: {str(e)[:300]}")
            return 1
        print(f"  launch             : OK  (version {b.version})")
        try:
            ctx = await b.new_context(user_agent=UA)
            pg = await ctx.new_page()
            resp = await pg.goto(URL, wait_until="domcontentloaded", timeout=45000)
            print(f"  HTTP status        : {resp.status if resp else 'n/a'}")
            print(f"  title              : {(await pg.title())[:80]}")

            print("\n  LIVE SELECTOR CHECK (what emed-gap-audit.py depends on):")
            ok_all = True
            for sel, label in (("#email", "username field"),
                               ("#password", "password field"),
                               ("#SigninBtn", "sign-in button (type=image)"),
                               ("#form1", "form"),
                               ("#__VIEWSTATE", "ASP.NET viewstate")):
                try:
                    el = await pg.query_selector(sel)
                    vis = await el.is_visible() if el else False
                    state = "PRESENT" + (" + visible" if vis else " (hidden)")
                    if not el:
                        state = "** MISSING **"
                        ok_all = False
                    print(f"    {label:<28} {sel:<16} {state}")
                except Exception as e:
                    print(f"    {label:<28} {sel:<16} ERR {type(e).__name__}")
                    ok_all = False

            # can we actually read the fields?
            try:
                t = await pg.get_attribute("#email", "placeholder")
                print(f"\n  #email placeholder : {t!r}  (confirms it is the USER NAME field)")
            except Exception:
                pass

            await b.close()
            print("\n" + "=" * 86)
            print(f"  VERDICT: browser lane {'WORKS' if ok_all else 'BROKEN — selector mismatch'}")
            print("  No credentials were submitted in this stage.")
            return 0 if ok_all else 1
        except Exception as e:
            print(f"  NAV/EXTRACT FAILED: {type(e).__name__}: {str(e)[:300]}")
            try:
                await b.close()
            except Exception:
                pass
            return 1


sys.exit(asyncio.run(main()))
