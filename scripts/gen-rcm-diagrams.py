#!/usr/bin/env python3
"""NURATECH RCM Platform — architecture diagram pack (12 diagrams, dark SVG/HTML)."""
import html

def esc(s): return html.escape(s)

def box(x, y, w, h, label, sub="", kind="backend"):
    fill = {"fe": "rgba(8,51,68,0.4)", "be": "rgba(6,78,59,0.4)", "db": "rgba(76,29,149,0.4)",
            "cloud": "rgba(120,53,15,0.3)", "sec": "rgba(136,19,55,0.4)", "bus": "rgba(251,146,60,0.3)",
            "ext": "rgba(30,41,59,0.5)"}[kind]
    stroke = {"fe": "#22d3ee", "be": "#34d399", "db": "#a78bfa", "cloud": "#fbbf24",
              "sec": "#fb7185", "bus": "#fb923c", "ext": "#94a3b8"}[kind]
    ly = y + h / 2 - 6 if sub else y + h / 2 + 4
    return (f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="6" fill="#0f172a"/>'
            f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="6" fill="{fill}" stroke="{stroke}" stroke-width="1.5"/>'
            f'<text x="{x+w/2}" y="{ly}" text-anchor="middle" font-size="12" fill="#e2e8f0" font-family="JetBrains Mono, monospace">{esc(label)}</text>'
            + (f'<text x="{x+w/2}" y="{y+h/2+9}" text-anchor="middle" font-size="9" fill="#94a3b8" font-family="JetBrains Mono, monospace">{esc(sub)}</text>' if sub else ""))

def arr(x1, y1, x2, y2, color="#64748b", dash=""):
    return (f'<line x1="{x1}" y1="{y1}" x2="{x2}" y2="{y2}" stroke="{color}" stroke-width="1.5" marker-end="url(#ah)" {dash}/>')

def svg(w, h, body):
    return (f'<svg viewBox="0 0 {w} {h}" xmlns="http://www.w3.org/2000/svg" style="width:100%;height:auto">'
            f'<defs><marker id="ah" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="7" markerHeight="7" orient="auto-start-reverse">'
            f'<path d="M 0 0 L 10 5 L 0 10 z" fill="#64748b"/></marker></defs>'
            f'<pattern id="grid" width="40" height="40" patternUnits="userSpaceOnUse">'
            f'<path d="M 40 0 L 0 0 0 40" fill="none" stroke="#1e293b" stroke-width="0.5"/></pattern>'
            f'<rect width="{w}" height="{h}" fill="url(#grid)"/>{body}</svg>')

def section(title, sub, diagram):
    return (f'<div class="diagram"><div class="dhead"><span class="dot"></span><h2>{esc(title)}</h2>'
            f'<span class="dsub">{esc(sub)}</span></div>{diagram}</div>')

CSS = """
body{background:#020617;color:#e2e8f0;font-family:'JetBrains Mono',monospace;margin:0;padding:24px}
header{display:flex;align-items:center;gap:14px;margin-bottom:8px}
h1{font-size:20px;margin:0}
.sub{color:#94a3b8;font-size:12px;margin-bottom:24px}
.dot{width:10px;height:10px;border-radius:50%;background:#34d399;animation:pulse 2s infinite}
@keyframes pulse{0%,100%{opacity:1}50%{opacity:.3}}
.diagram{background:#0f172a;border:1px solid #1e293b;border-radius:12px;padding:18px;margin-bottom:22px}
.dhead{display:flex;align-items:center;gap:10px;margin-bottom:12px}
.dhead h2{font-size:14px;margin:0;color:#22d3ee}
.dsub{color:#64748b;font-size:10px}
footer{color:#475569;font-size:10px;margin-top:16px;text-align:center}
"""

D = []
# ---- D1 System overview
d1 = svg(900, 520,
  box(40, 20, 260, 70, "NURATECH Clinics", "North Miami · Little Haiti · Ft. Lauderdale", "fe") +
  box(340, 20, 220, 70, "Patients", "285 MA · RAF 1.27 · PMPM $360", "fe") +
  box(600, 20, 260, 70, "Billing Manager", "Human approval gate", "sec") +
  arr(300, 55, 340, 55) + arr(560, 55, 600, 55) +
  box(40, 150, 260, 90, "Clinical Systems", "EMM EMR · HIE · MyChart", "ext") +
  box(330, 150, 240, 90, "Operational Systems", "GoHighLevel CRM · Perfex ERP", "be") +
  box(600, 150, 260, 90, "Imaging Systems", "Orthanc PACS · OHIF Viewer", "cloud") +
  arr(170, 120, 170, 150) + arr(450, 120, 450, 150) + arr(730, 120, 730, 150) +
  box(40, 300, 260, 90, "HERMES AGENT", "Agentic RCM Platform", "be") +
  box(330, 300, 240, 90, "Communications", "SMS · Email · FB/IG/LinkedIn · Voice", "bus") +
  box(600, 300, 260, 90, "AI Infrastructure", "Mac Studio M3 Ultra · External LLMs", "cloud") +
  arr(170, 240, 170, 300) + arr(450, 240, 450, 300) + arr(730, 240, 730, 300) +
  box(330, 440, 240, 60, "Supabase Postgres", "pgvector memory", "db") +
  box(600, 440, 260, 60, "Deterministic Rules Engine", "ICD-10 → HCC · RAF calc", "sec") +
  arr(450, 390, 450, 440) + arr(730, 390, 730, 440))
