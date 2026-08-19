import sys
sys.path.insert(0, "/opt/data/profiles/nura/python-packages")
from playwright.sync_api import sync_playwright

with sync_playwright() as p:
    browser = p.chromium.launch(executable_path="/opt/data/chrome/chrome-linux64/chrome",
                                args=["--no-sandbox", "--disable-gpu"])
    page = browser.new_page(viewport={"width": 460, "height": 920})
    page.goto("file:///opt/data/uploads/app-ui-mock.html")
    page.wait_for_timeout(800)
    page.screenshot(path="/opt/data/uploads/app-ui-mock.png")
    browser.close()
import os
print("PNG bytes:", os.path.getsize("/opt/data/uploads/app-ui-mock.png"))
