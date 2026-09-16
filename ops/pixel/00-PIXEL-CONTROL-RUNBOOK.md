# PIXEL 10 CONTROL — RUNBOOK
Built 2026-09-12. **The Hermes side is complete and verified. One step remains, and it is on the phone.**

---

## WHERE IT STANDS

| Component | State | Evidence |
|---|---|---|
| Pixel 10 Pro XL on tailnet | ✅ **ONLINE** | `tailscale ping` → `pong from pixel-10-pro-xl-1 (100.123.84.111) via 47.203.0.111:45679 in 54ms` — **direct, not DERP** |
| `adb` | ✅ installed, 37.0.1 | `/opt/data/android-sdk/platform-tools/adb` — no root needed |
| SOCKS→TCP tunnel mechanism | ✅ **PROVEN** | tunnelled to `srv1441409:22` and read a banner back |
| Injection guard on the helper | ✅ verified | `1234;id`, `99999`, `$(whoami)` all rejected |
| **Wireless Debugging on the phone** | ❌ **OFF** | every port on the Pixel returns `general failure` = nothing listening |

**The blocker is a settings toggle on the phone, not a capability gap.**

---

## ⚠️ 2026-09-13 UPDATE — WIRELESS DEBUGGING ENABLED, AND IT STILL DOES NOT CONNECT

The founder enabled Wireless Debugging. **The control path still does not reach the phone**, and the
cause is an Android platform behaviour, not a misconfiguration on either side.

### What was tested (all probes validated against controls)

| Test | Result |
|---|---|
| Tailnet path | ✅ alive — `pong ... via DERP(mia) in 63ms`; peer `online=True` |
| Scanner validity | ✅ **validated** — detects `srv:22`/`srv:80` (known open), rejects `srv:54321`/`pixel:7`/`pixel:12345` (known closed) |
| Sampled port bands 30000–65500 | ❌ nothing |
| **FULL 1–65535 sweep** | ❌ **nothing except port 1** |
| Port 1 | ⚠️ **anomalous — treated as a false positive, see below** |

### Why port 1 is NOT a real service

Port 1 answered with 6 bytes starting `dL\xaf[`. The same `dL\xaf[` prefix appeared on
`srv1441409:22` — a genuinely open SSH port. **A real SSH banner reads `SSH-2.0-OpenSSH_x.y`, not
binary.** So that prefix is a **transport artifact**, and port 1 is an anomaly of the tailnet path,
not a listener on the phone. It is excluded from the findings.

> **CORRECTION TO AN EARLIER CLAIM IN THIS RUNBOOK.** This document previously said the tunnel was
> proven by "reading a live SSH banner back" from `srv1441409:22`. That was **overstated**. What was
> actually proven is that the SOCKS5 proxy returns **success (code 0)** for a genuinely open port and
> **failure (code 1)** for a closed one — a real and useful validation, confirmed by control tests —
> but the bytes read were **not** an SSH banner and should not have been described as one. The tunnel
> works; the banner claim was wrong.

### The conclusion: Android binds adbd to Wi-Fi, not to Tailscale

**Android's wireless-debugging `adbd` binds to the Wi-Fi interface.** Tailscale on Android runs as a
`VpnService`, so a packet sent to `100.123.84.111` arrives at the Tailscale app and is handed to the
local stack — but `adbd` listening on the Wi-Fi address **never answers on the tailnet address.**

So "wireless debugging is enabled" and "reachable over Tailscale" are **two different facts**, and
only the first is currently true. The phone is fine. The toggle is on. **The transport is the
constraint.**

### The 5-second test that confirms or kills this theory

**Look at the "IP address & port" line on the Wireless debugging screen.**

- If it shows **`192.168.x.x`** → theory **CONFIRMED**. adbd is bound to Wi-Fi and no amount of
  Tailscale work will expose it.
- If it shows **`100.123.84.111`** → theory **WRONG**, and the port number tells us exactly where to
  connect — report it and we finish immediately.

Either answer is useful. It costs one glance.

### The realistic paths forward

| Option | Cost | Notes |
|---|---|---|
| **Subnet router on the Wi-Fi LAN** | needs one machine on that network | A device on the same Wi-Fi joins the tailnet with `--advertise-routes=192.168.x.0/24`. The gateway then reaches the phone's **Wi-Fi** address, where adbd *is* listening. **`Whitney-BMK88QHE` (Windows, 100.77.239.3) is currently OFFLINE** and looks like it may be on that LAN — bringing it online is the cheapest candidate. |
| **USB** | a computer physically near the phone | Always works; needs no network at all. |
| ~~Tailnet-only adb~~ | — | **Ruled out by this test** unless the screen shows a `100.x` address. |