D.append(("D1 — System Overview", "End-to-end platform layers", d1))

# ---- D2 RCM workflow
steps = ["Chart Retrieval", "Diagnosis Extraction", "ICD-10 Coding", "HCC Classification", "RAF Calculation", "Denial Risk", "Billing Mgr Review", "Claim Release"]
d2 = []
for i, s in enumerate(steps):
    x = 30 + i * 110
    kind = "sec" if s in ("Billing Mgr Review",) else ("db" if s == "RAF Calculation" else "be")
    d2.append(box(x, 180, 90, 60, s, "", kind))
    if i < 7: d2.append(arr(x + 90, 210, x + 110, 210))
d2.append(box(30, 100, 200, 50, "AI-assisted (no autonomy)", "rules + approvals", "bus"))
d2.append(box(660, 100, 210, 50, "Audit log every step", "approvals + traces", "sec"))
d2.append(svg(940, 280, "".join(d2)))
D.append(("D2 — RCM Workflow", "Chart to claim release", d2[-1]))

# ---- D3 Agents
d3 = svg(940, 460,
  box(370, 20, 200, 60, "ORCHESTRATOR", "Claude MCP · tool/model routing", "bus") +
  box(40, 140, 180, 60, "Connector Agent", "EMR · CRM · ERP · PACS · HIE", "be") +
  box(250, 140, 180, 60, "Chart Retrieval", "clinical history", "be") +
  box(460, 140, 180, 60, "Diagnosis Discovery", "chart text → candidates", "be") +
  box(670, 140, 180, 60, "Coding Agent", "ICD-10 recommendations", "be") +
  box(40, 260, 180, 60, "HCC / RAF Agent", "CMS risk adjustment", "be") +
  box(250, 260, 180, 60, "Denial Intelligence", "denial risk prediction", "be") +
  box(460, 260, 180, 60, "Communication Agent", "patient messaging", "be") +
  box(670, 260, 180, 60, "Voice Agent", "telephony automation", "be") +
  box(370, 370, 200, 60, "Memory Agent", "long-term outcomes", "db") +
  arr(470, 80, 130, 140) + arr(470, 80, 340, 140) + arr(470, 80, 550, 140) + arr(470, 80, 760, 140) +
  arr(130, 200, 130, 260) + arr(340, 200, 340, 260) + arr(550, 200, 550, 260) + arr(760, 200, 760, 260) +
  arr(470, 320, 470, 370))
D.append(("D3 — Agent Architecture", "9 specialized agents + orchestrator + memory", d3))

# ---- D4 Local AI
d4 = svg(900, 360,
  box(300, 20, 300, 70, "Mac Studio M3 Ultra", "local AI compute · PHI stays local", "cloud") +
  box(60, 140, 170, 60, "Ollama Runtime", "local LLM serving", "be") +
  box(250, 140, 170, 60, "ClinicalBERT", "clinical text extraction (MLM)", "be") +
  box(440, 140, 170, 60, "GatorTron", "clinical NLP (MLM)", "be") +
  box(630, 140, 170, 60, "Embedding Models", "vectorization", "db") +
  box(250, 250, 400, 60, "OCR Pipeline", "document understanding", "be") +
  box(60, 250, 170, 60, "External LLMs", "OpenAI · Claude · Perplexity", "ext") +
  arr(450, 90, 145, 140) + arr(450, 90, 335, 140) + arr(450, 90, 525, 140) + arr(450, 90, 715, 140) +
  arr(450, 200, 450, 250) + arr(145, 200, 145, 250))
D.append(("D4 — Local AI Infrastructure", "PHI-safe local inference + external fallback", d4))

