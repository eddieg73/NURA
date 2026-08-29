# OSINT · Red/Blue Security Techniques Reference — NURA Internal KB

**Purpose:** durable internal knowledge base of offensive (red/black-hat tradecraft), defensive (white-hat), and recovery techniques — for **authorized** vulnerability testing and internal recovery only.
**Scope doctrine (non-negotiable):** white-hat only; authorized/owned targets; read-only by default; RoE + deconfliction before any engagement; **no PHI**, no live production mutation, snapshot-before-mutate, leave-no-residue. Aligned with NetworkChuck's "you have permission" legal-ethical-hacking ethos and hackathon-style bounded, authorized events.
**Companion:** `/opt/data/osint-cache/awesome-osint-arsenal-tools.json` (curated OSINT arsenal: learning-resources, malware-threat-intel, domain-ip-network, recon, etc.).

---

## 0. Governing frameworks (the map)
- **MITRE ATT&CK v18 (Enterprise)** — 14 Tactics, 216 Techniques, 475 Sub-Techniques. The shared language for both offense and detection. → `attack.mitre.org`
- **OWASP Top 10:2025** — A01 Broken Access Control, A02 Security Misconfiguration, A03 Software Supply Chain Failures, A04 Cryptographic Failures, A05 Injection, A06 Insecure Design, A07 Authentication Failures, A08 Software/Data Integrity Failures, A09 Security Logging & Alerting Failures, A10 Mishandling of Exceptional Conditions. → `owasp.org/Top10/2025/`
- **PTES** (Penetration Testing Execution Standard) — Pre-engagement → Intel gathering → Threat model → Vuln analysis → Exploitation → Post-exploit → Reporting.
- **OWASP WSTG** — Web Security Testing Guide (the per-technique test checklist).
- **NIST SP 800-61 IR lifecycle** — Prepare → Detect/Identify → Contain → Eradicate → Recover → Post-incident/lessons.
- **Kill chain / Diamond model** — mapping attacker action → attribution → detection.

---

## PART A — OFFENSIVE / RED (tradecraft, for authorized testing)
Organized by ATT&CK tactic; each row = technique class + tool/class you'd use in a **scoped lab or authorized target**.

### A1 Recon (Tactics: Reconnaissance / Initial Access prep)
- **OSINT footprint** — domain/IP/WHOIS, subdomain enum (`Amass`, `subfinder`), cert transparency (`crt.sh`), DNS (`dnsrecon`, `massdns`), Shodan/FOFA/Censys, Wayback, GitHub/GitLab code search (secrets), Google dorks.
- **Passive vs active** — passive first (no packets to target) then active on authorized scope only.
- **Scope discipline** — enumerate ONLY in-scope domains/IPs; record the engagement scope before touching.

### A2 Initial Access
- **Web/app exploitation** — OWASP A01–A10; SQLi (`sqlmap`), XSS, SSRF, IDOR/access-control, auth bypass, deserialization, file upload, command injection.
- **Social / phishing** — email, credential harvesting (only with explicit authorization; use your OWN throwaway infra, never a live victim).
- **Exposed services** — default creds, unpatched CVEs, exposed admin panels, open ports (`nmap`, `masscan`).

### A3 Execution & Persistence
- **System/script proxy execution** — `rundll32`, `regsvr32`, PowerShell, WMI, scheduled tasks, services, init/systemd units, DLL sideloading, office macros (Windows) / cron, .bashrc, systemd (Linux).
- **Docker/K8s/container** — container escape, exposed Docker API, registry secrets, `docker exec`, mounted secrets.

### A4 Privilege Escalation
- Linux: SUID/SGID, sudo misconfig, capability abuse, kernel CVEs, `docker`/`lxd` groups, cron, NFS, weak `/etc/passwd`.
- Windows: `Potato`/token impersonation, service misconfig, `AlwaysInstallElevated`, UAC bypass, `SeImpersonate`/`SeDebug`.
- Cloud/IaC: over-privileged roles, metadata SSRF (`169.254.169.254`), misconfigured IAM, exposed secrets.

