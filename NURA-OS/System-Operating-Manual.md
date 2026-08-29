# NURA SYSTEM OPERATING MANUAL — HOW EVERYTHING WORKS (2026-08-02)

*The complete description of the machine we built: components, workflows, and how it all comes together.*

---

## 1. THE ANATOMY (what exists)

### 🧠 The Brain — Hermes (NURA OS core)
One agentic core running on the Clinic node (KVM4, 16GB, s6-managed gateway). It holds: persistent memory (MEMORY.md/USER.md + Mem0/Qdrant), ~380 procedural skills (how-to libraries), a session DB (conversation history), cron scheduler (41 jobs), and the executive persona (J.A.R.V.I.S. cadence, evidence doctrine). The brain DOES: research, code, ops, drafting, delegation, verification — and NEVER claims unverified completion.

### 🕸️ The Nervous System — MCP Connector Lanes (61+)
Every external system is a lane, and EVERY lane follows the universal 4-surface standard: **API + MCP + CLI + WEBHOOK**.
- Clinical: OpenEMR (charts/labs/meds), openFDA/PubMed/CDC (evidence), provider_labs, Mirth (HL7/FHIR)
- Business: Perfex (CRM), Chatwoot (omnichannel), n8n (workflows), Paperclip (agent org), Notion (connector hub)
- Infrastructure: Hostinger VPS (62 tools — the only hands on the fleet), Redis, Qdrant, Docker
- AI: OpenRouter routing, Gemini in-house, sovereign Colibrì/GLM-5.2 (hummingbird), Bio_ClinicalBERT

### 🤖 The Org — Paperclip Agents (65)
Atlas (CEO) owns org/staff/revenue/ceremonies; Orion (CTO) owns technical builds; Iris (CMO), Midas (CFO), Advisor (10-CEO council), + specialists (Bridge = MCP developer, Loom = n8n, Tally = Perfex, Florence = OpenEMR, Meridian = Mirth, QA lead...). Hermes files directives → Atlas assigns → agents execute → **evidence posts back on the issue**. Zero hires without evidence.

### 🏗️ The Body — Hostinger Fleet (3 VPS)
- **Clinic** (1441409, 16GB) — Docker apps: n8n, Chatwoot, Mirth, Orthanc/PACS, Obsidian-LiveSync CouchDB (:5984), NPM; Hermes container
- **Lab** (1030183, 32GB) — AI workloads, datasets (behind NUR-110 gate)
- **Edge/Storefront** (817449, 4GB) — pay.nuratech.ai (Perfex storefront)
Doctrine: localhost-only except NPM 80/443; firewall rules complete BEFORE activation; 6h fleet health cron.

### 📓 The Memory — Obsidian Vault + RAG
Every decision, spec, diary, and doc lands in the vault (NURA-OS/, Life/, IP/, SEC/...). Vault feeds the RAG index (nura-docs, 470 chunks, fastembed 384d) so the brain retrieves its own history. Secrets NEVER enter the vault (they stay .env 0600).

### ⏰ The Heartbeat — Cron (41 jobs, EST wall-clock)
Cost digest Mon 06:30 · scrum Mon 09:00 · fleet health every 6h · license watchdog 1st of month 09:00 · CME Sun 18:00 · UAP watch 17:00 · Notion mirrors · 30-min/2h monitors. Silent-OK: all-green = one line; anomalies = details.

### 👔 The Governance — Board + Directives
10-CEO advisory council (Musk/Bezos/Zuckerberg/Hormozi/Johnson/Cardone/Jobs/Buffett/Nadella/Huang) — advisory only, never overrides the provider gate. Every consequential decision → board consult [D#] → banked to Advisory-Board.md. Atlas owns ceremonies (scrum/EOD/monthly).

### 🏢 The Companies (one nervous system, five nodes)
Nuratech core (SaaS/app) · Assurance (books) · Capital Markets (parked) · Aero (drones) · EMS Agency (MIH partnership). Musk model: every company is customer AND supplier of the others; Hermes Lattice = the connective tissue (like Anduril's Lattice: one operating picture).

### 📜 The Assets (IP + Securities)
Provisional patent DRAFT (NOT FILED — being redrafted via patent attorney; must file before Reg A qualification) · Reg A Offering Circular master draft v3.0 (WY corp, $20M common) · YC SAFE suite (team hired) · Musk-style founder comp plan (12 tranches) · Delaware IP HoldCo (planned).

---

## 2. THE WORKFLOWS (how work actually flows)

### A. Directive → Evidence loop (the core loop)
1. Founder (or cron) gives intent → Hermes converts to a **CEO directive** (tight scope, owners, dates, evidence requirements)
2. Posted to Paperclip board → **Atlas assigns** (owner per lane)
3. Agents execute → post **evidence** (receipts, outputs, screenshots) on the issue
4. Hermes verifies (live probe where external effects claimed) → reports to founder
5. Failure → lesson → **skill/memory/cron** (twice = FAIL doctrine)

### B. The daily cadence
- 06:30 cost digest · 09:00 scrum (Mon) · 17:00 UAP/disclosure · 18:00 CME (Sun) · 6h fleet sweep · monthly license watchdog · quarterly board portfolio review

### C. Build workflow (CTO discipline)
Concrete task → reversible dev ok → tests/evidence before "done" → verify-before-declare → label untested honestly → consolidate before reporting → no scope drift.

### D. Connector workflow (every new integration)
API client → MCP registered + smoke → CLI verbs → webhook in/out → auth sealed 0600 → health check → beneficiary test → BAA/PHI check → lane registry. Four surfaces minimum.

### E. Credential workflow
Seal .env 0600 · never echo · probe live before "connected" · ~/uploads/ drops from the founder · no secrets in vault/chat.

### F. Content/marketing workflow
Brand voice (Peptide PA) · weekly letter (Sun) · FB/IG engine (Manus-style, Iris) · clinical claims gate before any health marketing · compliance-aware.

---

## 3. HOW IT ALL COMES TOGETHER (the one system)

```
FOUNDER (all signal, rapid switching)
   │  every switch lands somewhere
   ▼
HERMES (brain: memory + skills + routing + verification)
   ├─ MCP lanes (nervous system: 61 connectors, 4-surface standard)
   ├─ PAPERCLIP (org: Atlas owns, agents execute, evidence back)
   ├─ FLEET (body: 3 VPS, Docker, firewalls, cron heartbeat)
   ├─ VAULT+RAG (memory: everything banked, retrievable)
   ├─ BOARD (governance: 10 CEOs advise, Atlas decides, founder approves)
   ├─ COMPANIES (5 nodes, one nervous system — each feeds the others)
   └─ ASSETS (IP → Reg A → SAFE → comp plan → capital)
        ▲
        └─ the money comes back and funds the next build
```

**The doctrine that holds it together:** evidence over invention · verify before declare · local-first · approval-gated · audit-friendly · one coherent answer · every failure becomes a lesson · every idea becomes an asset.

---

## 4. DISASTER RECOVERY (the backup)
- **Backup**: `~/uploads/nura-backup-2026-08-02.tar.gz` (47MB, 5,352 files — vault + data + scripts + config + skills + cron + memories + sealed .env)
- **Restore**: extract to /opt/data, re-seal .env 0600, gateway restarts naturally (never kill s6 children)
- **Cadence recommendation**: nightly automated backup (tar) + weekly uploads copy — founder to pull to iCloud

---

*Version 1.0 — written 2026-08-02. Every section maps to a real component with real files. No fiction.*