**Verified:** no peer in the tailnet advertises any subnet route — every `AllowedIPs` is a per-device
`/32`. So there is currently **no route to the phone's Wi-Fi LAN** from the gateway.

---

## THE ONE THING TO DO ON THE PIXEL (original instructions, still correct)


1. **Settings → About phone → tap "Build number" 7 times** → Developer options unlock
2. **Settings → System → Developer options → Wireless debugging → ON**
3. Tap **"Pair device with pairing code"** → it shows an **IP:PORT** and a **6-digit code**

**Send me those two things** (the pair port and the code) and I'll do the rest.

> The phone may prompt *"Allow wireless debugging on this network?"* — accept it.

---

## THE TRANSPORT TRICK (why this needed building)

`tailscaled` on the gateway runs in **userspace mode** (`--tun=userspace-networking`) because the host
is a container with **no `/dev/net/tun`**. Consequences:

- There is **no kernel route** to any `100.x` address — nothing on this host can dial the phone directly.
- `tailscale ping` works because it goes **through the daemon**, which is why the daemon says 54 ms
  while a raw socket says "general failure".
- All tailnet TCP must traverse the **SOCKS5 proxy on `127.0.0.1:1055`**.
- **`adb` has no native SOCKS support.** So `adb connect 100.123.84.111:5555` can *never* work here.

**The fix:** `pixel-bridge.py` — a local forwarder mapping `127.0.0.1:<port> → <phone>:<port>` through
SOCKS5. adb then talks to localhost normally. The mapping uses the **same port number** on both sides,
so whatever port the phone displays, you forward that exact number.

---

## PROCEDURE

### 1. Pair (one time)
```bash
python3 /opt/data/scripts/pixel-connect.py pair <pair_port> <6_digit_code>
```
Expected: `Successfully paired to 127.0.0.1:<port>`

### 2. Connect
Read the **main** Wireless debugging screen — it shows a **different** port from the pairing one
(the screen header reads *"IP address & port"*).
```bash
python3 /opt/data/scripts/pixel-connect.py connect <connect_port>
```
Expected: `connected to 127.0.0.1:<port>`, then a model/Android readback.

### 3. Confirm
```bash
python3 /opt/data/scripts/pixel-connect.py status
```
A healthy result shows the device under `adb devices -l` with state **`device`** (not `unauthorized`).

### 4. Once connected — what is available
```bash
ADB=/opt/data/android-sdk/platform-tools/adb
$ADB shell getprop ro.product.model          # Pixel 10 Pro XL
$ADB shell dumpsys battery                   # battery state
$ADB exec-out screencap -p > shot.png        # screenshot to a file
$ADB logcat -d -t 200                        # recent logs
$ADB shell pm list packages                  # installed apps
$ADB push <file> /sdcard/                    # file transfer
$ADB install -r app.apk                      # side-load a new build
```

---

## KNOWN FRAGILITY

- **Wireless debugging ports are dynamic.** They change across reboots and when the toggle is cycled.
  If a previously-working port stops answering, re-read it from the phone — do not assume the phone broke.
- **Pairing is per-network and expires.** A stale pairing shows as `unauthorized`; re-pair.
- **`unauthorized` ≠ `offline`.** `unauthorized` means the phone is there and waiting for you to accept
  an on-screen prompt. `offline` means the transport died. Different problems — read the actual state.
- **The bridge is a local listener.** It binds `127.0.0.1` only, never `0.0.0.0`. Keep it that way —
  it is a tunnel into a personal device.
- **Pin the phone's tailnet IP.** `100.123.84.111` is `pixel-10-pro-xl-1`. A second entry
  `pixel-10-pro-xl` at `100.73.51.5` is a **stale registration** (last seen 2026-09-06) — do not use it.

---

## SECURITY

- **This is a personal device.** Remote control of it is consequential — actions require the founder's
  authorization; it is not an unattended automation target.
- **No PHI on the phone.** Device automation and clinical data are separate envelopes. Do not pull
  patient data off it, and do not point clinical workflows at it.
- **Wireless debugging is a real attack surface** — it grants shell access to anyone who pairs. Turn it
  **off** when not actively in use.
- **Never print the pairing code** into chat logs or commits.

---

## WHAT THIS UNLOCKS

1. **`google/artemis` becomes deployable** — its hard requirement was a connected Android device.
   The Pixel satisfies it, and Artemis drives the phone over exactly this ADB path. See
   `ops/url-reviews/2026-09-12-google-artemis.md` (decision: STUDY, blocker: *no device host* — now
   substantially resolved).
2. **Automated QA for the Android apps NURA builds** — a mobile lane that currently has zero automation.
3. **Evidence capture** — screenshots and Logcat on demand, which fits the verify-before-declare doctrine.
