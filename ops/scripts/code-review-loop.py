#!/usr/bin/env python3
"""CODE-REVIEW GATE — deterministic · silent-when-clean · real analyzer signals.

Efficiency doctrine:
  - No new commits since last review → tick costs one `git rev-parse` and exits SILENT.
  - Only on a moving HEAD: fetch → flutter analyze + flutter test → secret-scan the diff.
  - Score ≥ gate → SILENT (no message noise). Score < gate → compact actionable block.
"""
import subprocess, os, json, datetime, re

REPO = "/opt/data/nura_medical"
APP = f"{REPO}/apps/nura_medical"
STATE = "/opt/data/profiles/nura/cron/output/review-loop.json"
FLUTTER = "/opt/data/flutter-sdk/bin/flutter"
GATE = 4  # the founder's gate: nothing under 4/5 goes live

SECRET_PATTERNS = [
    r"sk-[A-Za-z0-9]{20,}",
    r"ghp_[A-Za-z0-9]{36}",
    r"AKIA[0-9A-Z]{16}",
    r"AIza[0-9A-Za-z_-]{30,}",
    r"-----BEGIN (RSA |EC |OPENSSH )?PRIVATE KEY-----",
    r"password\s*=\s*[\"'][^\"']{8,}",
    r"token\s*=\s*[\"'][A-Za-z0-9._-]{16,}",
]


def sh(cmd, timeout=240):
    try:
        r = subprocess.run(cmd, shell=True, capture_output=True, text=True, timeout=timeout)
        return (r.stdout or "") + (r.stderr or "")
    except subprocess.TimeoutExpired:
        return "TIMEOUT"


def load_state():
    try:
        with open(STATE) as f:
            return json.load(f)
    except Exception:
        return {}


def main():
    head = sh(f"cd {REPO} && git rev-parse HEAD 2>/dev/null").strip()
    st = load_state()
    if st.get("reviewed_commit") == head:
        return  # clean tick — silent by design

    sh(f"cd {REPO} && git fetch --quiet origin 2>/dev/null")
    new_head = sh(f"cd {REPO} && git rev-parse HEAD 2>/dev/null").strip() or head

    analyze = sh(f"cd {APP} && {FLUTTER} analyze 2>&1 | tail -25")
    errors = len(re.findall(r"\berror\s*\u2022", analyze))
    warnings = len(re.findall(r"\bwarning\s*\u2022", analyze))

    test_out = sh(f"cd {APP} && {FLUTTER} test 2>&1 | tail -6")
    tests_pass = "All tests passed!" in test_out

    diff = sh(
        f"cd {REPO} && git diff {st.get('reviewed_commit', 'HEAD~1')}..{new_head} "
        f"-- . ':!*.lock' ':!pubspec.lock' 2>/dev/null | head -600"
    )
    secrets = sum(1 for p in SECRET_PATTERNS for _ in re.finditer(p, diff, re.I))

    score = 5 - min(3, errors) - min(1, warnings // 10) - min(3, secrets * 2)
    if not tests_pass and test_out.strip() not in ("", "TIMEOUT"):
        score -= 2
    score = max(1, min(5, score))

    state = {
        "date": datetime.datetime.now().isoformat(),
        "score": score,
        "errors": errors,
        "warnings": warnings,
        "secrets": secrets,
        "tests_pass": tests_pass,
        "reviewed_commit": new_head,
        "gate": GATE,
    }
    os.makedirs(os.path.dirname(STATE), exist_ok=True)
    with open(STATE, "w") as f:
        json.dump(state, f)

    if score >= GATE:
        return  # clean pass — silent by design

    print(
        f"⛔ CODE-REVIEW GATE {score}/5 (need {GATE}) — "
        f"errors:{errors} warnings:{warnings} secrets:{secrets} tests:{'PASS' if tests_pass else 'FAIL'} "
        f"@{new_head[:8]}"
    )
    if errors:
        print(analyze[:900])
    elif warnings:
        print(analyze[:600])
    if secrets:
        print("· secret-pattern hits in diff — remediate before merge:")
        for p in SECRET_PATTERNS:
            if re.search(p, diff, re.I):
                print(f"  {p}")
    if not tests_pass:
        print(test_out[:400])


if __name__ == "__main__":
    main()
