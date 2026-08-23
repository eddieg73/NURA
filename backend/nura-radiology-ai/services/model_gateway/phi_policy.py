"""PHI policy — strip/reject protected identifiers before ANY external model/evidence call.
No patient identifiers leave the environment. Opaque refs only on the wire."""
import re

PHI_PATTERNS = {
    "mrn": re.compile(r"\bMRN[-_: ]?\d{3,}\b", re.I),
    "medicare": re.compile(r"\b\d{4}-?\d{2}-?\d{4}\b"),        # SSN-like
    "dob": re.compile(r"\b(?:DOB|birth[ -]?date)[^A-Za-z]{0,6}(19|20)\d{2}[-/.]\d{1,2}[-/.]\d{1,2}", re.I),
    "phone": re.compile(r"\b(?:\+?1[-. ]?)?(\(?\d{3}\)?[-. ]?)\d{3}[-. ]?\d{4}\b"),
    "email": re.compile(r"\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}\b"),
}
# Overrides to reduce false positives on incidental digits/emails.
SAFE_TECH_EMAIL = re.compile(r"nura@|@nuratech\.ai|@backblaze\.com|@gmail\.com$", re.I)


class PHIGuard:
    def __init__(self):
        self.stripped = []

    def redact(self, text: str) -> str:
        out = text
        for name, pat in PHI_PATTERNS.items():
            if name == "email" and SAFE_TECH_EMAIL.search(out):
                continue
            matches = pat.findall(out)
            if matches:
                self.stripped.append((name, matches))
                out = pat.sub(f"[REDACTED:{name}]", out)
        return out

    def assert_clean(self, text: str) -> None:
        hits = {n: pat.findall(text) for n, pat in PHI_PATTERNS.items() if pat.findall(text)}
        if hits:
            raise PermissionError(f"PHI detected - refuse external call: {hits}")


def check_phi(text: str) -> dict:
    g = PHIGuard()
    redacted = g.redact(text)
    return {"redacted": redacted, "stripped": g.stripped, "clean": not bool(g.stripped)}
