#!/usr/bin/env python3
"""NURA Gov Health RSS poller — verified US/global government medical feeds.
Fetches feeds, dedupes by link (state file), prints NEW items as digest; silent when nothing new.
Archives full items to data/gov-health-feeds/. Stdlib only."""
import datetime, os, sys
from xml.etree import ElementTree as ET
import urllib.request

UA = "NURA-Hermes/1.0"
BASE = "/opt/data/profiles/nura/data/gov-health-feeds"
STATE = os.path.join(BASE, "seen.txt")
os.makedirs(BASE, exist_ok=True)

FEEDS = [
    ("FDA Press Releases", "https://www.fda.gov/about-fda/contact-fda/stay-informed/rss-feeds/press-releases/rss.xml"),
    ("CDC Content", "https://tools.cdc.gov/api/v2/resources/media/403372.rss"),
    ("WHO News", "https://www.who.int/rss-feeds/news-english.xml"),
]

def fetch(url):
    req = urllib.request.Request(url, headers={"User-Agent": UA})
    with urllib.request.urlopen(req, timeout=25) as r:
        return r.read()

def _safe_xml(data):
    # XXE/billion-laughs guard: reject any DTD/ENTITY declarations before parsing.
    head = data[:2000].upper()
    if b"<!DOCTYPE" in head or b"<!ENTITY" in head:
        raise ValueError("XML with DTD/entities rejected (XXE guard)")
    return ET.fromstring(data)

def items_from(xml_bytes):
    root = _safe_xml(xml_bytes)
    out = []
    for item in root.iter("item"):
        title = (item.findtext("title") or "").strip()
        link = (item.findtext("link") or "").strip()
        pub = (item.findtext("pubDate") or "").strip()
        if title and link:
            out.append((title, link, pub))
    return out

def main():
    seen = set()
    if os.path.exists(STATE):
        seen = set(l.strip() for l in open(STATE) if l.strip())
    new_all = []
    errors = []
    for name, url in FEEDS:
        try:
            for title, link, pub in items_from(fetch(url)):
                if link in seen:
                    continue
                seen.add(link)
                new_all.append((name, title, link, pub))
        except Exception as e:
            errors.append(f"{name}: {str(e)[:120]}")
    with open(STATE, "w") as f:
        f.write("\n".join(sorted(seen)))
    if new_all:
        stamp = datetime.date.today().isoformat()
        with open(os.path.join(BASE, f"items-{stamp}.md"), "a") as f:
            for name, title, link, pub in new_all:
                f.write(f"- [{name}] {title} | {pub}\n  {link}\n")
        print(f"📡 GOV HEALTH DIGEST ({len(new_all)} new)")
        for name, title, link, pub in new_all[:20]:
            print(f"• [{name}] {title} — {pub}\n  {link}")
        if len(new_all) > 20:
            print(f"… +{len(new_all) - 20} more (archive: {BASE}/)")
    if errors:
        print("⚠ Feed errors:", "; ".join(errors))
    if not new_all and not errors:
        pass  # silent when nothing new

if __name__ == "__main__":
    main()