# ---- D5 Data
d5 = svg(900, 380,
  box(40, 20, 400, 80, "Supabase Postgres (primary)", "patients · encounters · documents · diagnosis_candidates", "db") +
  box(460, 20, 400, 80, "pgvector (vector memory)", "coding decisions · payer policies · denial outcomes · patterns", "db") +
  box(40, 140, 260, 60, "icd10_codes", "code reference", "db") +
  box(320, 140, 260, 60, "hcc_mappings", "CMS hierarchy", "db") +
  box(600, 140, 260, 60, "raf_scores", "risk scores", "db") +
  box(40, 240, 260, 60, "billing_tasks", "work queue", "db") +
  box(320, 240, 260, 60, "approvals", "human-in-loop", "sec") +
  box(600, 240, 260, 60, "audit_logs", "agent_runs · traces", "sec") +
  arr(240, 100, 170, 140) + arr(450, 100, 450, 140) + arr(660, 100, 730, 140) +
  arr(170, 200, 170, 240) + arr(450, 200, 450, 240) + arr(730, 200, 730, 240))
D.append(("D5 — Data Architecture", "Core tables + vector memory", d5))

# ---- D6 Microservices
svcs = ["api-gateway", "identity", "connectors", "normalization", "retrieval", "embeddings", "memory", "diagnosis-discovery", "coding-recommendation", "rules-engine", "denial-intelligence", "communications", "voice", "workflow", "audit", "evaluation"]
d6b = []
for i, s in enumerate(svcs):
    r, c = divmod(i, 4)
    d6b.append(box(60 + c * 210, 140 + r * 90, 180, 60, s, "", "be" if s not in ("rules-engine", "audit") else "sec"))
d6b.append(box(60, 40, 780, 60, "API Gateway", "authN · routing · rate limit", "bus"))
for i in range(4): d6b.append(arr(160 + i * 210, 100, 160 + i * 210, 140))
d6b.append(svg(900, 460, "".join(d6b)))
D.append(("D6 — Microservices", "16 modular service domains", d6b[-1]))

# ---- D7 Comms
d7 = svg(900, 320,
  box(340, 20, 220, 60, "GoHighLevel CRM", "central comms hub", "be") +
  box(60, 140, 160, 60, "SMS", "reminders", "fe") +
  box(240, 140, 160, 60, "Email", "templates", "fe") +
  box(420, 140, 160, 60, "Facebook Messenger", "2-way", "fe") +
  box(600, 140, 160, 60, "Instagram", "2-way", "fe") +
  box(60, 240, 160, 60, "LinkedIn", "2-way", "fe") +
  box(240, 240, 160, 60, "iMessage", "2-way", "fe") +
  box(420, 240, 340, 60, "Appointment · Billing · Follow-up · Responses", "orchestrated by Comms Agent", "bus") +
  arr(450, 80, 140, 140) + arr(450, 80, 320, 140) + arr(450, 80, 500, 140) + arr(450, 80, 680, 140) +
  arr(140, 200, 140, 240) + arr(320, 200, 320, 240) + arr(500, 200, 590, 240))
D.append(("D7 — Communications", "Channels via GHL", d7))

# ---- D8 Voice
d8 = svg(900, 300,
  box(40, 100, 180, 60, "SIP Trunk Provider", "carrier", "ext") +
  box(260, 100, 200, 60, "PBX", "Voice/PBX Manager", "be") +
  box(500, 100, 180, 60, "Voice Agent", "call automation", "be") +
  box(720, 100, 160, 60, "GHL + Task System", "records", "be") +
  box(260, 220, 420, 50, "Transcription · Voicemail analysis · Call summaries", "→ Hermes tasks", "bus") +
  arr(220, 130, 260, 130) + arr(460, 130, 500, 130) + arr(680, 130, 720, 130) +
  arr(500, 160, 500, 220) + arr(600, 160, 600, 220))
D.append(("D8 — Voice / PBX", "SIP → PBX → Voice Agent → tasks", d8))

# ---- D9 Imaging
d9 = svg(900, 300,
  box(40, 110, 160, 60, "X-ray Acquisition", "modality", "ext") +
  box(240, 110, 170, 60, "Orthanc PACS", "DICOM storage", "db") +
  box(450, 110, 160, 60, "OHIF Viewer", "reading UI", "fe") +
  box(650, 110, 210, 60, "Report Processing", "→ RAG memory", "be") +
  arr(200, 140, 240, 140) + arr(410, 140, 450, 140) + arr(610, 140, 650, 140))
D.append(("D9 — Imaging Integration", "X-ray → PACS → Viewer → RAG", d9))

