#!/usr/bin/env python3
"""
CONTROL TEST: does the port scanner actually detect an open port?

The Pixel scan found nothing. Before concluding "nothing is listening", prove the INSTRUMENT works.
A scanner that silently fails everywhere returns exactly the same answer as a closed port --
indistinguishable, and one of them would send me chasing the wrong problem.

srv1441409 (100.88.16.54) has :22 open and confirmed earlier. If the scanner cannot see THAT,
the scanner is broken and the Pixel result means nothing.
"""
import concurrent.futures as cf
import socket
import struct
import time


def socks_open(host, port, timeout=5):
    s = socket.socket()
    s.settimeout(timeout)
    try:
        s.connect(("127.0.0.1", 1055))
        s.sendall(b"\x05\x01\x00")
        if s.recv(2)[1] != 0:
            return False
        s.sendall(b"\x05\x01\x00\x01" + socket.inet_aton(host) + struct.pack(">H", port))
        rep = s.recv(4)
        ok = len(rep) >= 4 and rep[1] == 0
        s.close()
        return ok
    except Exception:
        try:
            s.close()
        except Exception:
            pass
        return False


print("=" * 84)
print("SCANNER CONTROL TEST")
print("=" * 84)

CASES = [
    ("100.88.16.54", 22, True, "srv1441409 ssh — KNOWN OPEN (must be detected)"),
    ("100.88.16.54", 80, True, "srv1441409 http — KNOWN OPEN"),
    ("100.88.16.54", 54321, False, "srv1441409 — KNOWN CLOSED (must be rejected)"),
    ("100.123.84.111", 5555, False, "Pixel adb — unknown"),
]

all_ok = True
for host, port, expected, label in CASES:
    t0 = time.time()
    got = socks_open(host, port)
    dt = (time.time() - t0) * 1000
    verdict = "OK " if got == expected else "!! "
    if got != expected and "unknown" not in label:
        all_ok = False
    print(f"  {verdict} {label:<52} got={got} expected={expected} ({dt:.0f}ms)")

print()
if all_ok:
    print("  SCANNER IS TRUSTWORTHY — it detects open ports and rejects closed ones.")
    print("  Therefore the Pixel result (no open ports) is a REAL finding, not an instrument fault.")
else:
    print("  SCANNER IS UNRELIABLE — fix it before drawing any conclusion about the Pixel.")

# ---- is the tailnet path still alive? -------------------------------------
print("\n" + "=" * 84)
print("TAILNET PATH TO THE PIXEL")
print("=" * 84)
import subprocess
env = {"PATH": "/opt/data/bin:/usr/bin:/bin"}
for cmd in [["tailscale", "--socket=/tmp/tailscaled.sock", "ping", "--c", "2", "100.123.84.111"]]:
    try:
        r = subprocess.run(cmd, capture_output=True, text=True, timeout=25, env=env)
        print((r.stdout + r.stderr).strip()[:300])
    except Exception as e:
        print(f"  ping failed: {e}")

r = subprocess.run(["tailscale", "--socket=/tmp/tailscaled.sock", "status", "--json"],
                   capture_output=True, text=True, timeout=25, env=env)
import json
try:
    d = json.loads(r.stdout)
    for k, p in (d.get("Peer") or {}).items():
        if "pixel" in (p.get("HostName", "")).lower() and p.get("Online"):
            print(f"  peer: {p.get('HostName')}  {p.get('TailscaleIPs')}  "
                  f"online={p.get('Online')}  lastseen={p.get('LastSeen')}  "
                  f"rx={p.get('RxBytes')} tx={p.get('TxBytes')}")
except Exception as e:
    print(f"  status parse: {e}")
