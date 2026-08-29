# NURA CLINICAL PLATFORM — HERMES MULTI-AGENT ARCHITECTURE (2026-08-04, founder canonical v1.0)

**Target:** Hermes Agent (Nous Research) · **Purpose:** the Multi-Clinician Distributed AI Operating System.

## MISSION & DESIGN PHILOSOPHY
Hermes = a distributed OS supporting THOUSANDS of clinicians through isolated AI workspaces sharing one platform kernel. NOT a chatbot — the orchestration kernel for NURA Clinical. **One platform · many clinicians · many Hermes agents · one secure ecosystem · every clinician owns their own AI workforce.**

## CORE ARCHITECTURE
```
NURA Cloud Platform
├── Control Plane ────────┐
└── AI Gateway ───────────┘
        └── Hermes Gateway
              ├── Clinician A → Cloud Hermes + Desktop Hermes + Mobile Hermes
              ├── Clinician B → Cloud + Desktop + Mobile
              └── Clinician C → Cloud + Desktop + Mobile
```

## EVERY CLINICIAN RECEIVES (the isolated workspace)
Cloud Hermes · Desktop Hermes · Mobile Hermes · Private Memory · Private Database · Private Vector Database · Private API Keys · Private EMR Credentials · Private Audit Logs · Private Settings. **No clinician may access another's workspace.**

## AGENT TYPES
- **Cloud Hermes (24/7):** orchestration · workflow engine · memory sync · long-term memory · scheduling · event routing · API gateway · auth · audit · clinical orchestration · background jobs.
- **Desktop Hermes:** local GPU inference · coding · Docker · Flutter builds · VS Code · Claude Code · Codex CLI · Playwright · local document + voice processing · local automation. **NEVER exposes local resources directly to the Internet — Cloud requests work through the Gateway.**
- **Mobile Hermes:** offline operation · voice assistant · clinical note capture · camera · OCR · barcode · Bluetooth medical devices · sync — **must continue functioning without connectivity.**

## COMMUNICATION
**A2A (agent-to-agent) — structured messages only, never prompt injection.** Example: {"type":"task","source":"cloud-hermes","destination":"desktop-hermes","action":"build_flutter","project":"NURA Mobile","priority":"normal"}.
**Transport preference:** 1. Hermes Gateway → 2. MCP → 3. NATS JetStream → 4. Redis Streams → 5. RabbitMQ. **Avoid direct REST whenever possible.**

## SHARED MEMORY (per clinician — never mixed)
PostgreSQL Schema · Redis Namespace · Qdrant Collection · S3 Bucket Prefix.

## IDENTITY
Every Hermes has: Agent ID (agent_01) · Workspace ID (workspace_452) · Tenant ID (tenant_medisun) · Device ID (desktop_001) · Session ID (session_xxx).

## CAPABILITY ADVERTISEMENT & DISCOVERY
Each agent publishes capabilities (docker · flutter · gpu · vscode · playwright · git · ollama · codex · claude...). Cloud discovers automatically — **never hardcode endpoints.** Task routing: Cloud receives "Build Flutter" → searches the capability registry → Desktop supports Flutter → assigns → Desktop builds → returns the artifact → Cloud deploys.

## AGENT PERMISSIONS (minimum necessary)
- **Desktop allowed:** build software · Docker · local files · local GPU. **Denied:** modify EMR · prescribe · delete cloud databases.
- **Cloud allowed:** workflow · scheduling · EMR · CRM · notifications. **Denied:** local file system.

## CLINICAL SAFETY (non-negotiable)
Hermes SHALL NEVER: diagnose autonomously · prescribe autonomously · sign notes · approve billing · order medications · release critical results · perform irreversible actions. **Provider approval required. ALWAYS.** Every clinical action awaiting authorization: `status: pending_provider_review` until approved.

## MULTI-TENANT ISOLATION
Dedicated per clinician: database · memory · vector store · Redis namespace · encryption keys · audit logs · API credentials. **Never share.**

## SECURITY
TLS · mTLS where possible · JWT · OAuth2 · RBAC · device certificates · **all API calls signed.**

## LOGGING (every action)
{"timestamp","tenant","clinician","agent","device","workflow","tool","duration","status"}.

## SYNCHRONIZATION (incremental — never resend entire conversations)
Desktop → Gateway → Cloud → Database → Other Agents. Only sync: changes · new memory · updated vectors · new files.

## TOKEN CONSERVATION
Never resend full context. Maintain: Conversation Summary · Entity Memory · Active Task · Working Memory · Vector References — retrieve only the required context.

## REGISTRIES
- **Agent Registry** (via the Gateway): name · version · capabilities · health · last heartbeat · workspace · tenant · model · available memory · GPU · tools.
- **Tool Registry** (central): OpenEMR · Perfex · Chatwoot · Twilio · Mirth · Orthanc · OHIF · ThaiRIS · OpenEvidence · PubMed · FDA · Bluetooth · FHIR · HL7 · S3 · RunPod · Supabase · Redis · Qdrant · PostgreSQL.
- **Device Registration:** unique certificate · device ID · device token · workspace assignment · automatic revocation.

## UPDATES & FAILURE HANDLING
Cloud pushes skills/prompts/policies/models/tool definitions — Desktop auto-updates AFTER verification. **Desktop down → Cloud continues. Cloud down → Desktop continues locally. Restored → auto-sync. No data loss.**

## SCALABILITY (no redesign)
1 → 10 → 100 → 1,000 → 10,000 clinicians.

## FUTURE AGENTS (all register identically)
Radiology · Pathology · Laboratory · Cardiology · Oncology · Legal · Compliance · Finance · Coding · Billing · Scheduling · Research · Pharmacy · **Robot Hermes (Ratchet)** · Drone Hermes · Space Medicine Hermes.

## THE DEPLOYMENT PHILOSOPHY
Hermes is a distributed operating system. Every clinician owns their own AI workforce. The NURA Cloud Platform manages those workforces through secure orchestration, shared governance, strict tenant isolation, and continuous synchronization — preserving clinician autonomy and patient safety.

---

## THE NURA MAP (how this lands on what we have)
- **The NUR-106 per-tenant doctrine = THIS spec's spine** (the SaaS-first: per-tenant schema/namespace/collection/prefix — the hermes-saas-productization skill's architecture).
- The Hermes Gateway = the existing gateway (the multi-channel kernel) · the transport ladder (MCP/NATS/Redis) = the lanes we already run (MCP 40+ · Redis redis-gc8b · the event bus roadmap).
- The Cloud/Desktop/Mobile triad = the surfaces we're wiring (the desktop connect tonight! · the mobile app · the cloud = this box).
- The safety doctrine = unchanged (AI drafts, providers sign, pending_provider_review until approved).
- The scale path: Medisun (tenant_medisun!) = the first tenant → the lighthouse → the SaaS (the Reg A story).
