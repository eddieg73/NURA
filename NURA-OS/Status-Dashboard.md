# NURA Status Dashboard

The one page for everything I'm managing. Updated by the status-board cron (daily 07:00) and on every significant change. The chat stays quiet — this is where the status lives. Last updated: 2026-08-19.

## The fleet
| Node | State | Disk | Note |
|---|---|---|---|
| Clinic 72.61.71.211 | 🟢 Up | 185G free | OpenEMR · Orthanc · ThaiRIS · Mirth · DocsGPT |
| Lab 72.60.163.140 | 🟢 Up | 118G free | Ollama · RustFS · Paperclip · n8n · Medplum |
| Edge 195.35.32.113 | 🟢 Up | 37G free | — |
| Hermes box | 🟢 Up | — | gateway :8642 · tools-API :8095 · Ollama |

## The services
| Service | State | Where |
|---|---|---|
| Gateway :8642 | 🟢 | local |
| WebUI :8787 | 🟢 | local |
| tools-API :8095 | 🟢 (llm:ok — the scribe/synthesis/health fixed 08-19) | local |
| Ollama (16 models) | 🟢 | local + Lab |
| DocsGPT :7091 | 🟢 (the 4 breaks repaired 08-19) | Clinic |
| Orthanc PACS | 🟢 (the synthetic DICOM loop proven) | Clinic |
| OHIF viewer | 🟡 (the nginx DICOMweb 401 — the queued fix) | Clinic |
| ThaiRIS | 🟢 | Clinic |
| Mirth 4.6 | 🟡 (the MLLP 6665/6666/6667 closed; the admin pw pending) | Clinic |
| OpenEMR | 🟢 (the MCP 20 tools) | Clinic |
| dsh harness | 🟢 (the 4 dep layers rebuilt; the dsh-mcp registered) | local |
| Paperclip board | 🟡 (the tunnel live; the agents idle pending heartbeat) | Lab |
| B2 (6 buckets) | 🟢 (the 13.25GB synced; the cap blocks the rest) | cloud |
| Tailscale | 🟡 (the hermes-webui only; the Clinic/Lab/Edge links pending) | mesh |

## The crons (the 78 jobs)
- The ~30 erroring on the old qwen2.5:3b context drift — re-pinned to the llama3.1:8b 08-19; the next runs clear.
- The alert discipline: the script-mode jobs are silent-when-clean. The chat gets the CRITICAL only.

## The founder's gates (the 7 taps)
1. B2 billing card ($6/TB)
2. Apple dev key (TestFlight)
3. Perfex REST module ($149)
4. Kaggle Run All
5. Mirth admin password
6. GitHub write token (the monorepo push)
7. Granola API key (the meeting-notes lane)

## The build queue
- SCRAPPED (the founder 08-19): the Perfex TTS AJAX integration — the no sense in it; the Perfex stays the Oussama's lane, untouched. The voice stays in the Hermes loop (the piper + the ElevenLabs), not the CRM.
- SCRAPPED (the founder 08-19): the Grok harness compile — the study-only, the no runtime.
- The app screen fixes (the Scribe endpoint, the dead tiles, the E6B NaN, the stale test) — the APPLIED 08-19, the test retry pending
- The OHIF 401 · the Mirth MLLP ports · the vision engine wire
- The RadLex + the 13 datasets (post-B2) · the sovereign audit deploy
- The CompreFace · the TAK EMS plugin · the Forgejo
- The Med42-v2 + MedGemma · the SkillClaw/openmed/audit-triple-check studies
- The Hermes image upgrade (the watchdog armed — the waiting upstream)

## The standing watchdogs (the silent, the armed)
- hermes-image-watchdog · lab-intake-interpreter · the B2 sync queue · the tailscale-watchdog · the tunnel guardian · the 13 dream lessons (the founder's review)
