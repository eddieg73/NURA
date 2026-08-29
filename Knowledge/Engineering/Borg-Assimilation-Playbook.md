# Borg Assimilation Playbook — Legal Capability Capture for NURA

**Goal:** expand NURA by incorporating capability from GitHub OSS and open-weight AI — legally, attribution-clean, copyleft-aware, audit-ready.
**Doctrine:** "Take what we need" = *capability capture* is legal; *code/weight copying from closed/proprietary sources* is not. Every assimilation passes the license gate first.

## 1. Allowed source classes (green-light)
- **Permissive OSS** (MIT / Apache-2.0 / BSD / ISC / MPL): integrate freely; keep LICENSE + copyright notices; record in SBOM/attribution manifest.
- **Open-weight AI models** per their license: MIT (DeepSeek-R1/V3, some), Apache-2.0 (Mistral, some), Llama community license (attribution + MAU ~700M cap), etc.
- **Public/standard APIs** (FHIR, HL7 v2, REST, SMART-on-FHIR): integrate via documented interface.
- **Clean-room reimplementation** of a black-box behavior/feature you want, built from scratch (never copying source).
- **Our own software / fleet:** deploy it, modify it freely (Mirth, OpenEMR, our modules).

## 2. License gate (run BEFORE any code is merged)
| License | Verdict | Action |
|---|---|---|
| MIT / Apache-2.0 / BSD / ISC / MPL | ✅ | Integrate + record attribution |
| LGPL | ✅ | Keep as separate library (dynamic link ideal) |
| GPL / AGPL (copyleft) | ⚠️ | Only if we ship that component GPL; else clean-room reimplement |
| **No license / UNLICENSED** | ❌ | All rights reserved — need written permission; skip unless obtained |
| Model license (Llama/club/etc.) | ✅ | Honor attribution + usage caps in the manifest |

GFDL/CC-BY is fine for docs; CC-BY-NC is **not** for commercial use. Commercial-use restrictions → LEXA review.

## 3. The pipeline (how a capability gets assimilated)
1. **Discovery** — find candidate repo/model; capture name, stars, last-commit, license file, primary language. Add to `awesome-osint-arsenal-tools.json` (or a NURA-specific `assimilation-index`).
2. **License gate** — read LICENSE/COPYING/PACKAGE metadata; classify per the matrix; **fail-closed** if ambiguous or missing.
3. **SBOM + attribution manifest** — record component, version, license, vendor, source URL, copyright holder. This is the audit trail (use `cyclonedx`/`syft` + a `THIRD_PARTY_NOTICES.md`).
4. **Security/dependency scan** — `trivy`, `gitleaks` (secrets), `semgrep`/`bandit` (SAST) before merge; flag supply-chain risk (A03 Software Supply Chain Failures).
5. **Integrate + test** — add tests; keep a clean-room path when GPL/no-license blocks direct copy.
6. **Attribution & docs** — put it in `THIRD_PARTY_NOTICES.md` + lockfiles; document in the build diary / Notion.
7. **Route gray cases to LEXA** — license ambiguity, copyleft concerns, commercial-use restrictions, or any "can we reuse X?" question → LEXA before code.

## 4. Hard exclusion list (never do)
- Decompile/copy a **closed-source / proprietary** application's internals.
- Bypass DRM, license checks, or access protections (DMCA §1201).
- Copy another service's **private model weights** or resell an AI service through an unauthorized proxy.
- Reuse **no-license** code without explicit written permission.
- Incorporate copyleft (GPL/AGPL) code into a closed component without honoring the copyleft (unless we accept GPL for that component).

## 5. NURA-specific AI assimilation targets
- **Open-weight models:** DeepSeek-R1/V3 (MIT) for local inference; Mistral (Apache-2.0); Llama-club models for the sovereign Ollama lane; Needle 2 (tool-caller) as LOM brain.
- **Clinical OSS:** Medplum (FHIR), HAPI FHIR, Mirth Connect/OIE, OpenEMR, GoHighLevel/open-source langchain/langgraph, Deep Agents.
- **Agent/automation OSS:** LangGraph (MIT), superset, n8n (OSS), docs/knowledge base stacks.

## 6. Operating note
Treat this as living: on every new component added, run the license gate + update the manifest; when the founder names a target repo/model, route it through this playbook and record the verdict.
