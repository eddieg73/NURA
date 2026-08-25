# RPA / Anti-Bot Tooling Matrix (2026)
Which automation tool beats which detector. Source: 2026 anti-detect benchmark (651 verdicts) + repo recommendations.

| Tool | Score | Engine | Beats | License | Use when |
|---|---|---|---|---|---|
| **`nodriver`** | 28/31 · **0 blocked** | real Chrome over **CDP, no Playwright shim** | **automation-protocol fingerprinting** (the main gate) — canadianinsider | AGPL-3.0 | the target gates on how the browser is driven; **#1 pick** |
| `curl_cffi` | 26 | Chrome TLS+fingerprint, no JS engine | TLS-fingerprint gates (Akamai, DataDome) | Apache-2.0 | static HTML / API-only, 50-100x faster, no browser |
| `stealth-browser` | router | nodriver + curl_cffi + camoufox, auto-escalate | **multi-vendor + auto-detect the vendor** | Apache-2.0 | unknown wall; want detection + auto-fallback |
| `Patchright` | 25 | Chrome fork (CDP patches) | Chrome-based gates | — | drop-in Playwright with a bundled browser |
| `Camoufox` | 25 | Firefox fork (C-level) | Firefox-whitelisted sites / Chromium-targeting WAFs | MIT | the target whitelists Firefox or fingerprints Chromium |
| SeleniumBase UC | medium | Selenium patches | medium-security | MIT | existing Selenium codebase |

**Rule:** match the tool to the DETECTOR, not to "best tool." The eMedical/Solis bot-walls gate on **automation-protocol fingerprinting** → **nodriver** is the correct choice (0 blocked). `curl_cffi` for the API-only lane.
