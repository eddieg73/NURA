#!/usr/bin/env python3
"""
PIXEL PAIR & CONNECT — one-shot helper for Google Pixel 10 wireless debugging.

Everything on the Hermes side is already proven working:
  * tailscaled runs in userspace mode (SOCKS5 on 127.0.0.1:1055) -- no kernel route to 100.x
  * Pixel 10 Pro XL = 100.123.84.111, ONLINE, direct path, `tailscale ping` 54 ms
  * adb 37.0.1 installed at /opt/data/android-sdk/platform-tools/adb
  * the SOCKS->TCP tunnel was verified end-to-end against a live tailnet peer

The ONE missing piece is that adbd is not listening on the phone yet -- Wireless Debugging is off.
Android 11+ uses DYNAMIC ports and a TLS pairing step, so the phone must tell us:

  PAIR port  (from "Pair device with pairing code")  + the 6-digit code
  CONNECT port (from the main Wireless debugging screen, "IP address & port")

Usage:
    python3 pixel-connect.py pair  <pair_port> <6_digit_code>
    python3 pixel-connect.py connect <connect_port>
    python3 pixel-connect.py status
"""
import os
import subprocess
import sys
import time

ADB = "/opt/data/android-sdk/platform-tools/adb"
PHONE = "100.123.84.111"
BRIDGE = "/opt/data/scripts/pixel-bridge.py"
PY = "/opt/hermes/.venv/bin/python3"


def valid_port(v):
    """Ports come from the user's command line. Validate as a plain int in range before use --
    the bridge is started as a subprocess, so an unvalidated value would be an injection vector."""
    try:
        n = int(v)
    except (TypeError, ValueError):
        raise SystemExit(f"invalid port: {v!r} (must be an integer)")
    if not (1 <= n <= 65535):
        raise SystemExit(f"invalid port: {n} (out of range 1-65535)")
    return n


def run(cmd, timeout=90):
    """Always pass a list -- never shell=True with interpolated values."""
    p = subprocess.run(cmd, capture_output=True, text=True, timeout=timeout)
    return p.returncode, (p.stdout or "") + (p.stderr or "")


def start_bridge(port):
    """Start a forwarder on local port == remote port, kill any previous one.

    Ports are validated to ints first and the process is launched with an argv LIST,
    so no shell metacharacter can ever be interpreted.
    """
    run(["/usr/bin/pkill", "-f", "pixel-bridge.py"])
    time.sleep(0.5)
    ports = sorted({port, 5555, 5037})
    log = open("/tmp/pixel-bridge.log", "w")
    subprocess.Popen(
        [PY, BRIDGE, "--phone", PHONE,
         "--ports", ",".join(str(p) for p in ports)],
        stdout=log, stderr=subprocess.STDOUT, start_new_session=True)
    time.sleep(2.5)
    return "/tmp/pixel-bridge.log"


def bridge_log():
    try:
        return open("/tmp/pixel-bridge.log").read()[-600:]
    except Exception:
        return "(no log)"


def show_devices():
    rc, out = run([ADB, "devices", "-l"], timeout=30)
    return out.strip()


def main():
    if len(sys.argv) < 2:
        print(__doc__)
        sys.exit(1)
    mode = sys.argv[1]

    if mode == "status":
        print("=" * 74)
        print("PIXEL CONTROL — STATUS")
        print("=" * 74)
        rc, out = run([PY, BRIDGE, "--selftest"], timeout=60)
        print(out)
        print("  adb devices:")
        for line in show_devices().splitlines():
            print("   ", line)
        print("\n  bridge log:")
        print("   ", bridge_log().replace("\n", "\n    "))
        return

    if mode == "pair":
        if len(sys.argv) < 4:
            print("usage: pixel-connect.py pair <pair_port> <6_digit_code>")
            sys.exit(1)
        port, code = valid_port(sys.argv[2]), sys.argv[3]
        if not (code.isdigit() and len(code) == 6):
            raise SystemExit(f"invalid pairing code: {code!r} (expected 6 digits)")
        print(f"  starting bridge on local port {port} -> {PHONE}:{port}")
        start_bridge(port)
        print(f"  bridge log: {bridge_log()[:200]}")
        print(f"\n  pairing via 127.0.0.1:{port} ...")
        rc, out = run([ADB, "pair", f"127.0.0.1:{port}", code], timeout=120)
        print(f"  {out.strip()}")
        if "Successfully paired" in out:
            print("\n  PAIRED.")
            print("  Now read the CONNECT port from the phone's main Wireless debugging screen")
            print("  (it usually differs) and run:")
            print(f"     python3 {sys.argv[0]} connect <connect_port>")
        return

    if mode == "connect":
        if len(sys.argv) < 3:
            print("usage: pixel-connect.py connect <connect_port>")
            sys.exit(1)
        port = valid_port(sys.argv[2])
        start_bridge(port)
        print(f"  connecting via 127.0.0.1:{port} ...")
        rc, out = run([ADB, "connect", f"127.0.0.1:{port}"], timeout=120)
        print(f"  {out.strip()}")
        time.sleep(2)
        devs = show_devices()
        print("\n  adb devices -l:")
        for line in devs.splitlines():
            print("   ", line)
        if "\tdevice" in devs:
            print("\n  ✅ CONNECTED — the Pixel is under adb control.")
            rc, out = run([ADB, "shell", "getprop", "ro.product.model"], timeout=60)
            print(f"     model: {out.strip()}")
            rc, out = run([ADB, "shell", "getprop", "ro.build.version.release"], timeout=60)
            print(f"     android: {out.strip()}")
        elif "unauthorized" in devs:
            print("\n  ⚠ UNAUTHORIZED — accept the 'Allow USB debugging?' prompt ON THE PHONE.")
        else:
            print("\n  Not connected yet. Check the phone's screen is unlocked and the port is right.")
        return

    print(f"unknown mode {mode}")
    print(__doc__)
    sys.exit(1)


if __name__ == "__main__":
    main()
