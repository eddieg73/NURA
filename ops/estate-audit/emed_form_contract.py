#!/usr/bin/env python3
"""
Extract the REAL login-form contract from the live eMedical page.

Two independent defects found:
  1. playwright + browser binaries are ABSENT -> the script cannot launch a browser at all.
  2. the script's LOGIN selectors do not all match the live page (#username = 0 matches).

Fixing only (1) would leave a script that launches a browser and then fails on a selector. Get the
real contract first, from the live HTML, so both can be corrected in one pass.
"""
import re
import urllib.request

URL = "https://service.emedpractice.com/"
UA = ("Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
      "(KHTML, like Gecko) Chrome/124.0 Safari/537.36")

req = urllib.request.Request(URL, headers={"User-Agent": UA})
with urllib.request.urlopen(req, timeout=30) as r:
    html = r.read().decode("utf-8", "ignore")

print("=" * 88)
print("ALL <input> ELEMENTS ON THE LIVE LOGIN PAGE")
print("=" * 88)
for m in re.finditer(r"<input\b[^>]*>", html, re.I):
    tag = m.group(0)
    def attr(name):
        a = re.search(rf'{name}\s*=\s*["\']([^"\']*)["\']', tag, re.I)
        return a.group(1) if a else ""
    line = (f"    type={attr('type'):<12} id={attr('id'):<22} "
            f"name={attr('name'):<22} cls={attr('class')[:26]:<28}")
    ph = attr("placeholder")
    if ph:
        line += f" ph={ph[:28]}"
    print(line)

print("\n" + "=" * 88)
print("ALL <button> / submit CONTROLS")
print("=" * 88)
for m in re.finditer(r"<button\b[^>]*>.*?</button>", html, re.I | re.S):
    tag = m.group(0)
    one = re.sub(r"\s+", " ", tag)[:170]
    print(f"    {one}")
for m in re.finditer(r'<input\b[^>]*type\s*=\s*["\']submit["\'][^>]*>', html, re.I):
    print(f"    {re.sub(chr(92)+'s+', ' ', m.group(0))[:170]}")

print("\n" + "=" * 88)
print("FORM ACTION TARGETS")
print("=" * 88)
for m in re.finditer(r"<form\b[^>]*>", html, re.I):
    a = re.search(r'action\s*=\s*["\']([^"\']*)["\']', m.group(0), re.I)
    i = re.search(r'id\s*=\s*["\']([^"\']*)["\']', m.group(0), re.I)
    print(f"    action={a.group(1) if a else '(none)'}  id={i.group(1) if i else '(none)'}")

print("\n" + "=" * 88)
print("SCRIPT-CRITICAL SELECTOR CHECK")
print("=" * 88)
checks = {
    "#username": r'id\s*=\s*["\']username["\']',
    "#password": r'id\s*=\s*["\']password["\']',
    "#SigninBtn": r'id\s*=\s*["\']SigninBtn["\']',
    "#btnLogin": r'id\s*=\s*["\']btnLogin["\']',
    "#login": r'id\s*=\s*["\']login["\']',
    "name=username": r'name\s*=\s*["\']username["\']',
    "name=password": r'name\s*=\s*["\']password["\']',
    "__VIEWSTATE": r"__VIEWSTATE",
    "__EVENTVALIDATION": r"__EVENTVALIDATION",
}
for label, pat in checks.items():
    n = len(re.findall(pat, html, re.I))
    print(f"    {label:<22} {n} {'OK' if n else '** MISSING **'}")

print("\n" + "=" * 88)
print("CANDIDATE USERNAME SELECTORS (what the script SHOULD target)")
print("=" * 88)
for m in re.finditer(r"<input\b[^>]*>", html, re.I):
    tag = m.group(0)
    if re.search(r'type\s*=\s*["\'](text|email)["\']', tag, re.I):
        i = re.search(r'id\s*=\s*["\']([^"\']*)["\']', tag, re.I)
        n = re.search(r'name\s*=\s*["\']([^"\']*)["\']', tag, re.I)
        print(f"    id={i.group(1) if i else '-':<24} name={n.group(1) if n else '-'}")
print("\n  -> the job must use the id/name above, NOT the hardcoded #username")
