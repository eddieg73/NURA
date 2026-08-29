# NURA CONNECTION REGISTRY & AUDIT (2026-08-06 — the complete smoke-test, every lane probed)

**The doctrine: every connection documented — what it is, where it's wired, its verified status, and its fix-queue. The audit = the live-truth of every MCP/API/CLI lane.**

## ✅ MCP SERVERS — VERIFIED WORKING (the tools load, 2026-08-06)
| Server | Wiring | Status |
|---|---|---|
| qdrant | wrapper → 127.0.0.1:6333 | ✓ 200 + tools (store/find!) |
| redis | wrapper → redis-gc8b | ✓ tools (set/get/pubsub!) |
| openemr | wrapper → Clinic OpenEMR API | ✓ tools (measures/patients!) |
| gemini | wrapper → Google API | ✓ tools (vision/generate! — generation 429-gated!) |
| behive | http://127.0.0.1:8090/mcp | ✓ 405-probe (reachable!) + tools |
| legal-case-law | venv python server | ✓ tools (case search!) |
| hostinger-vps / api / hosting / domains / dns / billing / reach | wrappers → Hostinger API | ✓ tools (VM/domain ops!) |
| twilio-docs | https://mcp.twilio.com/docs | ✓ tools (search/retrieve!) |
| firebase | wrapper | ✓ tools (send/validate!) |
| firecrawl | npx -y firecrawl-mcp | ✓ 25/25 tools (key sealed!) |
| notion | wrapper → Notion API | ⚠️ tools load, token-scope-gated (the share-pending!) |

## ❌ MCP SERVERS — CONNECTION FAILING (the fix-queue, root-caused)
| Server | Symptom | Root cause | Fix |
|---|---|---|---|
| perfex | Connection closed | no live Perfex instance + no creds | instance up + creds (founder-gate!) |
| chatwoot | Connection closed | wrapper env/creds on the box | the Clinic-side creds sync |
| paperclip | Connection closed | cookie-gated API from the box | session/creds lane (founder-gate!) |
| elevenlabs | Connection closed | key/endpoint config on the box | key re-seal (founder-gate!) |
| homeassistant | Connection closed | uvx ha-mcp install pending | uvx install + auth token |
| filesystem | Connection closed / :8101 = 000 | the local filesystem MCP server down | restart the :8101 server |
| playwright | Connection closed | browser env missing on the box | playwright install + browsers |

## ✅ ENDPOINTS — THE PINGS (2026-08-06)
- qdrant 6333: 200 ✓ · docsgpt 7091: 200 ✓ · langfuse 3020: 200 ✓ · ollama 11434: 200 ✓ · paperclip 3100: 200 ✓ · behive 8090: reachable (405 = POST-expected!) · Clinic NPM 80: probe-again-via-8080 (iptables-lane!)

## ✅ CLIs — VERIFIED
- hermes v0.20.0 ✓ · xurl 1.3.1 ✓ · ntn 0.21.6 ✓ · himalaya v2.0.0 ✓ · uv ✓ · npx ✓ · tailscale 1.86.2 (at /opt/data/bin — PATH-note!) · gh / mmctl / hapi = MISSING (install-queue!)

## 📋 THE FIX QUEUE (prioritized)
1. The 7 failing MCP wrappers (the root-causes above — the founder-gates on the creds!)
2. gh CLI (the GitHub lane — the PAT exists!) · hapi (the Hostinger CLI!) · mmctl (the Mattermost — the remote-lane!)
3. The filesystem :8101 restart (the local-server!)
4. The firecrawl/firebase = ready — the next-session tool-load!

## 🔄 THE AUDIT CADENCE
- The weekly MCP Lane Health cron (Mondays!) re-probes · the Connection Registry updates with every change · the founder sees the deltas in the Monday brief!
