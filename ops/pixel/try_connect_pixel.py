#!/usr/bin/env python3
"""
ACTUALLY TRY TO CONNECT — stop theorising.

Two things to settle with real attempts:

1. IS THE BULK SCAN RELIABLE? The full sweep used 300 concurrent workers through one SOCKS proxy.
   High concurrency can silently drop connections and produce a FALSE "nothing listening". Control:
   run the SAME bulk method against srv1441409, where ports 22 and 80 are known open. If the bulk
   method misses those, every Pixel conclusion drawn from it is void.

2. DOES adb ITSELF CONNECT? A raw-scan null is not the same as adb failing. adb performs a real
   protocol handshake. Attempt it against every candidate, including via the local bridge.
"""
import concurrent.futures as cf
import socket
import struct
import subprocess
import time

ADB = "/opt/data/android-sdk/platform-tools/adb"
PHONE = "100.123.84.111"
SRV = "100.88.16.54"


def socks_open(host, port, timeout=6):
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


# ---------------------------------------------------------------- 1. control
print("=" * 88)
print("1. CONTROL — is the bulk/threaded scan reliable?")
print("=" * 88)
SAMPLE = [22, 80] + list(range(21000, 21050))
t0 = time.time()
with cf.ThreadPoolExecutor(max_workers=300) as ex:
    res = list(ex.map(lambda p: (p, socks_open(SRV, p)), SAMPLE, chunksize=8))
found = [p for p, ok in res if ok]
print(f"  same 300-worker method vs srv1441409, {len(SAMPLE)} ports in {time.time()-t0:.1f}s")
print(f"  detected open: {found}   (expected at least [22, 80])")
bulk_reliable = 22 in found and 80 in found
print(f"  => bulk scan {'RELIABLE' if bulk_reliable else 'UNRELIABLE — earlier nulls are void'}")

# ---------------------------------------------------------------- 2. rescan
print("\n" + "=" * 88)
print("2. RESCAN THE PIXEL — moderate concurrency across the real wireless-debug range")
print("=" * 88)
CANDIDATES = [5555]
# Android allocates wireless-debug ports from a wide ephemeral range
CANDIDATES += list(range(30000, 50100))
t0 = time.time()
hits = []
with cf.ThreadPoolExecutor(max_workers=96) as ex:
    for p, ok in ex.map(lambda x: (x, socks_open(PHONE, x)), CANDIDATES, chunksize=16):
        if ok:
            hits.append(p)
print(f"  scanned {len(CANDIDATES)} ports in {time.time()-t0:.0f}s")
print(f"  open on the Pixel: {hits if hits else 'NONE'}")

# ---------------------------------------------------------------- 3. adb
print("\n" + "=" * 88)
print("3. ATTEMPT adb — the real handshake, not a raw socket")
print("=" * 88)
subprocess.run([ADB, "kill-server"], capture_output=True, timeout=30)
subprocess.run([ADB, "start-server"], capture_output=True, timeout=60)
time.sleep(1)

targets = [PHONE + ":" + str(p) for p in (hits or [5555])]
for tgt in targets:
    r = subprocess.run([ADB, "connect", tgt], capture_output=True, text=True, timeout=60)
    out = (r.stdout + r.stderr).strip()
    print(f"  adb connect {tgt}")
    print(f"    -> {out[:150]}")

print()
r = subprocess.run([ADB, "devices", "-l"], capture_output=True, text=True, timeout=30)
print("  adb devices -l:")
for line in r.stdout.strip().splitlines():
    print("   ", line)

print("\n" + "=" * 88)
print("VERDICT")
print("=" * 88)
if not bulk_reliable:
    print("  The scan method is unreliable — the earlier 'nothing listening' result is void and")
    print("  must not be used to conclude anything.")
elif hits:
    print(f"  Ports found on the Pixel: {hits} — see the adb output above.")
else:
    print("  Bulk method IS reliable, and the Pixel genuinely exposes no port in 30000-50100 or 5555.")
    print("  adb cannot connect without a listening port. The Wi-Fi-binding explanation stands.")
