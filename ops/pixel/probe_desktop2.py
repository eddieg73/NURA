#!/usr/bin/env python3
"""
CORRECTED reachability probe — my previous one had a false-positive bug.

THE BUG: in probe_desktop.py, `subprocess.TimeoutExpired` was classified as "connected (held open)".
But `tailscale nc` to a FIREWALL-DROPPED port does not refuse -- it HANGS. So every dropped port was
reported OPEN. That produced a fake "11 ports open on the desktop, adb is running" result.

THE TELL: exit codes.
  exit 0   = TCP established (real listener)
  exit 1   = refused ("dial failure") -- host reachable, nothing on that port
  exit 124 = timeout -- FIREWALL DROPPED IT (not a listener)

A dropped port and a listening port are only distinguishable by how the connection FAILS. Treating
a timeout as success is exactly the same error class as everything else this session: the instrument
lying, not the work.

This version returns the exit code and classifies strictly.
"""
import subprocess

TS = ["/opt/data/bin/tailscale", "--socket=/tmp/tailscaled.sock", "nc"]
ENV = {"PATH": "/opt/data/bin:/usr/bin:/bin", "HOME": "/opt/data"}

DESK = "100.77.239.3"
SRV = "100.88.16.54"


def probe(host, port, timeout=10):
    """Return (verdict, exit_code). verdict in OPEN / refused / DROPPED / other."""
    cmd = TS + [host, str(port)]
    try:
        p = subprocess.run(cmd, input=b"", capture_output=True, timeout=timeout, env=ENV)
        rc = p.returncode
        if rc == 0:
            return "OPEN", rc
        return "refused", rc
    except subprocess.TimeoutExpired:
        return "DROPPED", 124
    except Exception as e:
        return f"exc:{e}", -1


print("=" * 90)
print("CONTROLS FIRST — the instrument must separate refused from dropped from open")
print("=" * 90)
for host, port, label in [
    (SRV, 22, "srv:22      KNOWN OPEN"),
    (SRV, 54321, "srv:54321   KNOWN CLOSED (refusing host)"),
    (DESK, 54321, "wht:54321   KNOWN CLOSED (dropping host)"),
]:
    v, rc = probe(host, port)
    print(f"  {label:<40} verdict={v:<9} exit={rc}")

print("\n" + "=" * 90)
print("DESKTOP — the ports my previous run falsely reported as OPEN")
print("=" * 90)
DESK_PORTS = [(22, "SSH"), (3389, "RDP"), (445, "SMB"), (5985, "WinRM"),
              (5037, "adb server"), (5555, "adb device"), (5938, "TeamViewer"), (7070, "AnyDesk")]
real = []
for port, label in DESK_PORTS:
    v, rc = probe(DESK, port)
    print(f"  {port:<6} {v:<9} exit={rc:<5} {label}")
    if v == "OPEN":
        real.append(port)

print("\n" + "=" * 90)
print("TRUTH")
print("=" * 90)
if real:
    print(f"  Genuinely reachable on the desktop: {real}")
else:
    print("  THE DESKTOP EXPOSES NOTHING.")
    print("  Every earlier 'OPEN' was a firewalled DROP that my script mislabelled as a connection.")
    print("  The desktop is ONLINE on the tailnet (packets route -- `tailscale ping` works), but")
    print("  Windows Firewall drops inbound on every probed port.")
    print()
    print("  => There is NO remote-management surface on the desktop from here.")
    print("  => The desktop can only be driven FROM ITS OWN SIDE -- which is precisely the")
    print("     'brother' route the founder named: an agent already running on that machine.")
print("=" * 90)
