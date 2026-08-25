# Web-Scraping / RPA & Anti-Bot Tooling Matrix (2026)

## Anti-bot / automation (which tool beats which detector)
| Tool | Score | Engine | Beats | License |
|---|---|---|---|---|
| **`nodriver`** | 28/31 · **0 blocked** | real Chrome over **CDP, no Playwright shim** | **automation-protocol fingerprinting** (the main gate) | AGPL-3.0 |
| `curl_cffi` | 26 | Chrome TLS+fingerprint, no JS | TLS-fingerprint (Akamai/DataDome) | Apache-2.0 |
| `stealth-browser` | router | nodriver + curl_cffi + camoufox | multi-vendor + auto-detect | Apache-2.0 |
| `Patchright` | 25 | Chrome fork (CDP patches) | Chrome-based gates | — |
| `Camoufox` | 25 | Firefox fork (C-level) | Firefox-whitelisted / Chromium-targeting WAFs | MIT |
| SeleniumBase UC | medium | Selenium patches | medium-security | MIT |

## LLM-ready extractors (turn pages → structured JSON → RAG/LLM) — BEST for clinical data
| Tool | What it does | We have it? |
|---|---|---|
| **Firecrawl** (`firecrawl/firecrawl`) | sites → clean Markdown/structured JSON for LLM/RAG | ✅ **MCP** (`firecrawl_*`) |
| **browser-use** (`browser-use/browser-use`) | AI agent drives a browser via natural language | ✅ **`browser_exec`** tool |
| **Crawl4AI** (`unclecode/crawl4ai`) | high-speed, LLM-friendly structured output | ➕ add |
| **ScrapeGraphAI** | LLM graph pipelines, no manual selectors | ➕ add |

## Full crawler frameworks
Scrapy (Python, industry standard) · Crawlee (Apify, TS/Python, proxy rotation + anti-block) · Colly (Go, fast) — heavier than needed for a single EHR portal; useful for bulk/batch.

## Browser automation
Playwright (Microsoft; SPA scraping) · Puppeteer (Google, Node CDP).

## Curated / specialized
`awesome-scrapers` (directory) · `yt-dlp` (video/audio).

## Recommended stack for eMedical / Solis clinical data
**browser-use** (drive login, AI agent) → **Firecrawl / Crawl4AI** (parse chart → **structured JSON**) → **NURA MEAT gate + RAF-combine + `solis_hermes`/Mirth warehouse**. This turns the EHR pages into LLM-ready structured clinical records instead of raw HTML.
**Login/bot-wall:** `nodriver` (#1 anti-detect) or the **Cookie-Editor JSON** session-ride, or the vendor **FHIR API** (cleanest, permanent).
