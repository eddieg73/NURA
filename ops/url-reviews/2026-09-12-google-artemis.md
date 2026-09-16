# URL INTEGRATION REVIEW — google/artemis
Reviewed 2026-09-12 by the CTO. Every figure below came from the GitHub API or the raw repo files,
not from the README's own claims.

---

## §1 CLASSIFY

| Field | Value |
|---|---|
| Repo | **`google/artemis`** |
| Category | **official** (Google) — highest trust tier |
| License | **Apache-2.0** — *verified by reading the `LICENSE` file*, not the API's `spdx_id` (a lesson already paid for this session: the API reported `NOASSERTION` on repos that turned out to be Meta proprietary) |
| Language | Python (3.12+; host has 3.13.5 ✓) |
| Created | 2026-08-13 · **pushed 2026-09-12 — active today** |
| Stars | **3,852 in under 1 month** · 321 forks · 56 open issues |
| Topics | ai-agents, android, google, test-automation, testing |

> **Claim to treat with care:** "99%+ on AndroidWorld". It is Google's own benchmark and the badge is
> their assertion. **Not independently verified here.** Plausible for a well-resourced Google team,
> but it is a vendor claim.

## What it actually is

**Natural-language → reliable Android automation.** It drives a *real phone* through ADB, captures
Logcat and screenshots, and exposes itself as a **native MCP server**.

Two execution modes — and this is the architectural detail that matters to us:

| Mode | Mechanism |
|---|---|
| **Flash** | Reactive observe-think-act loop. **No LangGraph**, no planner, no checker. ~5 s/step |
| **Pro** | **LangGraph multi-node**: Planner → Operator → Checker → Outputter. ~30 s/turn, `verification_level` off/final/checkpoints/strict |

**Pro is LangGraph.** Our Architecture Constitution says *"LangGraph = bounded reasoning"* — so Pro's
shape is one we already reason in.

## The decisive architectural fact

```
ADB, agents, models, and image processing remain on the device host
     ↓
a ZERO-RUNTIME-DEPENDENCY client reaches it over  http://artemis-host:8000
```

So Artemis does **not** have to live where Hermes lives. It lives where the **phone** is, and we drive
it over HTTP or the Python SDK:

```python
client = ArtemisClient("http://artemis-host:8000", device_serial="emulator-5554")
result = await client.run("Open Settings, verify battery %, check for crash dialogs")
assert result.succeeded
```

`OPEN_ROUTER_API_KEY` is a first-class provider — and **OpenRouter is already NURA's routing layer.**

---

## §2 VIABILITY ON THE NURA FLEET — the honest blocker

I probed rather than assumed:

| Check | Result | Meaning |
|---|---|---|
| `/dev/kvm` | **ABSENT** | **No hardware-accelerated emulator on this host** |
| CPU virt flags (`vmx`/`svm`) | not exposed | nested virt unavailable |
| `adb` | **not installed** | no device bridge |
| `uv` | 0.11.6 ✓ | toolchain fine |
| Docker | 26.1.5 ✓ | but an emulator needs KVM regardless |
| Load avg / free RAM | 3.03 / **1.0 GB free** | a 2–4 GB emulator would not fit |

And `mcp_server/rules.md` states it plainly:

> **"Running ARTEMIS requires at least one physically connected, fully authorized Android device
> (e.g., a Pixel phone) or an active emulator."**

**Verdict: excellent project, wrong substrate — today.** Artemis is not integrable on this gateway
host and the fleet has no Android device. It is a **desktop/device-host** tool: it belongs on a
machine with a phone attached, with Hermes driving it remotely.

---

## §3 FIT-MAP against the NURA plan

| NURA surface | Fit | Note |
|---|---|---|
| `computer-use` skill | **HIGH** | extends computer-use from desktop → **Android phones** |
| Mobile product builds | **HIGH** | NURA builds Flutter/Android apps. The recovered Paperclip org had Pixel (Flutter Lead), Canvas (Mobile Eng Lead), Beacon (App Store) — a **whole mobile lane with no automated QA** |
| `remote-device-control` | **HIGH** | a real phone as a controllable endpoint |
| MCP lane | **HIGH** | config shape is identical to our existing lanes (`mcp_servers.artemis`) |
| CI/CD release gating | **MEDIUM** | Python SDK + Pydantic + pytest assertions |
| Evidence discipline | **HIGH** | Logcat + screenshots + **trace replay** — aligns with verify-before-declare |
| OpenRouter routing | **MEDIUM** | supported provider, matches our layer |
| **Clinical / PHI / RAF** | **NONE** | no clinical relevance whatsoever. **Not a clinical tool — do not let it near PHI.** |

