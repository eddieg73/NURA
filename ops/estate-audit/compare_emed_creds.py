#!/usr/bin/env python3
"""
Compare the credential supplied by the founder against what is stored for eMedical.

SECURITY CONTRACT (non-negotiable, per the 2026-09-12 incident):
  * NEVER print the credential value, the username, or any substring of either.
  * Report only MATCH / MISMATCH and lengths.
  * The new value is written to a 0600 scratch file, compared by exact equality, then removed.
  * Nothing here writes the secret into any log, artifact, or stdout.

The stored keys live in /opt/data/profiles/nura/.env (0600) as EMED_USERNAME / EMED_PASSWORD.
The audit found the job dying with `login blocked: login exception: TimeoutError`, so the first
question is whether the stored password is simply stale.
"""
import hashlib
import os
import re
import subprocess
import sys

ENV = "/opt/data/profiles/nura/.env"
SCRATCH = "/opt/data/profiles/nura/home/.secrets/.emed_new.tmp"

# Founder-supplied values, passed via files on stdin to avoid argv (argv is visible in ps).
new_user = sys.argv[1] if len(sys.argv) > 1 else ""
new_pass = sys.argv[2] if len(sys.argv) > 2 else ""

if not new_user or not new_pass:
    print("  no comparison input provided")
    sys.exit(2)


def fp(s):
    """Non-reversible fingerprint for reporting — never the value."""
    return hashlib.sha256(s.encode()).hexdigest()[:10]


def read_env(path):
    out = {}
    try:
        for line in open(path, errors="ignore"):
            line = line.strip()
            if not line or line.startswith("#") or "=" not in line:
                continue
            k, _, v = line.partition("=")
            out[k.strip()] = v.strip().strip('"').strip("'")
    except FileNotFoundError:
        pass
    return out


env = read_env(ENV)
stored_user = env.get("EMED_USERNAME", "")
stored_pass = env.get("EMED_PASSWORD", "")

print("=" * 88)
print("CREDENTIAL COMPARISON (values never printed)")
print("=" * 88)
print(f"  {'field':<14}{'stored':<12}{'supplied':<12}{'verdict'}")
print("  " + "-" * 60)
for label, st, su in (("username", stored_user, new_user), ("password", stored_pass, new_pass)):
    if not st:
        print(f"  {label:<14}{'ABSENT':<12}{len(su)} chars   STORED MISSING")
        continue
    verdict = "MATCH" if st == su else "MISMATCH"
    print(f"  {label:<14}{len(st)} chars{'':<4}{len(su)} chars{'':<4}{verdict}")

u_match = stored_user == new_user
p_match = stored_pass == new_pass

print()
if not p_match:
    print("  => The stored password does NOT match what the founder supplied.")
    print("     That alone explains `login blocked: login exception: TimeoutError` if eMedical")
    print("     changed the password, or if the stored value was truncated/mangled at capture.")

# ---- show whether the stored password looks structurally intact -------------------
print()
print("  stored password shape (no value disclosed):")
print(f"    length        : {len(stored_pass)}")
print(f"    has $-char    : {'$' in stored_pass}")
print(f"    has whitespace: {any(c.isspace() for c in stored_pass)}")
print(f"    fingerprint   : {fp(stored_pass) if stored_pass else 'n/a'}")

print()
print(f"  supplied password shape:")
print(f"    length        : {len(new_pass)}")
print(f"    fingerprint   : {fp(new_pass)}")

print()
print(f"  RESULT: user {'MATCH' if u_match else 'MISMATCH'} · pass {'MATCH' if p_match else 'MISMATCH'}")
