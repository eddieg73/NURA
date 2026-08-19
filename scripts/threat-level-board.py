#!/usr/bin/env python3
"""NURA Threat Level Board — outbreak / military / UAP OSINT monitor.
Deterministic keyword classification → per-domain threat level + composite board.
Alerts when: any item mentions Florida/US, or any domain hits ORANGE+, or new high items.
Silent when nothing new and all GREEN. Stdlib only. Feed URLs live-verified 2026-08-01."""
import datetime, os, re, sys, urllib.request
from xml.etree import ElementTree as ET

UA = "NURA-Hermes/1.0"
BASE = "/opt/data/profiles/nura/data/threat-board"
STATE = os.path.join(BASE, "seen.txt")
os.makedirs(BASE, exist_ok=True)

FEEDS = [
    ("WHO", "https://www.who.int/rss-feeds/news-english.xml"),
    ("CDC", "https://tools.cdc.gov/api/v2/resources/media/403372.rss"),
    ("MMWR", "https://tools.cdc.gov/api/v2/resources/media/132120.rss"),
    ("DEFENSE-NEWS", "https://www.defensenews.com/arc/outboundfeeds/rss/?outputType=xml"),
    ("CRISIS-GROUP", "https://www.crisisgroup.org/rss.xml"),
    ("NYT-POLITICS", "https://www.nytimes.com/svc/collections/v1/publish/https://www.nytimes.com/section/us/politics/rss.xml"),
    ("DEBRIEF", "https://thedebrief.org/feed/"),
]

# Domain classification: (domain, weight, match-terms)
OUTBREAK_TERMS = ["outbreak", "epidemic", "pandemic", "pheic", "ebola", "marburg", "nipah", "h5n1", "mpox",
                  "cholera", "dengue", "zika", "measles", "polio", "influenza", "covid", "who declares",
                  "public health emergency", "vaccination campaign", "disease", "virus"]
OUTBREAK_HIGH = ["pandemic", "pheic", "ebola", "marburg", "nipah", "h5n1", "public health emergency of international"]
OUTBREAK_MED = ["epidemic", "outbreak", "emergency"]
MIL_TERMS = ["war", "invasion", "airstrike", "airstrikes", "military intervention", "troops", "mobilization",
             "nuclear", "strikes", "combat", "missile", "naval", "deployment", "ceasefire", "conflict",
             "tensions", "exercises", "nato", "pentagon", "shelling", "offensive"]
MIL_HIGH = ["war", "invasion", "nuclear", "mobilization", "military intervention", "wwiii", "world war"]
MIL_MED = ["airstrike", "airstrikes", "troops", "strikes", "offensive", "combat", "missile"]
UAP_TERMS = ["uap", "ufo", "unidentified", "disclosure", "aaro", "non-human", "crash retrieval", "anomaly",
             "congressional hearing", "phenomena", "unexplained"]
UAP_HIGH = ["congressional hearing", "disclosure", "non-human", "crash retrieval", "uap report", "official"]
US_TERMS = ["florida", "tampa", "miami", "jacksonville", "orlando", "united states", "u.s.", " usa ", " america",
            " pentagon", "nato", "white house", "congress", "us "]
FL_TERMS = ["florida", "tampa", "miami", "jacksonville", "orlando", "fl."]

def _safe_xml(data):
    head = data[:2000].upper()
    if b"<!DOCTYPE" in head or b"<!ENTITY" in head:
        raise ValueError("XML with DTD/entities rejected")
    return ET.fromstring(data)

def fetch(url):
    req = urllib.request.Request(url, headers={"User-Agent": UA})
    with urllib.request.urlopen(req, timeout=25) as r:
        return r.read()

def items_from(xml_bytes):
    root = _safe_xml(xml_bytes)
    out = []
    for item in root.iter("item"):
        title = (item.findtext("title") or "").strip()
        link = (item.findtext("link") or "").strip()
        desc = (item.findtext("description") or "")[:200]
        if title and link:
            out.append((title, link, desc))
    return out