# ---- D10 HIE
hosp = ["Jackson Memorial", "University of Miami", "UM Health System", "North Shore Medical", "Broward Health", "Memorial Healthcare"]
d10b = []
for i, h in enumerate(hosp):
    d10b.append(box(40 + (i % 3) * 290, 140 + (i // 3) * 90, 250, 60, h, "", "ext"))
d10b.append(box(300, 20, 300, 60, "Regional HIE Networks", "discharge · encounters · consults · imaging", "bus"))
d10b.append(box(300, 340, 300, 60, "Hermes Agent", "normalize → memory → work", "be"))
for i in range(6):
    x = 165 + (i % 3) * 290
    y = 140 + (i // 3) * 90
    d10b.append(arr(x, 80 if i < 3 else 200, x, y))
d10b.append(arr(450, 80, 450, 340) if False else arr(450, 200, 450, 340))
d10b.append(svg(940, 440, "".join(d10b)))
D.append(("D10 — Hospital / HIE Integration", "6 target networks → Hermes", d10b[-1]))

# ---- D11 Environments
envs = ["Development", "Integration", "Simulation", "Staging", "Production", "Local Fallback"]
d11b = []
for i, e in enumerate(envs):
    kind = "ext" if e == "Local Fallback" else ("sec" if e == "Production" else "be")
    d11b.append(box(40 + i * 140, 160, 110, 70, e, "de-identified" if e == "Simulation" else ("live supervised" if e == "Production" else "local inference" if e == "Local Fallback" else ""), kind))
    if i < 5: d11b.append(arr(150 + i * 140, 195, 150 + i * 140 + 30, 195))
d11b.append(box(40, 60, 820, 50, "Promotion gates: tests → integration → sim validation → staging → prod (human-supervised)", "", "bus"))
d11b.append(svg(920, 280, "".join(d11b)))
D.append(("D11 — Deployment Environments", "Dev → Prod + local fallback", d11b[-1]))

# ---- D12 Security
d12 = svg(900, 320,
  box(340, 20, 220, 60, "Keycloak / Auth0", "identity provider", "sec") +
  box(40, 140, 200, 60, "Role-Based Access", "RBAC per role", "sec") +
  box(260, 140, 200, 60, "Encrypted Storage", "AES-256 at rest", "sec") +
  box(480, 140, 200, 60, "API AuthN", "OAuth2 · tokens", "sec") +
  box(700, 140, 160, 60, "Audit Logging", "PHI access tracking", "sec") +
  box(40, 250, 820, 50, "All AI actions gated: Billing Manager approval · deterministic rules · full trace", "", "bus") +
  arr(450, 80, 140, 140) + arr(450, 80, 360, 140) + arr(450, 80, 580, 140) + arr(450, 80, 780, 140) +
  arr(450, 200, 450, 250))
D.append(("D12 — Security & Governance", "Identity · RBAC · audit · approvals", d12))

# ---- Assemble
cards = ""
for i, (t, s, _) in enumerate(D[:3]):
    cards += f'<div class="card"><div class="card-header"><div class="card-dot {"cyan" if i==0 else "green" if i==1 else "violet"}"></div><h3>{esc(t)}</h3></div><ul><li>• {esc(s)}</li></ul></div>'

body = "".join(f'<div class="diagram"><div class="dhead"><span class="dot"></span><h2>{esc(t)}</h2><span class="dsub">{esc(s)}</span></div>{d}</div>' for t, s, d in D)
page = f"""<!DOCTYPE html><html><head><meta charset="utf-8"><title>NURATECH RCM Platform — Architecture Diagram Pack</title>
<link href="https://fonts.googleapis.com/css2?family=JetBrains+Mono:wght@400;700&display=swap" rel="stylesheet">
<style>{CSS}
.card{{background:#0f172a;border:1px solid #1e293b;border-radius:12px;padding:14px}}
.card-header{{display:flex;align-items:center;gap:8px}}
.card-header h3{{font-size:12px;margin:0}}
.card-dot{{width:8px;height:8px;border-radius:50%}}
.card-dot.cyan{{background:#22d3ee}}.card-dot.green{{background:#34d399}}.card-dot.violet{{background:#a78bfa}}
.cards{{display:grid;grid-template-columns:repeat(3,1fr);gap:14px;margin:14px 0 22px}}
ul{{margin:8px 0 0;padding-left:16px;font-size:10px;color:#94a3b8}}
</style></head><body>
<header><span class="dot"></span><h1>NURATECH.ai — Agentic RCM Platform (Hermes)</h1></header>
<div class="sub">Architecture diagram pack · 12 diagrams · CTO master plan 2026-08-02 · dark SVG (no deps)</div>
<div class="cards">{cards}</div>
{body}
<footer>NURATECH.ai Technology Master Plan — Hermes agent · generated by Hermes Agent (architecture-diagram skill)</footer>
</body></html>"""
with open("/opt/data/home/nura-clinical-platform/docs/diagrams/rcm-architecture-pack.html", "w") as f:
    f.write(page)
import os
print("WROTE", os.path.getsize("/opt/data/home/nura-clinical-platform/docs/diagrams/rcm-architecture-pack.html"), "bytes,", len(D), "diagrams")
