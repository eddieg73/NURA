#!/usr/bin/env python3
"""The hermes-image watchdog: silent unless a Docker Hub tag newer than v2026.8.3 publishes."""
import json, urllib.request

LATEST_KNOWN = "v2026.8.3"

def get_tags():
    tags = []
    for page in (1, 2):
        url = f"https://hub.docker.com/v2/repositories/nousresearch/hermes-agent/tags?page_size=15&page={page}&ordering=last_updated"
        try:
            with urllib.request.urlopen(url, timeout=25) as r:
                data = json.loads(r.read())
            tags += [t["name"] for t in data.get("results", [])]
        except Exception:
            return None
    return tags

def newer_than(known: str, tags: list) -> list:
    """Version-compare the vYYYY.M.D tags."""
    def key(s):
        try:
            parts = s.replace("v", "").split(".")
            return tuple(int(p) for p in parts[:3])
        except ValueError:
            return (0, 0, 0)
    return [t for t in tags if t not in ("latest", "main") and key(t) > key(known)]

if __name__ == "__main__":
    tags = get_tags()
    if tags is None:
        print("⚠️ The hermes-image watchdog: the Hub's the unreachable (the check failed).")  # the alert's the loud when the probe itself breaks
        raise SystemExit(0)
    fresh = newer_than(LATEST_KNOWN, tags)
    if fresh:
        print(f"🚀 THE NEW HERMES IMAGE PUBLISHED: {', '.join(sorted(fresh))} — the upgrade's the unblocked. The one-paste block's the ready (the vault's the Hermes-Changelog-Pass).")
    # else: silent — nothing to report
