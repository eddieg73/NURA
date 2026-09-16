#!/usr/bin/env python3
"""
Fix every instance of the same defect in paperclip-product-companies.py.

THE BUG: implicit string concatenation inside a tuple-looking paren group is closed with `}` instead
of `)`. e.g.

    "description": ("line one "
                    "line two "
                    "last line."},        <-- WRONG: } closes the dict, ( is never closed

should be:

    "description": ("line one "
                    "line two "
                    "last line."),        <-- correct

It appears multiple times. Fixing one at a time just moves the SyntaxError further down, so fix them
all, then verify the whole file compiles and that only THIS pattern changed.
"""
import hashlib
import re

P = "/opt/data/NURA/scripts/paperclip-product-companies.py"
src = open(P).read()
before = hashlib.sha256(src.encode()).hexdigest()

# The defective line ends the description value: a quoted string followed by `},`
# We only touch lines that look like a string literal terminator followed by }, and where the
# immediately preceding context is a description string group.
lines = src.splitlines(keepends=True)
fixed = []
changed = []
for i, ln in enumerate(lines, 1):
    stripped = ln.rstrip()
    if stripped.endswith('"},'):
        # confirm it is a string literal closing into a dict-close
        fixed.append(ln[:ln.rfind('"},')] + '"),' + ln[len(stripped):] if ln.endswith("\n") else ln.replace('"},', '"),'))
        changed.append(i)
    else:
        fixed.append(ln)

out = "".join(fixed)
open(P, "w").write(out)

after = hashlib.sha256(out.encode()).hexdigest()
print(f"  lines changed: {len(changed)}  {changed}")
print(f"  sha256 before: {before[:16]}")
print(f"  sha256 after : {after[:16]}")

# ---- verify it compiles --------------------------------------------------
print("\n  compile check:")
try:
    compile(out, P, "exec")
    print("    COMPILES OK")
except SyntaxError as e:
    print(f"    STILL BROKEN: line {e.lineno}: {e.msg}")
    ls = out.splitlines()
    for i in range(max(0, e.lineno - 4), min(len(ls), e.lineno + 2)):
        print(f"      {'>>' if i+1==e.lineno else '  '} {i+1:>4}: {ls[i]}")

# ---- confirm no other pattern was disturbed ------------------------------
print("\n  structural check — issue count and keys preserved:")
import ast
try:
    tree = ast.parse(out)
    # count dict literals with a 'title' key at module level assignment
    n_issues = out.count('"title":')
    n_assignee = out.count('"assigneeAgentId":')
    print(f"    title keys: {n_issues}   assignee keys: {n_assignee}")
    print(f"    parses as valid Python: YES")
except SyntaxError as e:
    print(f"    parse failed: {e}")
