# NURA INFRASTRUCTURE MAP (2026-08-08 — the live-probed truth!)

## The Fleet + the Mesh
| Server | Public-IP | WireGuard | Role |
|---|---|---|---|
| Clinic | 72.61.71.211 | 10.10.0.1 | The app-stack: DocsGPT · Chatwoot · MCP · NPM · RIS/PACS · Mattermost |
| Lab | 72.60.163.140 | 10.10.0.2 | The brain: Ollama · Langfuse · Dokploy · website · paperclip-db · corpora |
| Edge | 195.35.32.113 | 10.10.0.3 | The automation: n8n (×2) |

## The URLs + the routes (live-DNS + the NPM-conf truth!)
| URL | Target | Where |
|---|---|---|
| nuratech.ai + www | 72.60.163.140 | Lab (the website-stack!) |
| api.nuratech.ai | 72.60.163.140 (DNS) + NPM-route | Lab-DNS, Clinic-route — VERIFY! |
| n8n.nuratech.ai | 72.60.163.140 (DNS!) | ⚠️ MISPOINT — the n8n's on the EDGE (195.35.32.113)! The known-fix! |
| carepilot.nuratech.ai | 2.24.107.152 | the external Hostinger-Laravel! |
| mcp.nuratech.ai | 72.61.71.211 | the Clinic! |
| hermes.nuratech.ai | NPM-route | the Clinic — the Hermes-dashboard! |
| paperclip.nuratech.ai | NPM-route | the Clinic — the Paperclip-board! |
| chat.nuratech.ai + chatwoot.nuratech.ai | NPM-route | the Clinic — the Chatwoot! |
| ris.nuratech.ai | NPM-route | the Clinic — the ThaiRIS! |
| pacs.nuratech.ai | NPM-route | the Clinic — the Orthanc! |

## The Services (per node!)
**Clinic (48 containers!):** docsgpt-oss (backend :7091 · frontend :5173 · postgres · redis · worker) · chatwoot (rails :3000 · sidekiq · redis) · paperclip (:58886) · hermes-gateway (:8642) + dashboard (:9119) · openemr-zklo (mariadb!) · thairis-web (:32790) + db · ohif-viewer (:32791) · orthanc-pacs (:4242/:8042) · obsidian-livesync (:5984) · openclaw (:18789) · obd-bridge · bar-assistant · nura-mapping-gw-relay · nginx-proxy-manager (the route-hub!)
**Lab (22 containers!):** langfuse (web · worker · redis · postgres · minio · clickhouse!) · dokploy (the deploy-platform!) · nuratech-website-app · medisun (redis + insight!) · paperclip-db · ollama (qwen2.5:3b — the brain!)
**Edge (2 containers!):** n8n (code-n8n + n8n — :5678!)

## The Mesh (the new WireGuard!): 10.10.0.1↔.2↔.3 — the private-lane (verified 1-62ms!)

## The known-issues (this map's flags!)
1. ⚠️ n8n-DNS → points at the Lab; the n8n's on the Edge! (the founder hPanel-move!)
2. ⚠️ api.nuratech.ai → DNS-Lab vs the NPM-route — the dual-target needs the resolution!
3. ⚠️ The NPM-only routes (hermes/paperclip/chat/ris/pacs!) have NO public-DNS-records — the internal-only (the mesh or the IP:port access!)
4. ✅ The firewall-groups: 338570/338571/338674 (the VM-mappings!)
