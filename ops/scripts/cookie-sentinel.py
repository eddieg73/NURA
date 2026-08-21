#!/usr/bin/env python3
"""COOKIE-DROP SENTINEL — silent until the founder drops a cookie file.

Watches /opt/data/cookies/. When a recognized cookie file appears:
  - writes the yt-dlp config so YouTube extraction auto-works
  - flags reddit-cookies for the rdt-cli lane
  - prints a ONE-TIME arming report (delivered to origin)
Silent (empty stdout) on every clean tick.
"""
import os, json

DROP = "/opt/data/cookies"
STATE = "/opt/data/profiles/nura/cron/output/cookie-sentinel.json"
YTDLP_CONFIG = "/opt/data/profiles/nura/home/.config/yt-dlp/config"

RECOGNIZED = {
    "cookies.txt": "YouTube (yt-dlp) + transcripts",
    "youtube-cookies.txt": "YouTube (yt-dlp) + transcripts",
    "reddit-cookies.txt": "Reddit (rdt-cli)",
    "linkedin-cookies.txt": "LinkedIn (manual-lane)",
}


def load_state():
    try:
        with open(STATE) as f:
            return json.load(f)
    except Exception:
        return {"armed": {}}


def main():
    st = load_state()
    os.makedirs(DROP, exist_ok=True)
    present = {}
    for fname in RECOGNIZED:
        path = os.path.join(DROP, fname)
        if os.path.isfile(path) and os.path.getsize(path) > 100:
            present[fname] = path

    # arm yt-dlp when a youtube cookie exists
    yt_cookie = present.get("cookies.txt") or present.get("youtube-cookies.txt")
    if yt_cookie:
        os.makedirs(os.path.dirname(YTDLP_CONFIG), exist_ok=True)
        with open(YTDLP_CONFIG, "w") as f:
            f.write(f"--cookies {yt_cookie}\n")

    new_armed = {k: v for k, v in present.items() if k not in st.get("armed", {})}
    if not new_armed:
        return  # silent tick

    st["armed"] = present
    os.makedirs(os.path.dirname(STATE), exist_ok=True)
    with open(STATE, "w") as f:
        json.dump(st, f)

    lines = ["🔓 COOKIE-DROP DETECTED — lanes armed:"]
    for k in sorted(new_armed):
        lines.append(f"· {RECOGNIZED[k]} ({k})")
    print("\n".join(lines))


if __name__ == "__main__":
    main()
