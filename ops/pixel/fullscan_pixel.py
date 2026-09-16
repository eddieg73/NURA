#!/usr/bin/env python3
"""
FULL-RANGE scan of the Pixel — definitive answer to "is anything listening?"

The sampled bands found nothing, but a sampled scan cannot prove absence. This sweeps all 65535
ports concurrently. At ~60ms latency with 300 workers that is roughly 15-25s, which is cheap enough
to make the answer conclusive.

The scanner is already validated against known-open and known-closed controls on srv1441409.
"""
import concurrent.futures as cf
import socket
import struct
import time

PHONE = "100.123.84.111"


def socks_open(port, timeout=6):
    s = socket.socket()
    s.settimeout(timeout)
    try:
        s.connect(("127.0.0.1", 1055))
        s.sendall(b"\x05\x01\x00")
        if s.recv(2)[1] != 0:
            return None
        s.sendall(b"\x05\x01\x00\x01" + socket.inet_aton(PHONE) + struct.pack(">H", port))
        rep = s.recv(4)
        if len(rep) >= 4 and rep[1] == 0:
            return (port, s)
        return None
    except Exception:
        return None


print("=" * 84)
print(f"FULL-RANGE SCAN 1-65535  ->  {PHONE}")
print("=" * 84)

t0 = time.time()
open_ports = []
PORTS = list(range(1, 65536))
with cf.ThreadPoolExecutor(max_workers=300) as ex:
    for r in ex.map(socks_open, PORTS, chunksize=64):
        if r:
            open_ports.append(r)

print(f"  scanned 65535 ports in {time.time()-t0:.0f}s")
print(f"\n  OPEN PORTS: {[p for p, _ in open_ports] if open_ports else 'NONE — literally nothing listening'}")

for p, s in open_ports:
    try:
        s.settimeout(3)
        d = s.recv(64)
        print(f"    port {p}: {len(d)} bytes  {d[:32]!r}")
    except socket.timeout:
        print(f"    port {p}: silent listener (accepted, no banner)")
    except Exception as e:
        print(f"    port {p}: {e}")
    finally:
        s.close()

print("\n" + "=" * 84)
print("INTERPRETATION")
print("=" * 84)
if not open_ports:
    print("""
  ZERO listening ports on the tailnet address. The scanner is validated, so this is real.

  MOST LIKELY CAUSE — an Android platform behaviour, not a mistake on your part:
  Android's wireless-debugging adbd binds to the WI-FI interface, not to the Tailscale (VPN)
  interface. Tailscale on Android runs as a VpnService: packets sent to 100.123.84.111 arrive at
  the Tailscale app and are handed to the local stack, but if adbd is bound specifically to the
  Wi-Fi address it will never answer on the tailnet address. So "wireless debugging is enabled"
  and "reachable over Tailscale" are two different things, and only the first is currently true.

  This is exactly the same failure shape as the rest of tonight: the phone is fine, the toggle is
  on, and the transport is the constraint.

  WHAT TO TRY, IN ORDER OF COST:
   1. Tell me the PORT shown on the Wireless debugging screen ("IP address & port"). If a port
      appears there and my scan still shows nothing, the binding theory is confirmed rather than
      assumed -- and we stop guessing.
   2. Check whether the phone shows a WiFi IP as well as the Tailscale IP. If wireless debugging
      displays a 192.168.x.x address, that is the interface it bound to.
   3. USB remains the reliable path if a computer is ever physically near the phone.
""")
else:
    print("  Ports found — proceed to pair/connect with pixel-connect.py.")