### A5 Defense Evasion & Impair Defenses
- **Obfuscation** — base64, XOR, staged loaders, packing, fileless memory-only.
- **Log/monitoring tamper** — clear event logs, disable audit, drop/alter rules.
- **Masquerading** — rename tools, valid accounts, false flags.

### A6 Credential Access
- OS cred dumping (`Mimikatz`, `secretsdump`, `lsass`), password stores (browser, credential manager, keychain), Kerberos (`Rubeus`, ticket forging), cloud metadata API, `.env`/config stash, SSH keys.
- **Offline crack** — hashcat/john with wordlists + masks (offline only).

### A7 Discovery & Lateral Movement
- Discovery: `whoami`, netstat, `ps`, LDAP/AD queries, SMB (`enum4linux`, `crackmapexec`), cloud SSRF.
- Lateral: SMB/WMI/WinRM (`psexec`, `impacket`), SSH, pass-the-hash/ticket, credential reuse, cloud asset pivoting.

### A8 Collection, C2, Exfiltration
- Collection: screenshots, clipboard, keylog, email, cloud storage.
- **C2** — beacons, DNS/HTTPS tunnels, web shells, `Cobalt Strike`/`Sliver`/`Mythic` (authorized).
- Exfil: HTTP/S, DNS tunneling, cloud upload, alternate protocols.

### A9 Impact
- Ransomware/wipe, DDoS, data destruction, defacement — understand the blast radius to build **prevention + recovery**, never to execute on live.

---

## PART B — DEFENSIVE / BLUE (white-hat, detection & hardening)
### B1 Asset discovery & vulnerability management
- Asset inventory (`Amass`, `nmap`), vuln scan (`OpenVAS/GVM`, `Nessus`, `Trivy`), source/SAST (`Semgrep`, `Bandit`, `gitleaks`), dependency (`Trivy`, `Syft`, `OSV`).

### B2 Network monitoring & detection
- `Suricata` / `Snort` (IDS/IPS), `Zeek` (metadata), `Wireshark`/`tcpdump` (packet), `Security Onion`, `Elastic/SIEM`.

### B3 endpoint security & detection
- `Sysmon` (Windows event detail), `Wazuh`, `Velociraptor` (DFIR + live), `osquery`, EDR/XDR concepts, syslog/auditd (Linux).

### B4 Threat intelligence
- `MISP`, `OpenCTI`, `MITRE ATT&CK`, `AbuseIPDB`, `abuse.ch` (malware intel), STIX/TAXII feeds, YARA rules.

### B5 Phishing analysis & defense
- `urlscan.io`, `VirusTotal`, `Any.Run`, sandboxes, email headers/DKIM/SPF/DMARC check.

### B6 Crypto & secrets hygiene
- `OpenSSL`/`GnuPG`, TLS, `gitleaks`/`trufflehog`/`detect-secrets` for repo secrets, vault/KMS, SSH key mgmt.

---

## PART C — RECOVERY (internal, our own systems)
### C1 Backup & restore
- Verified backups: hot + cold + offsite; test-restore drill; RPO/RTO; immutable/object-lock copies. Use storage doctrine: Postgres=state, B2=binary/durable object storage, Redis=transient, Hermes=event refs.
### C2 Incident response workflow (NIST 800-61)
- Prepare → Identify → Contain (isolate host/ip/cred) → Eradicate (patch/rm implant, rotate creds) → Recover (restore from clean backup, verify) → Post-incident (lessons, detections, telemetry).
- **Containment tooling**: `TheHive`, `IRIS`, `DFIRTrack`, `FIR`, `GRR`, `Velociraptor`.
### C3 Forensic recovery / evidence
- Disk/memory image (`FTK Imager`, `KAPE`, `DumpIt`), memory analysis (`Volatility`), artifact parsing (`Autopsy`, `Plaso`, `DFIR ORC`), timeline tools, log analysis.
### C4 Credential & access recovery
- Rotate ALL exposed secrets; revoke sessions/tokens (the pasted `fmp_` key scenario); re-audit SSH keys/API keys/GCP/AWS; check cloud metadata + IAM after a compromise.
### C5 Data destruction / ransomware recovery
- Immutable backups, offline copies, isolate & don't pay; identify encryption scope; restore from last clean snapshots; re-stage environment (containerized fleet = rebuild-from-image).
### C6 Lessons → hardening
- Turn every incident into a detection rule (Sigma), a playbook, and a hardened config (pipeline: fixed error → memory → skill → cron per doctrine).

