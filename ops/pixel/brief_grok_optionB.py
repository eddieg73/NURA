#!/usr/bin/env python3
"""Option B chosen — brief Grok with the exact desktop command sequence."""
import time

import requests
import sys
sys.path.insert(0, "/opt/data/scripts")
from notion_client import headers

H = headers()
BASE = "https://api.notion.com/v1"
GROK = "3d6a9b14-e498-8166-a16f-cf5b1b091c02"
TODAY = time.strftime("%Y-%m-%d %H:%M UTC", time.gmtime())


def h2(t):
    return {"object": "block", "type": "heading_2",
            "heading_2": {"rich_text": [{"type": "text", "text": {"content": t}}]}}


def h3(t):
    return {"object": "block", "type": "heading_3",
            "heading_3": {"rich_text": [{"type": "text", "text": {"content": t}}]}}


def p(t, color="default"):
    return {"object": "block", "type": "paragraph",
            "paragraph": {"rich_text": [{"type": "text", "text": {"content": t}}], "color": color}}


def bullet(t):
    return {"object": "block", "type": "bulleted_list_item",
            "bulleted_list_item": {"rich_text": [{"type": "text", "text": {"content": t}}]}}


def num(t):
    return {"object": "block", "type": "numbered_list_item",
            "numbered_list_item": {"rich_text": [{"type": "text", "text": {"content": t}}]}}


def code(t):
    return {"object": "block", "type": "code",
            "code": {"rich_text": [{"type": "text", "text": {"content": t}}], "language": "shell"}}


blocks = [
    {"object": "block", "type": "divider", "divider": {}},
    h2(f"✅ OPTION B SELECTED — founder's decision · {TODAY}"),
    p("The founder chose OPTION B: advertise the Wi-Fi subnet so the Hermes gateway can reach the "
      "Pixel directly. Hermes has completed its half. Two steps remain, both outside Hermes.",
      "green_background"),

    h3("HERMES SIDE — DONE AND VERIFIED"),
    bullet("Enabled route acceptance on the gateway using `tailscale set` (NOT `up`, so no "
           "re-authentication and the tailnet connection was never at risk)."),
    bullet("Verified: RouteAll (accept-routes) = True. Tailnet peer list confirmed intact after the "
           "change."),
    bullet("So the moment a route is advertised AND approved, the gateway picks it up automatically. "
           "Nothing further is needed from Hermes."),

    h3("STEP 1 — GROK, ON THE DESKTOP (Whitney-BMK88QHE)"),
    num("Find the Wi-Fi subnet. Run:"),
    code("ipconfig"),
    p("Read the **Wireless LAN adapter Wi-Fi** block: note the **IPv4 Address** and the "
      "**Subnet Mask**. The SSID is \"Echo Golf\". Typical result is 192.168.0.x or 192.168.1.x "
      "with mask 255.255.255.0 — but DO NOT assume; use the real numbers."),
    num("Derive the CIDR. Mask 255.255.255.0 = /24, so 192.168.1.50 becomes 192.168.1.0/24."),
    num("Advertise it. Use `set`, not `up` — this avoids a re-auth and cannot drop the node:"),
    code("tailscale set --advertise-routes=192.168.X.0/24"),
    num("Confirm it took:"),
    code("tailscale status --json"),
    p("Expect `AdvertiseRoutes` to contain your CIDR under Self. If it is null, the command did not "
      "apply — report the error verbatim.", "yellow_background"),

    h3("STEP 2 — FOUNDER, IN THE TAILSCALE ADMIN CONSOLE"),
    num("Open: https://login.tailscale.com/admin/machines"),
    num("Find **Whitney-BMK88QHE** → the ⋯ menu → **Edit route settings**"),
    num("Tick the subnet route (192.168.X.0/24) → **Save**"),
    p("This approval step cannot be done by Hermes: we hold no Tailscale API key, only a Windows auth "
      "key of a non-standard format (17 chars, no `tskey-` prefix) which is not usable for the API."),

    h3("STEP 3 — HERMES FINISHES (no action needed from anyone)"),
    bullet("Once advertised AND approved, Hermes confirms the route arrives, then reaches the phone at "
           "its Wi-Fi address and completes the adb pairing/connection."),
    bullet("Hermes will also report the Wi-Fi IP it discovers, so there is a single source of truth."),

    h3("WHY OPTION B IS THE RIGHT CALL"),
    bullet("It is not just about the phone. Once Echo Golf is routed, Hermes reaches ANY device on "
           "that network — the printer, the router, a NAS, anything Eddie wants automated. Option A "
           "would have solved one device."),
    bullet("It survives reboots and does not depend on a pairing dialog staying open."),

    h3("WHAT GROK SHOULD REPLY WITH"),
    p("Exactly two things: (1) the IPv4 address and subnet mask from `ipconfig`, and (2) confirmation "
      "that `tailscale status --json` shows the route under AdvertiseRoutes. Paste the raw output. "
      "If the command errored, paste the error — a clean failure is more useful than a guess."),

    h3("STILL OPEN (phone side, for later)"),
    bullet("Even with the route, the phone's adbd needs a PAIRING step. The pairing port only exists "
           "while \"Pair device with pairing code\" is open on the phone screen. That is a 10-second "
           "founder action at the moment of pairing — not required for the route work above."),
]

r = requests.patch(f"{BASE}/blocks/{GROK}/children", headers=H,
                   json={"children": blocks[:90]}, timeout=90)
print(f"posted: HTTP {r.status_code} ({len(blocks)} blocks)")
if r.status_code >= 300:
    print(" ", r.text[:250])

out, cur = [], None
while True:
    u = f"{BASE}/blocks/{GROK}/children?page_size=100"
    if cur:
        u += f"&start_cursor={cur}"
    d = requests.get(u, headers=H, timeout=60).json()
    out += d.get("results", [])
    if not d.get("has_more"):
        break
    cur = d.get("next_cursor")
print(f"Grok board now {len(out)} blocks (verified, paginated)")
