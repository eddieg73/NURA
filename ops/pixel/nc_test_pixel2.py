#!/usr/bin/env python3
"""
AUTHORITATIVE TEST via `tailscale nc` — corrected syntax.

BUG IN THE PREVIOUS ATTEMPT (caught by its own control test, which is why controls matter):
  `tailscale nc` takes TWO arguments:  tailscale nc <host-or-IP> <port>
  I passed a single "host:port" string, so EVERY call printed usage and exited 1.
  My success-detector looked for keywords like "refused" in stderr and therefore classified the
  usage error as SUCCESS -> it reported ok=True for a known-closed port. The control exposed it.

Corrected: separate argv elements, and judge strictly on the exit code plus explicit error text.

Why this instrument matters: `tailscale nc` uses the DAEMON'S OWN netstack, so it
  * bypasses the SOCKS5 proxy entirely (which we proved cannot route IPv6)
  * reaches BOTH IPv4 and IPv6 tailnet addresses
"""
import subprocess
import sys

TS = ["/opt/data/bin/tailscale", "--socket=/tmp/tailscaled.sock", "nc"]
ENV = {"PATH": "/opt/data/bin:/usr/bin:/bin", "HOME": "/opt/data"}

PHONE4 = "100.123.84.111"
PHONE6 = "fd7a:115c:a1e0::1c2c:5470"
SRV = "100.88.16.54"


def nc(host, port, timeout=8):
    """Return (connected, detail). Correct argv: host and port SEPARATE."""
    cmd = TS + [host, str(port)]
    try:
        p = subprocess.run(cmd, input=b"", capture_output=True, timeout=timeout, env=ENV)
    except subprocess.TimeoutExpired:
        # connected, peer held the socket open — that IS a successful connection
        return True, "connected (held open)"
    except Exception as e:
        return False, f"exc {e}"

    err = (p.stderr or b"").decode(errors="ignore").strip()
    out = (p.stdout or b"")
    if p.returncode == 0:
        return True, f"connected ({len(out)} bytes)"
    if "usage:" in err:
        return False, "USAGE ERROR — bad argv (this is a bug, not a closed port)"
    return False, (err.splitlines()[-1][:90] if err else f"exit {p.returncode}")


print("=" * 92)
print("CONTROL — corrected invocation")
print("=" * 92)
c1 = nc(SRV, 22)
print(f"  srv:22     KNOWN OPEN    -> {c1}")
c2 = nc(SRV, 54321)
print(f"  srv:54321  KNOWN CLOSED  -> {c2}")
ok = c1[0] and not c2[0] and "USAGE" not in c2[1]
print(f"  => instrument {'TRUSTWORTHY' if ok else 'STILL BROKEN'}")
if not ok:
    sys.exit(1)

print("\n" + "=" * 92)
print("PHONE — IPv4 (100.123.84.111)")
print("=" * 92)
for p in [5555, 5037, 37099, 41655, 43211, 43721]:
    c, d = nc(PHONE4, p)
    print(f"  {p:<6} -> connected={c}   {d}")

print("\n" + "=" * 92)
print("PHONE — IPv6 ([fd7a:115c:a1e0::1c2c:5470])  <- NEVER TESTED BEFORE")
print("=" * 92)
for p in [5555, 5037, 37099, 41655, 43211, 43721]:
    c, d = nc(PHONE6, p)
    print(f"  {p:<6} -> connected={c}   {d}")

print("\n" + "=" * 92)
print("SWEEP the wireless-debug range on BOTH families")
print("=" * 92)
f4 = []
for p in range(30000, 50101, 11):
    if nc(PHONE4, p, timeout=4)[0]:
        f4.append(p)
print(f"  IPv4 hits: {f4 if f4 else 'none'}")

f6 = []
for p in range(30000, 50101, 11):
    if nc(PHONE6, p, timeout=4)[0]:
        f6.append(p)
print(f"  IPv6 hits: {f6 if f6 else 'none'}")

print("\n" + "=" * 92)
if f4 or f6:
    print(f"  LISTENERS: IPv4 {f4}   IPv6 {f6}")
else:
    print("  Definitive: no listener on the phone's tailnet address, either family,")
    print("  via the daemon's own stack. The constraint is the phone-side binding.")
print("=" * 92)
