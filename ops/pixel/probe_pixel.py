#!/usr/bin/env python3
"""
Can Hermes reach the Pixel 10 Pro XL across the tailnet?

tailscaled runs in USERSPACE mode (--tun=userspace-networking), so there is NO kernel route to
100.x addresses. All tailnet traffic must go through the SOCKS5 proxy on localhost:1055.
This matters: adb has no native SOCKS support, so any raw-TCP client needs a bridge.

This script (a) confirms the SOCKS proxy answers, (b) reaches the Pixel through it, and
(c) probes the ports that matter for device control.
"""
import socket
import struct
import sys
import time

PHONE = "100.123.84.111"
SOCKS = ("127.0.0.1", 1055)

# Ports worth knowing about for Android device control
PORTS = [
    (5555, "adb tcpip (wireless debugging legacy)"),
    (37099, "adb wireless-debugging (Android 11+ dynamic)"),
    (5037, "adb server"),
    (8080, "http alt"),
    (8000, "artemis console"),
    (22, "ssh"),
    (5900, "vnc"),
    (7100, "tailscale ssh/generic"),
]


def socks5_connect(host, port, timeout=6):
    """Minimal SOCKS5 CONNECT through the tailscaled userspace proxy."""
    s = socket.socket()
    s.settimeout(timeout)
    try:
        s.connect(SOCKS)
    except Exception as e:
        return None, f"socks proxy unreachable: {e}"
    try:
        # greeting: no auth
        s.sendall(b"\x05\x01\x00")
        resp = s.recv(2)
        if len(resp) < 2 or resp[0] != 5:
            return None, f"bad greeting {resp!r}"
        if resp[1] != 0:
            return None, f"socks auth method rejected ({resp[1]})"
        # CONNECT to an IPv4 literal
        ip = socket.inet_aton(host)
        req = b"\x05\x01\x00\x01" + ip + struct.pack(">H", port)
        s.sendall(req)
        rep = s.recv(4)
        if len(rep) < 4:
            return None, "short reply"
        if rep[1] != 0:
            codes = {1: "general failure", 2: "not allowed", 3: "network unreachable",
                     4: "host unreachable", 5: "connection refused", 6: "TTL expired",
                     7: "command not supported", 8: "addr type not supported"}
            return None, codes.get(rep[1], f"code {rep[1]}")
        return s, "OK"
    except Exception as e:
        return None, str(e)


print("=" * 78)
print(f"TAILNET REACHABILITY -> {PHONE} (Pixel 10 Pro XL)")
print("=" * 78)

# ---- 0. is the proxy alive? ----------------------------------------------
s, msg = socks5_connect("100.76.175.91", 1, timeout=5)  # our own tailnet IP
print(f"\n0. SOCKS5 proxy at {SOCKS[0]}:{SOCKS[1]}")
print(f"   self-connect test (100.76.175.91:1): {msg}")
print(f"   -> proxy {'ANSWERS' if s is not None or 'refused' in msg.lower() else 'FAILED'}")

# ---- 1. can we reach the phone at all? -----------------------------------
print(f"\n1. PORT PROBE through SOCKS5 -> {PHONE}")
open_ports, closed, other = [], [], []
for port, desc in PORTS:
    t0 = time.time()
    sock, msg = socks5_connect(PHONE, port, timeout=7)
    dt = (time.time() - t0) * 1000
    if sock is not None:
        # try to read a banner without committing (adb speaks a protocol)
        banner = ""
        try:
            sock.settimeout(2)
            data = sock.recv(64)
            if data:
                banner = data[:40].hex()
        except Exception:
            pass
        print(f"   {port:<6} OPEN     {desc}   ({dt:.0f}ms)"
              + (f"  banner={banner}" if banner else ""))
        open_ports.append((port, desc))
        sock.close()
    elif "refused" in msg:
        print(f"   {port:<6} closed   {desc}   ({dt:.0f}ms)")
        closed.append(port)
    else:
        print(f"   {port:<6} {msg:<8} {desc}   ({dt:.0f}ms)")
        other.append((port, msg))

print(f"\n   OPEN:   {[p for p,_ in open_ports] or 'none'}")
print(f"   CLOSED: {closed or 'none'}")
if other:
    print(f"   OTHER:  {other}")

# ---- 2. interpretation ---------------------------------------------------
print("\n" + "=" * 78)
print("READING")
print("=" * 78)
if any(p == 5555 for p, _ in open_ports):
    print("  * adb tcpip (5555) is OPEN -> 'adb connect 100.123.84.111:5555' would work directly.")
elif closed:
    print("  * The phone ANSWERS (connection refused = a live host refusing a closed port).")
    print("    The tailnet path is GOOD; the phone simply is not running adb on a TCP port yet.")
    print("    Wireless debugging must be enabled: Developer options -> Wireless debugging.")
else:
    print("  * No definitive answer. Re-check tailscaled and that the phone is awake.")

print("\n  IMPORTANT (userspace mode): tailscaled here has NO TUN device, so nothing on this host")
print("  can dial 100.123.84.111 directly. adb has no native SOCKS support either. Any raw-TCP")
print("  client needs either (a) a local SOCKS->TCP bridge, or (b) an 'adb connect' to a")
print("  locally-forwarded port. Both are buildable without root.")
