#!/usr/bin/env python3
"""
Is port 1 a REAL listener on the Pixel, or a SOCKS-proxy artifact?

The full scan reported port 1 open with a 6-byte banner starting dL\xaf[ -- and the earlier
srv1441409:22 probe returned a banner starting dL\xaf[\x80@. Two different hosts, same 4-byte
prefix, both on ports that should not behave that way. That is the signature of the TRANSPORT
answering, not the target.

Control test: probe port 1 on hosts where we know the truth, and several reserved/dead ports.
"""
import socket
import struct
import time


def probe(host, port, timeout=8):
    """Return (reply_code, bytes_read, sample)."""
    s = socket.socket()
    s.settimeout(timeout)
    try:
        s.connect(("127.0.0.1", 1055))
        s.sendall(b"\x05\x01\x00")
        if s.recv(2)[1] != 0:
            return ("auth-fail", 0, b"")
        s.sendall(b"\x05\x01\x00\x01" + socket.inet_aton(host) + struct.pack(">H", port))
        rep = s.recv(4)
        if len(rep) < 4:
            return ("short", 0, rep)
        if rep[1] != 0:
            return (f"socks-code-{rep[1]}", 0, b"")
        s.settimeout(2.5)
        try:
            d = s.recv(64)
        except socket.timeout:
            d = b""
        return ("OK", len(d), d)
    except Exception as e:
        return (f"exc:{type(e).__name__}", 0, b"")
    finally:
        try:
            s.close()
        except Exception:
            pass


PIXEL = "100.123.84.111"
SRV = "100.88.16.54"

print("=" * 88)
print("IS PORT 1 REAL? CONTROL PROBES")
print("=" * 88)

CASES = [
    (PIXEL, 1, "PIXEL port 1  <- the suspicious 'open'"),
    (SRV, 1, "srv port 1    <- should NOT be open"),
    ("1.1.1.1", 1, "1.1.1.1 port 1 <- public control"),
    (SRV, 22, "srv port 22   <- genuinely open (known)"),
    (SRV, 54321, "srv 54321     <- genuinely closed (known)"),
    (PIXEL, 7, "PIXEL port 7  <- reserved, should be closed"),
    (PIXEL, 12345, "PIXEL 12345   <- arbitrary"),
]

for host, port, label in CASES:
    code, n, sample = probe(host, port)
    print(f"  {label:<44} code={code:<14} bytes={n:<3} {sample[:20]!r}")

print("\n" + "=" * 88)
print("READING")
print("=" * 88)
c1_pixel = probe(PIXEL, 1)
c1_srv = probe(SRV, 1)
if c1_srv[0] == "OK" and c1_srv[1] > 0:
    print("  srv:1 ALSO returns data -> this is a TRANSPORT artifact, not a service on the Pixel.")
    print("  Conclusion: the 'port 1 open' result is a FALSE POSITIVE of the SOCKS path.")
    print("  Port 1 must be excluded, and the Pixel scan verdict stands: NO real listener found.")
elif c1_pixel[0] == "OK" and c1_srv[0] != "OK":
    print("  Only the Pixel answers on port 1 -> inspect further before trusting anything.")
else:
    print(f"  Neither host answers meaningfully on port 1 (pixel={c1_pixel[0]}, srv={c1_srv[0]}).")
