# OSINT Assessed Repos (Founder-shared, added 2026-09-05)

Assessed per the OSINT doctrine (verified-feeds / no-fabrication / dual-use handled honestly).

## anthropics/claude-for-legal (Apache-2.0, 8.2K★)
Legal-workflow plugin suite (commercial/privacy/corporate/employment/litigation/regulatory/IP/AI-governance agents + MCP connectors: Ironclad, DocuSign, iManage, Everlaw, CourtListener). Guardrail = every output is a draft for attorney review, source-attributed, no legal advice. NURA: reuse the governance/guardrail pattern; never replaces our counsel (Stavrou). Reg A "AI never signs" rule preserved.

## ruvnet/RuView (MIT, 91K★) — via Google share link
WiFi CSI sensing (ESP32) -> through-wall presence, contactless vitals, fall/activity/occupancy, drone-swarm module. Edge-only, RuVector memory, Ed25519 attestation. **DUAL-USE/security caveat:** presence-through-walls + vitals + drone swarm. OSINT-monitor/assess, NOT deploy-against-people. Self-corrected accuracy: v2 held-out temporal-triplet = 82.3%; pose PCK@20 ~2.5-3% (below target); several numbers synthetic until real-data validation.
