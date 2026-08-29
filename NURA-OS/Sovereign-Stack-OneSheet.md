# Sovereign Self-Hosted AI Enterprise — One-Sheet (founder 2026-08-02) + NURA status map

Goal: air-gapped medical & ops intelligence platform (Hermes/Llama local, Qdrant memory, PostgreSQL/OpenEMR, Paperclip/n8n orchestration, human-in-the-loop via Mattermost).

## Status map (verified 2026-08-02)
| Component | NURA status | Action |
|---|---|---|
| Nginx Proxy Manager | ✅ LIVE (NPM :80/443 on 1441409) | keep |
| MeshCentral | ❌ not deployed | optional — remote OOB admin (CTO decision) |
| vLLM / Ollama (local Llama) | ⚠️ Ollama DELETED; vLLM skill exists, NOT deployed | **Lab 1030183 = the sovereign inference lane** (quantized models; replaces cloud for PHI reasoning) |
| Paperclip | ✅ LIVE :3101, 59 agents | keep |
| Agent Zero | ❌ not deployed (community project — optional; Paperclip already covers hierarchy) | skip unless needed |
| n8n | ✅ LIVE (n8n.nuratech.ai) | keep |
| MCP | ✅ LIVE (35+ lanes) | keep |
| Qdrant | ✅ LIVE (nura-docs 540 chunks) | keep |
| PostgreSQL | 🔶 planned (NUR-103 app DB) + OpenEMR MySQL | sequence per NUR-103 |
| Redis | ✅ LIVE (8.8.1, vectorset) | keep |
| OpenEMR | ✅ deployed (OAuth gate pending) | keep |
| Mattermost | ❌ skill exists, NOT deployed | **DEPLOY = human-in-the-loop approvals/alerts lane (operator charter)** |
| Home Assistant | ❌ skill exists, NOT deployed | optional (IoT) |
| Media Server / Tandoor | ❌ not deployed | optional (non-clinical) |

## HONEST CORRECTION (doctrine)
"Entirely air-gapped from third-party cloud APIs" is NOT TRUE today: reasoning runs DeepSeek/Gemini/Anthropic (cloud, NON-PHI only); PHI stays local. TRUE air-gap = local vLLM lane on Lab (quantized Llama/MedGemma) + local embeddings (already 384d fastembed) + local STT (Whisper on device). Feasible; cost = GPU-ish compute on Lab + model mgmt. CTO to sequence.

## Board
NUR-104 → CTO: (1) Mattermost deploy (approval lane), (2) vLLM local lane on Lab (air-gap milestone), (3) MeshCentral/AgentZero/HA/media = optional backlog, (4) evidence per deploy.