---

## PART D — NURA-specific targets (internal, authorized)
Our stack to test/recover (all owned): Hostinger VPS fleet (Docker), Perfex (pay/management), OpenEMR FHIR, Mirth/OIE 4.6.0, n8n, Redis, Qdrant, Postgres, Hermes gateway, Tailscale mesh, docs stack.
- **Webhook/config integrity**: the module's `fmp_` token format is `^fmp_[a-f0-9]{48}$` — any key matching that in a repo/bundle is a real secret to flag (gitleaks rule).
- **Mirth admin recovery**: PBKDF2-HMAC-SHA256 @600k iters/8-byte salt/256-bit (per `red-teaming/offensive-security-ops` reference) — recover, never redeploy-fresh.
- **Secrets**: use the SEAL→PROBE→REGISTER→WIRE→DOC→REPORT SOP; keep creds out of code.
- **Web/API auth**: probe auth-gated vs non-auth-gated endpoints read-only first; check TLS self-signed (`curl -sk`), HTTP header requirements, IP allowlists.
- **Pipeline**: on every internal vuln finding or recovery, add SAST (`semgrep`/`bandit`) + secret scan (`gitleaks`) + dependency scan (`trivy`).

---

## PART E — Tool index (GitHub, curated)
**Red/offensive** (authorized use): `nmap`, `masscan`, `rustscan`, `sqlmap`, `Burp Suite Community`, `Metasploit Framework`, `impacket`, `mimikatz`, `hashcat`/`john`, `responder`, `crackmapexec`, `linpeas`/`winpeas`, `Sliver`/`Mythic` (C2).
**AI offensive-agent harnesses (RoE-gated, authorized):** `elder-plinius/T3MP3ST` (autonomous red-team, ★5.7k), `PurpleAILAB/Decepticon` (autonomous Red Team agent, ★5.3k, RoE/ConOps/OPPLAN), `Ed1s0nZ/CyberStrikeAI` (★5.9k, Eino Go agents + MCP), `GH05TCREW/pentestagent` (black-box + playbooks, MIT), `samugit83/redamon` (containerized pentest pipeline, MIT).
**Blue/defensive/DFIR (curated lists):** `fabacab/awesome-cybersecurity-blueteam`, `meirwah/awesome-incident-response`, `cugu/awesome-forensics`, `tsale/awesome-dfir-skills`, `luduslibrum/awesome-playbooks` (1,347 IR playbooks), `Nervi0z/blue-team-tools`.
**Defensive tooling:** Suricata, Zeek, Snort, Wireshark, Velociraptor, GRR, Wazuh, Sysmon, osquery, TheHive, MISP, OpenCTI, Volatility, Autopsy, KAPE, FTK Imager, Plaso, OpenVAS/GVM, Nessus, Trivy, Semgrep, Bandit, gitleaks, trufflehog.

---

## How to use this KB
1. **Plan an engagement:** define scope + RoE → pick the ATT&CK tactics in scope → select PART A techniques and PART E tools.
2. **Defend/detect:** use PART B to map each ATT&CK technique to a detection source (Sysmon/Zeek/EDR) + a Sigma rule.
3. **Recover:** follow PART C (NIST lifecycle) using PART D's stack-specific notes.
4. **Keep current:** treat as living; on each new technique/finding or error, patch this note and the relevant skill; add new tools to `awesome-osint-arsenal-tools.json` categories.
