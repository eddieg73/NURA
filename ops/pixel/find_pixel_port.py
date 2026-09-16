#!/usr/bin/env python3
"""
FIND the Pixel's wireless-debugging ports on the tailnet.

Why a scan instead of `adb mdns services`: mDNS discovery relies on multicast on the LOCAL network.
Our phone is reached across a tailnet through a SOCKS5 proxy, so multicast never arrives. The port
must be found by connecting.

Android 11+ opens TWO ports once wireless debugging is on:
  * a PAIRING port  (_adb-tls-pairing) -- needs the 6-digit code shown on screen
  * a CONNECT port  (_adb-tls-connect) -- used after pairing
Both are dynamic, typically high. Scanning the whole 65535 range over a
50ms-latency tunnel is too slow, so scan the realistic range concurrently.
"""
import concurrent.futures as cf
import socket
import struct
import time

PHONE = "100.123.84.111"
SOCKS = ("127.0.0.1", 1055)


def socks_open(port, timeout=4):
    s = socket.socket()
    s.settimeout(timeout)
    try:
        s.connect(SOCKS)
        s.sendall(b"\x05\x01\x00")
        if s.recv(2)[1] != 0:
            return port, None
        s.sendall(b"\x05\x01\x00\x01" + socket.inet_aton(PHONE) + struct.pack(">H", port))
        rep = s.recv(4)
        if len(rep) < 4 or rep[1] != 0:
            return port, None
        return port, s
    except Exception:
        try:
            s.close()
        except Exception:
            pass
        return port, None


def scan(ports, workers=120):
    open_ports = []
    with cf.ThreadPoolExecutor(max_workers=workers) as ex:
        for port, s in ex.map(lambda p: socks_open(p), ports):
            if s is not None:
                open_ports.append(port)
                s.close()
    return open_ports


print("=" * 84)
print(f"SCANNING {PHONE} FOR WIRELESS-DEBUGGING PORTS")
print("=" * 84)

# The Android wireless-debugging allocator uses a broad ephemeral range. Scan it densely,
# plus the well-known adb port, concurrently.
RANGES = [
    (5555, 5556, "well-known adb tcpip"),
    (30000, 30100, "low ephemeral"),
    (37000, 37100, "common wd range"),
    (39000, 39100, "common wd range"),
    (40000, 40200, "common wd range"),
    (42000, 42100, "common wd range"),
    (44000, 44100, "common wd range"),
]

found = []
t0 = time.time()
for lo, hi, label in RANGES:
    ports = list(range(lo, hi))
    hits = scan(ports)
    print(f"  {label:<24} {lo}-{hi-1}   open: {hits if hits else '-'}")
    found += hits

print(f"\n  first pass complete in {time.time()-t0:.0f}s   open: {sorted(set(found))}")

# If nothing found in the sampled bands, sweep the full high range in coarse blocks.
if not set(found) - {5555}:
    print("\n  sampled bands empty — sweeping 30000-65535 (coarse, then refine)")
    coarse = scan(list(range(30000, 65536, 7)), workers=150)
    print(f"    coarse hits: {sorted(set(coarse))}")
    if coarse:
        refine = []
        for c in coarse:
            refine += list(range(max(30000, c - 6), min(65535, c + 7)))
        hits2 = scan(sorted(set(refine)), workers=150)
        print(f"    refined hits: {sorted(set(hits2))}")
        found += hits2

found = sorted(set(found))
print("\n" + "=" * 84)
print(f"OPEN PORTS ON THE PIXEL: {found if found else 'NONE'}")
print("=" * 84)

if found:
    print("\n  Probing each for the adb TLS handshake (adb wireless ports speak TLS):")
    for p in found:
        s, _ = socks_open(p, timeout=5)
        if not s:
            continue
        try:
            s.settimeout(3)
            # adb TLS handshake: the SERVER sends a 4-byte banner in some builds; others stay silent
            data = s.recv(64)
            print(f"    {p}: recv {len(data)} bytes  {data[:32]!r}")
        except socket.timeout:
            print(f"    {p}: silent (accepted, no banner) — consistent with an adb TLS listener")
        except Exception as e:
            print(f"    {p}: {e}")
        finally:
            s.close()
else:
    print("\n  Nothing listening. Possibilities:")
    print("   - wireless debugging was toggled off")
    print("   - the phone is asleep (wireless debugging stops advertising when idle)")
    print("   - the tailnet path dropped")
    print("   Re-check: python3 /opt/data/scripts/pixel-connect.py status")