### The genuinely valuable artifact, available *now* — `mcp_server/rules.md`

A "Mobile Testing Mindset" doctrine that is **reusable regardless of whether we run the tool**:

1. **Dynamic-First, Coordinate-Fallback** locator pattern — prefer IDs/text/OCR; absolute coordinates
   as fallback. (Directly analogous to our own "deterministic geometry over model claims".)
2. **Flash vs Pro routing with measured latency** — ~5 s vs ~30 s step interval, and *compensate for
   model latency during exploration but write deterministic waits in the final test code.*
3. **The Runnable Code Principle** — deliver runnable tests with verified interactions, never
   assumed ones. **Explore with the agent; then write exact timing by hand.**
4. **Per-device mutex + multi-device concurrency** (`DeviceExecutionLock`, FIFO per device).
5. **Verify with a read-only Checker** at graduated depth — `off / final / checkpoints / strict`.
6. **Execution incidents persist in the Operator's context** with a consecutive-failure count as a
   *fact* until a later action succeeds. *(Same instinct as our failure doctrine: track repeats.)*

Point 3 is the one worth stealing outright: **the exploration agent and the final test code are
different instruments, and only the second one is deterministic.**

---

## §4 DECIDE

**STUDY + MONITOR, with a conditional INTEGRATE.**

- ❌ **Do NOT install on this gateway host.** No KVM, no adb, no device, 1 GB free RAM.
- ✅ **ABSORB `rules.md` now** — the doctrine is tool-independent and applies to any mobile QA we do.
- ✅ **REGISTER as the designated Android QA lane**, to be deployed the moment a device host exists.
- ⚠️ **Trigger for INTEGRATE:** NURA has (a) a physical Android device **or** an emulator host, and
  (b) an Android build that needs release gating.

**Why STUDY rather than SKIP:** NURA ships mobile apps. Automated Android QA is a real, currently
uncovered capability — and this is the Apache-2.0 Google reference implementation of it.

**Why not INTEGRATE today:** there is nothing to point it at. Buying a phone to run a tool we have no
immediate test target for is the wrong order. **Device first, tool second.**

---

## §5 SUPPLY-CHAIN FLAG — read before anyone runs `./start.sh`

The one-click script **auto-installs system toolchains** (ADB, scrcpy, FFmpeg, Python/`uv` deps) **and
mounts global MCP configuration + agent rule files into your IDEs** — Antigravity, Cursor, Claude
Code, Codex, Windsurf, VS Code, Cline/Roo, OpenClaw.

That is a **global-config mutation from a convenience script**. Our supply-chain doctrine is
*sanction + inspect before integration, never blind-install*.

**If it is ever deployed: use the manual path** (`uv`, explicit `.env`, `artemis mcp --generate-config
<client>` to emit a config for review) — **do not run `start.sh` on a machine carrying credentials**
until those installer steps have been read. Google provenance is a strong signal, not a substitute
for reading what executes.

**Isolation:** if/when deployed, run it on the **device host**, never on the gateway or a clinical
node. It holds provider API keys and drives a physical endpoint.

---

## §6 REGISTER

| URL | Source | Category | Fit | Decision | Status | Date |
|---|---|---|---|---|---|---|
| https://github.com/google/artemis | Google (official) | mobile QA / agent tooling | Android automation + MCP lane | **STUDY + MONITOR** | Not deployed — no device host. `rules.md` doctrine absorbable now. | 2026-09-12 |

---

## §7 REPORT — one line

**Google's Apache-2.0 agent that drives real Android phones over MCP. Genuinely strong, architecturally
familiar (Pro is LangGraph, OpenRouter is a first-class provider), and it fills a real gap — NURA ships
mobile apps and has zero automated Android QA. But it needs a physical phone or a KVM-enabled emulator,
and this fleet has neither, so it is a STUDY — its `rules.md` testing doctrine is the part we can use
today, and the tool follows the first Android device.**
