#!/usr/bin/env python3
"""
NEW LEAD: test IPv6.

Every scan so far used IPv4 only (SOCKS5 ATYP=1). The phone also has a tailnet IPv6 address:
fd7a:115c:a1e0::1c2c:5470

If adbd binds to `::` (all IPv6) rather than to a specific IPv4 Wi-Fi address, it would answer on the
IPv6 tailnet address while being invisible on IPv4. That is a real possibility and it costs one test.

SOCKS5 with IPv6 uses ATYP=4 (0x04) and 16 raw address bytes instead of 4.
"""
import socket
import struct
import sys
import time

SOCKS = ("127.0.0.1", 1055)
PHONE_V6 = "fd7a:115c:a1e0::1c2c:5470"
PHONE_V4 = "100.123.84.111"


def socks6(host6, port, timeout=8):
    """SOCKS5 CONNECT to an IPv6 literal (ATYP=4)."""
    s = socket.socket()
    s.settimeout(timeout)
    try:
        s.connect(SOCKS)
        s.sendall(b"\x05\x01\x00")
        if s.recv(2)[1] != 0:
            return None, "auth refused"
        try:
            packed = socket.inet_pton(socket.AF_INET6, host6)
        except Exception as e:
            return None, f"bad ipv6 ({e})"
        s.sendall(b"\x05\x01\x00\x04" + packed + struct.pack(">H", port))
        rep = s.recv(4)
        if len(rep) < 4:
            return None, f"short reply {rep!r}"
        if rep[1] != 0:
            names = {1: "general failure", 2: "not allowed", 3: "net unreachable",
                     4: "host unreachable", 5: "connection refused",
                     6: "TTL expired", 7: "cmd not supported", 8: "atyp not supported"}
            return None, names.get(rep[1], f"code {rep[1]}")
        return s, "OK"
    except Exception as e:
        return None, f"exc {e}"


print("=" * 88)
print("IPv6 REACHABILITY TEST — the address my earlier scans never tried")
print("=" * 88)
print(f"  phone IPv6 : {PHONE_V6}")
print(f"  phone IPv4 : {PHONE_V4}")
print()

# Sanity: can we even do IPv6 through this SOCKS proxy? Control on a known-good target.
print("  control — does the proxy do IPv6 at all?")
s, m = socks6("2606:4700:4700::1111", 443, timeout=10)   # Cloudflare DNS over IPv6
print(f"    2606:4700:4700::1111:443  -> {m}")
if s:
    s.close()
proxy_v6 = (m == "OK")
print(f"    proxy IPv6 support: {'YES' if proxy_v6 else 'NO — IPv6 path unavailable'}")
print()

print("  phone, common wireless-debug ports over IPv6:")
cands = [5555, 37099, 43721, 43211, 41655, 33123]
for p in cands:
    s, m = socks6(PHONE_V6, p)
    print(f"    [{PHONE_V6}]:{p:<6} -> {m}")
    if s:
        try:
            s.settimeout(3)
            d = s.recv(64)
            print(f"        banner: {d[:40]!r}")
        except Exception:
            pass
        s.close()

print()
print("  if any port answered above, do a dense IPv6 sweep of 30000-50100")
open6 = []
t0 = time.time()
import concurrent.futures as cf


def probe6(p):
    s, m = socks6(PHONE_V6, p, timeout=6)
    if s:
        return p
    return None


with cf.ThreadPoolExecutor(max_workers=96) as ex:
    for r in ex.map(probe6, range(30000, 50101), chunksize=16):
        if r:
            open6.append(r)
print(f"    IPv6 sweep 30000-50100 in {time.time()-t0:.0f}s -> open: {open6 if open6 else 'NONE'}")

print()
open6b = []
with cf.ThreadPoolExecutor(max_workers=96) as ex:
    for r in ex.map(probe6, range(1, 30000, 3), chunksize=16):
        if r:
            open6b.append(r)
print(f"    IPv6 sweep 1-30000 (step 3) -> open: {open6b if open6b else 'NONE'}")

print("\n" + "=" * 88)
if open6 or open6b:
    print(f"  IPv6 FOUND LISTENERS: {sorted(set(open6 + open6b))}")
    print("  -> proceed with: adb connect via the bridge over IPv6")
else:
    print("  No IPv6 listeners either. IPv6 is not the answer — the binding theory stands.")
    print("  Everything on the Hermes side is exhausted; the constraint is on the phone.")
print("=" * 88)