def classify(title, desc):
    text = f"{title} {desc}".lower()
    # policy/industry noise — downgrade signals, never threat levels
    NEG = ["agreement", "accord", "meeting", "summit", "progress", "funding", "donation", "strategy",
           "engagement", "awards", "deal", "contract", "billion", "stockpile", "budget", "industry",
           "certified", "poll finds", "petition", "scholarship"]
    dom, level, us, fl = None, 0, False, False
    if any(t in text for t in OUTBREAK_TERMS):
        dom = "OUTBREAK"
        if any(t in text for t in OUTBREAK_HIGH) and not any(n in text for n in NEG):
            level = 3
        elif any(t in text for t in OUTBREAK_MED) and not any(n in text for n in NEG):
            level = 2
        elif any(t in text for t in OUTBREAK_TERMS):
            level = 1
    elif any(t in text for t in MIL_TERMS):
        dom = "MILITARY"
        if any(t in text for t in MIL_HIGH) and not any(n in text for n in NEG):
            level = 3
        elif any(t in text for t in MIL_MED) and not any(n in text for n in NEG):
            level = 2
        elif any(t in text for t in MIL_TERMS):
            level = 1
    elif any(t in text for t in UAP_TERMS):
        dom = "UAP"
        level = 3 if any(t in text for t in UAP_HIGH) else 1
    if re.search(r"\b(florida|tampa|miami|jacksonville|orlando|fl)\b", text) or " florida " in text:
        fl = True
    if re.search(r"\b(us|usa|u\.s\.|united states|america|pentagon|nato|white house|congress)\b", text):
        us = True
    return dom, level, us, fl

LEVELS = {0: "GREEN", 1: "GREEN", 2: "YELLOW", 3: "ORANGE"}  # per-domain; RED reserved for FL/US ORANGE+
def main():
    seen = set()
    if os.path.exists(STATE):
        seen = set(l.strip() for l in open(STATE) if l.strip())
    domains = {"OUTBREAK": 0, "MILITARY": 0, "UAP": 0}
    new = []          # (domain, level, title, link, us, fl)
    alerts = []
    errors = []
    for name, url in FEEDS:
        try:
            for title, link, desc in items_from(fetch(url)):
                if link in seen:
                    continue
                seen.add(link)
                dom, level, us, fl = classify(title, desc)
                if dom:
                    new.append((dom, level, title, link, us, fl))
                    domains[dom] = max(domains[dom], level)
                    if fl:
                        alerts.append(f"🔴 FLORIDA ITEM [{dom} L{level}]: {title} — {link}")
                    elif us:
                        alerts.append(f"🟠 US ITEM [{dom} L{level}]: {title} — {link}")
        except Exception as e:
            errors.append(f"{name}: {str(e)[:100]}")
    with open(STATE, "w") as f:
        f.write("\n".join(sorted(seen)))
    if not new and not alerts and not errors:
        return  # silent when nothing new, all green
    board = []
    board.append("📊 NURA THREAT LEVEL BOARD — " + datetime.datetime.now().strftime("%Y-%m-%d %H:%M UTC"))
    for d in ["OUTBREAK", "MILITARY", "UAP"]:
        lv = domains[d]
        board.append(f"  {d}: {LEVELS.get(lv, 'GREEN')}" + (" (ESCALATED)" if lv >= 2 else ""))
    for a in alerts[:12]:
        board.append(a)
    by_dom = {}
    for dom, level, title, link, us, fl in sorted(new, key=lambda x: -x[1]):
        by_dom.setdefault(dom, []).append(f"  [L{level}] {title} — {link}")
    for d, items in by_dom.items():
        board.append(f"  · {d} new items:")
        board.extend(items[:6])
    if errors:
        board.append("⚠ feed errors: " + "; ".join(errors))
    out = "\n".join(board)
    with open(os.path.join(BASE, f"board-{datetime.date.today().isoformat()}.md"), "a") as f:
        f.write(out + "\n\n")
    print(out)

if __name__ == "__main__":
    main()
